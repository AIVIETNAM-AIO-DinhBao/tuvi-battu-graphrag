"""Lazy local LLM JSON client for Kaggle/offline W3 ingestion."""

from __future__ import annotations

import json
import re
from typing import Any


DEFAULT_LOCAL_LLM_MODEL = "Qwen/Qwen2.5-7B-Instruct"
DEFAULT_LOCAL_LLM_MAX_NEW_TOKENS = 1024


def extract_json_candidate(text: str) -> str:
    stripped = text.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, flags=re.S | re.I)
    if fenced:
        stripped = fenced.group(1).strip()

    if stripped.startswith("{") or stripped.startswith("["):
        return stripped

    start_positions = [pos for pos in (stripped.find("{"), stripped.find("[")) if pos >= 0]
    if not start_positions:
        return stripped
    start = min(start_positions)
    open_char = stripped[start]
    close_char = "}" if open_char == "{" else "]"
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(stripped)):
        char = stripped[index]
        if escape:
            escape = False
            continue
        if char == "\\":
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return stripped[start : index + 1]
    return stripped[start:]


def parse_json_payload(text: str) -> Any:
    return json.loads(extract_json_candidate(text))


class LocalQwenJsonClient:
    """Transformers-backed Qwen client that returns parsed JSON payloads."""

    def __init__(
        self,
        model_name: str = DEFAULT_LOCAL_LLM_MODEL,
        *,
        device: str | None = None,
        quantization: str = "4bit",
        max_new_tokens: int = DEFAULT_LOCAL_LLM_MAX_NEW_TOKENS,
        temperature: float = 0.0,
        top_p: float = 0.9,
        max_json_retries: int = 1,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.quantization = quantization
        self.max_new_tokens = max(1, int(max_new_tokens))
        self.temperature = max(0.0, float(temperature))
        self.top_p = float(top_p)
        self.max_json_retries = max(0, int(max_json_retries))
        self._tokenizer: Any | None = None
        self._model: Any | None = None
        self.call_count = 0
        self.json_error_count = 0

    def get_usage_summary(self) -> dict[str, Any]:
        return {
            "llm_backend": "local",
            "local_llm_call_count": self.call_count,
            "local_llm_device": self.device,
            "local_llm_json_error_count": self.json_error_count,
            "local_llm_max_new_tokens": self.max_new_tokens,
            "local_llm_model": self.model_name,
            "local_llm_quantization": self.quantization,
            "local_llm_temperature": self.temperature,
        }

    def _ensure_model(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        try:
            import torch  # type: ignore[import-not-found]
            from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "Local Qwen backend requires torch and transformers. "
                "Install backend/requirements-kaggle.txt in the Kaggle notebook."
            ) from exc

        model_kwargs: dict[str, Any] = {"device_map": {"": self.device} if self.device else "auto"}
        if self.quantization == "4bit":
            try:
                from transformers import BitsAndBytesConfig  # type: ignore[import-not-found]
            except ImportError as exc:
                raise RuntimeError("4-bit Qwen loading requires bitsandbytes.") from exc
            model_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
        elif self.quantization == "8bit":
            try:
                from transformers import BitsAndBytesConfig  # type: ignore[import-not-found]
            except ImportError as exc:
                raise RuntimeError("8-bit Qwen loading requires bitsandbytes.") from exc
            model_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
        elif self.quantization == "none":
            model_kwargs["torch_dtype"] = "auto"
        else:
            raise ValueError("--local-llm-quantization must be 4bit, 8bit, or none.")

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            **model_kwargs,
        )
        self._model.eval()

    def _format_prompt(self, prompt: str) -> str:
        self._ensure_model()
        messages = [
            {
                "role": "system",
                "content": "Return strict JSON only. Do not include explanations outside JSON.",
            },
            {"role": "user", "content": prompt},
        ]
        if hasattr(self._tokenizer, "apply_chat_template"):
            return self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        return prompt

    def generate_text(self, prompt: str) -> str:
        self._ensure_model()
        import torch  # type: ignore[import-not-found]

        formatted = self._format_prompt(prompt)
        inputs = self._tokenizer(formatted, return_tensors="pt")
        try:
            device = next(self._model.parameters()).device
            inputs = {key: value.to(device) for key, value in inputs.items()}
        except Exception:
            pass

        generate_kwargs: dict[str, Any] = {
            "max_new_tokens": self.max_new_tokens,
            "pad_token_id": self._tokenizer.eos_token_id,
        }
        if self.temperature > 0:
            generate_kwargs.update({"do_sample": True, "temperature": self.temperature, "top_p": self.top_p})
        else:
            generate_kwargs["do_sample"] = False

        self.call_count += 1
        with torch.no_grad():
            output = self._model.generate(**inputs, **generate_kwargs)
        prompt_tokens = int(inputs["input_ids"].shape[-1])
        generated = output[0][prompt_tokens:]
        return self._tokenizer.decode(generated, skip_special_tokens=True)

    def generate_json(self, prompt: str) -> Any:
        current_prompt = prompt
        last_error: Exception | None = None
        for attempt in range(self.max_json_retries + 1):
            text = self.generate_text(current_prompt)
            try:
                return parse_json_payload(text)
            except Exception as exc:  # noqa: BLE001 - retry with a repair prompt.
                self.json_error_count += 1
                last_error = exc
                current_prompt = (
                    f"{prompt}\n\nThe previous response was invalid JSON: {exc}. "
                    "Return only one valid JSON object matching the requested schema."
                )
                if attempt >= self.max_json_retries:
                    break
        raise ValueError(f"Local Qwen response was not valid JSON: {last_error}")
