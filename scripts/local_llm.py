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


def repair_json_candidate(candidate: str) -> str:
    repaired = candidate.strip()
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    quote_count = 0
    escape = False
    for char in repaired:
        if escape:
            escape = False
            continue
        if char == "\\":
            escape = True
            continue
        if char == '"':
            quote_count += 1
    if quote_count % 2:
        repaired += '"'
    for open_char, close_char in (("{", "}"), ("[", "]")):
        delta = repaired.count(open_char) - repaired.count(close_char)
        if delta > 0:
            repaired += close_char * delta
    return repaired


def parse_partial_entities_payload(candidate: str) -> dict[str, Any] | None:
    match = re.search(r'"entities"\s*:\s*\[', candidate)
    if not match:
        return None
    index = match.end()
    entities: list[Any] = []
    while index < len(candidate):
        while index < len(candidate) and candidate[index] not in "{]":
            index += 1
        if index >= len(candidate) or candidate[index] == "]":
            break
        start = index
        depth = 0
        in_string = False
        escape = False
        while index < len(candidate):
            char = candidate[index]
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = not in_string
            elif not in_string:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        index += 1
                        item_text = repair_json_candidate(candidate[start:index])
                        try:
                            item = json.loads(item_text)
                        except json.JSONDecodeError:
                            item = None
                        if isinstance(item, dict):
                            entities.append(item)
                        break
            index += 1
        else:
            break
    if entities:
        return {"entities": entities}
    return None


def parse_json_payload(text: str) -> Any:
    candidate = extract_json_candidate(text)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    repaired = repair_json_candidate(candidate)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        partial = parse_partial_entities_payload(candidate)
        if partial is not None:
            return partial
        raise


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

    def warmup(self) -> None:
        self._ensure_model()

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

        if self.device in {None, "", "auto", "auto-cuda"}:
            device_map: Any = "auto"
        else:
            device_map = {"": self.device}
        model_kwargs: dict[str, Any] = {
            "device_map": device_map,
            "low_cpu_mem_usage": True,
        }
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
            model_kwargs["dtype"] = torch.float16 if torch.cuda.is_available() else "auto"
        else:
            raise ValueError("--local-llm-quantization must be 4bit, 8bit, or none.")

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        try:
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                **model_kwargs,
            )
        except Exception as exc:
            if self.quantization == "none":
                raise RuntimeError(
                    f"Failed to load non-quantized local LLM {self.model_name}. "
                    "Use a Kaggle GPU with enough memory, or reduce the model size if quality requirements allow it."
                ) from exc
            raise
        if self.device == "auto-cuda":
            device_values = {
                str(device).lower()
                for device in getattr(self._model, "hf_device_map", {}).values()
            }
            offloaded = [device for device in sorted(device_values) if device == "cpu" or device == "disk"]
            if offloaded:
                raise RuntimeError(
                    f"Non-quantized local LLM {self.model_name} was offloaded to {offloaded}. "
                    "Use a Kaggle runtime with enough GPU memory for full-model inference."
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
                    "The previous response was invalid JSON. Regenerate the answer as compact minified JSON only.\n"
                    f"JSON error: {exc}\n"
                    "Use exactly {\"entities\":[{\"entity_type\":\"...\",\"surface_text\":\"...\","
                    "\"evidence_text\":\"...\",\"confidence\":0.0}]} or {\"entities\":[]}.\n"
                    "No markdown. No explanation. At most 20 entities.\n\n"
                    f"Original task:\n{prompt}"
                )
                if attempt >= self.max_json_retries:
                    break
        raise ValueError(f"Local Qwen response was not valid JSON: {last_error}")
