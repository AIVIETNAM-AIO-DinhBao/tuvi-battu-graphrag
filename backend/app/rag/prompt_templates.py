from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.rag.config import ExperimentConfig
from app.rag.state import RAGState


@dataclass(frozen=True)
class PromptTemplate:
    template_id: str
    description: str
    builder: Callable[[RAGState, ExperimentConfig], str]


def prompt_inputs(state: RAGState) -> tuple[str, str]:
    query = state.get("rewritten_query") or state.get("normalized_query") or state.get("query") or ""
    final_context = state.get("final_context") or ""
    return str(query), str(final_context)


def metadata_block(query: str, final_context: str, config: ExperimentConfig) -> str:
    return (
        f"prompt_template_id: {config.prompt_template_id}\n"
        f"chunk_strategy_id: {config.chunk_strategy_id}\n"
        f"generation_model: {config.generation_model}\n"
        f"QUESTION: {query}\n\n"
        f"CONTEXT:\n{final_context}\n"
    )


def build_tuvi_generation_v1(state: RAGState, config: ExperimentConfig) -> str:
    query, final_context = prompt_inputs(state)
    return (
        "Bạn là trợ lý luận giải Tử Vi. Chỉ trả lời trong domain TUVI.\n"
        "Dựa vào CONTEXT và lá số được cung cấp; không bịa nguồn, không suy diễn ngoài dữ liệu.\n"
        "Nếu CONTEXT không đủ, hãy nói rõ chưa đủ dữ liệu trong nguồn hiện có.\n"
        "Khi dùng thông tin từ nguồn sách, ghi citation dạng [S1], [S2]. "
        "Khi dùng dữ kiện lá số trong khối [CHART], ghi citation [CHART]. "
        "Không viết marker [CHART_FACTS]; chỉ dùng [CHART] cho dữ kiện lá số. "
        "Không tự tạo marker [S1] nếu CONTEXT không có block [S1].\n\n"
        f"{metadata_block(query, final_context, config)}\n\n"
        "Trả lời tiếng Việt, ngắn gọn, có citation nếu có nguồn."
    )


def build_tuvi_generation_grounded_v2(state: RAGState, config: ExperimentConfig) -> str:
    query, final_context = prompt_inputs(state)
    return (
        "Bạn là trợ lý luận giải Tử Vi chuyên bám nguồn. Chỉ trả lời trong domain TUVI.\n"
        "NGUYÊN TẮC BẮT BUỘC:\n"
        "1. Dữ kiện lá số chỉ lấy từ khối [CHART] và khi dùng phải citation [CHART].\n"
        "2. Luận giải/quy tắc chỉ lấy từ các khối nguồn [S1], [S2], ... có trong CONTEXT.\n"
        "3. Không tự thêm sao, cung, tam hợp, xung chiếu hoặc trạng thái miếu/hãm nếu CONTEXT không nêu.\n"
        "4. Không tạo citation mới; không viết [CHART_FACTS] hoặc bất kỳ marker lỗi nào kết hợp CHART với FACTS.\n"
        "5. Nếu câu hỏi là factual về lá số, ưu tiên trả lời trực tiếp từ [CHART], không ép dùng nguồn sách.\n"
        "6. Nếu câu hỏi cần luận giải nhưng corpus thiếu quy tắc cho đúng sao/cung/tổ hợp được hỏi, nói rõ chưa đủ dữ liệu trong nguồn hiện có.\n"
        "7. Với câu hỏi tam hợp/liên hệ cung, chỉ xét các cung được [CHART] hoặc câu hỏi khóa tường minh.\n\n"
        f"{metadata_block(query, final_context, config)}\n\n"
        "Hãy trả lời tiếng Việt, súc tích, nêu rõ phần nào chắc từ lá số và phần nào là luận giải từ nguồn."
    )


def build_tuvi_generation_structured_v3(state: RAGState, config: ExperimentConfig) -> str:
    query, final_context = prompt_inputs(state)
    return (
        "Bạn là trợ lý Tử Vi. Nhiệm vụ là tạo câu trả lời có cấu trúc, bám sát CONTEXT.\n"
        "Chỉ dùng dữ kiện trong [CHART] và các nguồn [S1], [S2], ... có sẵn. "
        "Không dùng [CHART_FACTS], không bịa citation, không suy diễn ngoài dữ liệu.\n"
        "Nếu thiếu bằng chứng cho một kết luận, hãy ghi ở mục giới hạn dữ liệu thay vì đoán.\n\n"
        f"{metadata_block(query, final_context, config)}\n\n"
        "Định dạng trả lời:\n"
        "1. Dữ kiện lá số: tóm tắt đúng phần liên quan, citation [CHART] nếu có.\n"
        "2. Luận giải từ nguồn: chỉ nêu ý được hỗ trợ bởi [S1], [S2], ... và gắn citation.\n"
        "3. Giới hạn dữ liệu: nêu rõ nếu nguồn hiện có chưa đủ để kết luận.\n"
        "Nếu câu hỏi chỉ cần dữ kiện factual, có thể bỏ mục 2 nhưng vẫn giữ câu trả lời ngắn gọn."
    )


PROMPT_TEMPLATES: dict[str, PromptTemplate] = {
    "tuvi_generation_v1": PromptTemplate(
        template_id="tuvi_generation_v1",
        description="Baseline concise Tu Vi generation prompt used before W7-ABL-01.",
        builder=build_tuvi_generation_v1,
    ),
    "tuvi_generation_grounded_v2": PromptTemplate(
        template_id="tuvi_generation_grounded_v2",
        description="Stricter grounding/citation prompt for W7 generation ablation.",
        builder=build_tuvi_generation_grounded_v2,
    ),
    "tuvi_generation_structured_v3": PromptTemplate(
        template_id="tuvi_generation_structured_v3",
        description="Structured answer prompt with explicit data-limit section.",
        builder=build_tuvi_generation_structured_v3,
    ),
}


def build_prompt_from_template(state: RAGState, config: ExperimentConfig) -> str:
    template = PROMPT_TEMPLATES.get(config.prompt_template_id)
    if template is None:
        available = ", ".join(sorted(PROMPT_TEMPLATES))
        raise ValueError(f"Unknown prompt_template_id '{config.prompt_template_id}'. Available templates: {available}.")
    return template.builder(state, config)


__all__ = [
    "PROMPT_TEMPLATES",
    "PromptTemplate",
    "build_prompt_from_template",
]