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
        "Bạn là trợ lý luận giải Tử Vi chuyên bám nguồn. Nhiệm vụ là tạo câu trả lời có cấu trúc, "
        "cá nhân hóa theo lá số, không chỉ liệt kê dữ kiện. Chỉ trả lời trong domain TUVI.\n"
        "NGUYÊN TẮC BẮT BUỘC:\n"
        "1. Dữ kiện lá số chỉ lấy từ [CHART]; khi dùng dữ kiện cung/sao/trạng thái phải citation [CHART].\n"
        "2. Quy tắc, ý nghĩa và đánh giá tốt/xấu chỉ lấy từ các nguồn [S1], [S2], ... có trong CONTEXT.\n"
        "3. Không tự thêm sao, cung, tam hợp, xung chiếu, miếu/hãm/đắc/vượng hoặc Tuần/Triệt nếu CONTEXT không nêu.\n"
        "4. Không dùng [CHART_FACTS], không bịa citation, không tạo marker ngoài [CHART] và [Sx] có sẵn.\n"
        "5. Một citation chỉ được gắn với mệnh đề mà nguồn trực tiếp hỗ trợ; không dùng nguồn nói về sao/cung khác để kết luận rộng.\n"
        "6. Nếu nguồn chỉ hỗ trợ ý nghĩa chung của cung, hãy ghi rõ đó là ý nghĩa chung, không biến thành kết luận cá nhân mạnh.\n"
        "7. Nếu thiếu bằng chứng cho một sao, phụ tinh hoặc tổ hợp trong lá số, có thể nêu sao đó xuất hiện từ [CHART] "
        "nhưng phải nói nguồn hiện có chưa đủ để luận riêng sao đó.\n"
        "8. Phân biệt sao gốc và lưu tinh: sao có tiền tố L. hoặc Lưu chỉ nên luận như yếu tố lưu/hạn khi câu hỏi hỏi về hạn/vận/năm.\n"
        "9. Không phán tuyệt đối; mọi nhận định là khuynh hướng và cần xét toàn lá số.\n\n"
        f"{metadata_block(query, final_context, config)}\n\n"
        "Định dạng trả lời:\n"
        "1. Dữ kiện chính từ lá số: tóm tắt đúng phần liên quan, citation [CHART].\n"
        "2. Luận giải tổng hợp từ nguồn: ưu tiên chính tinh/tổ hợp chính trước phụ tinh; nêu rõ citation [Sx] cho từng ý.\n"
        "3. Thuận lợi và điểm cần lưu ý: cân bằng cát tinh với sát/bại tinh hoặc yếu tố ràng buộc nếu có nguồn.\n"
        "4. Kết luận ngắn và giới hạn dữ liệu: kết luận hữu ích, đồng thời nêu phần nào chưa đủ nguồn để luận sâu.\n"
        "Nếu câu hỏi chỉ cần dữ kiện factual, có thể trả lời ngắn gọn và bỏ các mục không cần thiết."
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