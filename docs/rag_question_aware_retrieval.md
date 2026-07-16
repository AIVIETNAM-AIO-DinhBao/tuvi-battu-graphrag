# Question-aware and Chart-aware Retrieval Design / Thiết kế retrieval theo câu hỏi và lá số

**Status:** W6-RAG-01..07 implemented and test-verified  
**Last updated:** 2026-07-14  
**Related tasks:** W6-RAG-01, W6-RAG-02, W6-RAG-03, W6-RAG-04, W6-RAG-05, W6-RAG-06, W6-RAG-07, W6-DOC-01, W6-ABL-02, W7-OBS-01, W7-OBS-02

This document explains the current question-aware and chart-aware retrieval design after W6-RAG-07. It is intended to let a teammate understand the roadmap, scope, validation plan, and production caveats without reading the whole RAG codebase.

Tài liệu này mô tả thiết kế retrieval hiện tại sau W6-RAG-07: hệ thống không còn chỉ retrieve generic theo query text, mà dùng `question_family`, `question_complexity`, `retrieval_plan`, chart facts, evidence roles, graph modes và diagnostics để chọn context có chủ đích hơn.

---

## 1. Executive summary / Tóm tắt

The RAG pipeline now follows this high-level model:

```text
query
  -> normalize_query
  -> query_rewrite optional
  -> runtime entity extraction
  -> query planner
  -> chart fact extraction
  -> role-aware graph retrieval
  -> planner-gated dense retrieval
  -> role-aware sparse retrieval
  -> fusion / rerank / document grading
  -> role-aware context assembly
  -> generation
  -> citation mapping
  -> retrieval diagnostics
```

Key ideas:

- **Question-aware:** query is mapped to `question_family` and `question_complexity` before retrieval.
- **Chart-aware:** chart facts are extracted from `chart_data` and placed before corpus chunks in context.
- **Role-aware:** retrieval and context assembly track evidence roles such as `house_scope`, `star_definition`, `modifier_effect`, `relation_rule`, and `combination_pattern`.
- **Graph strictness:** graph retrieval supports `entity_any`, `entity_all`, and `min_hit_count`, with controlled fallback.
- **Dense safety:** dense retrieval is implemented but planner-gated. The default production config still keeps dense off until ablation and p95 latency evidence are available.

---

## 2. Why this design was needed / Vì sao cần thiết kế này

Before W6-RAG-01..07, the retrieval path had several limitations:

| Area | Previous limitation | Current mitigation |
|---|---|---|
| Graph retrieval | Generic entity lookup could return broad `MENTIONS` chunks without knowing what role the evidence should play. | Planner selects graph mode and evidence roles; graph retrieval can be role-aware and strict. |
| Sparse retrieval | Fulltext/entity-text search did not distinguish definition, relation, modifier, or combination evidence. | Role queries annotate candidates with `evidence_role`, `retrieval_intent`, and `role_query`. |
| Dense retrieval | Dense was disabled in production default because local BGE-M3 cold start could exceed chat timeout. | W6-RAG-07 adds planner-gated dense, query embedding cache, and ablation config. |
| Fusion | Generic RRF/fusion could rank high-scoring chunks while missing a required role. | W6-RAG-06 context assembly covers required roles before filling remaining budget globally. |
| Reranker | Current reranker is heuristic/lexical, not a learned cross-encoder. | Kept configurable; final choice should be based on W6/W7 ablation. |
| Context assembly | Top-ranked chunks only could miss chart facts or role diversity. | Chart summary and chart facts are prioritized before role-labeled corpus chunks. |

Some limitations remain production decisions rather than implementation blockers; see Section 12.

---

## 3. Target reasoning model / Mô hình suy luận mục tiêu

| Complexity | Meaning | Grounding model | Retrieval behavior |
|---|---|---|---|
| `Direct` | Câu hỏi fact trực tiếp từ lá số. | Chart facts are primary. | Corpus retrieval can be disabled; Direct chart QA should not run dense. |
| `One-hop` | Cần một bước nối từ chart fact sang corpus evidence. | Chart fact + one or more evidence roles. | Graph/sparse role-aware retrieval; dense can run only if config and planner gate allow it. |
| `Two-hop` | Cần nhiều quan hệ/vai trò evidence và synthesis. | Chart graph expansion + multiple roles + synthesis. | Strict graph mode, role-aware retrieval/context, planner-gated dense. |

Examples:

| Example question | Expected family/complexity | Grounding |
|---|---|---|
| “Cung Mệnh nằm ở đâu?” | `core_identity` / `Direct` | Chart facts only. |
| “Cung Mệnh có Thiên Mã thì luận thế nào?” | `menh_house_interpretation` / `One-hop` | Chart fact: Mệnh has Thiên Mã; corpus: star definition/modifier evidence. |
| “Mệnh tam hợp và xung chiếu ảnh hưởng sự nghiệp thế nào?” | `menh_tam_hop` or `menh_xung_chieu` / `Two-hop` | Chart relations + relation rules + combination patterns + synthesis. |

---

## 4. Pipeline nodes and implementation files / Pipeline và file liên quan

| Stage | Purpose | Main files |
|---|---|---|
| Query normalization/rewrite | Prepare stable user query, optional model rewrite. | `backend/app/rag/nodes.py`, `backend/app/rag/rewrite.py` |
| Runtime entity extraction | Extract query entities used by planner/retrieval. | `backend/app/rag/query_entities.py` |
| Query planner | Produce `question_family`, `question_complexity`, `retrieval_plan`. | `backend/app/rag/planner.py` |
| Chart fact extraction | Extract target houses/stars/relations and verified claims from chart JSON. | `backend/app/rag/chart_facts.py` |
| Role-aware retrieval | Build role queries and annotate graph/sparse candidates. | `backend/app/rag/role_retrieval.py`, `backend/app/rag/retrieval.py`, `backend/app/rag/nodes.py` |
| Graph retrieval | Entity matching, graph modes, strict fallback. | `backend/app/rag/retrieval.py`, `backend/app/rag/nodes.py` |
| Dense retrieval | BGE-M3 query embedding and vector search, planner-gated. | `backend/app/rag/nodes.py`, `backend/app/clients.py` |
| Sparse retrieval | Fulltext search with role/generic queries. | `backend/app/rag/retrieval.py`, `backend/app/rag/nodes.py` |
| Fusion/rerank/grading | Rank unified candidates. | `backend/app/rag/ranking.py` |
| Context assembly | Prioritize chart facts and role coverage. | `backend/app/rag/context.py` |
| Generation/citation | Generate answer and map sources. | `backend/app/rag/generation.py`, `backend/app/rag/citations.py` |
| Diagnostics/evaluation | Expose and aggregate retrieval behavior. | `backend/app/rag/diagnostics.py`, `backend/app/rag/evaluation.py` |

---

## 5. Question family mapping / Mapping nhóm câu hỏi

The planner maps each query to a deterministic retrieval plan. The table below summarizes the current `QUESTION_FAMILY_PLANS`.

| question_family | Complexity | Retrieval depth | Required evidence roles | Chart fact intents | Graph mode | Dense gate |
|---|---|---|---|---|---|---|
| `core_identity` | Direct | `chart_only` | `house_scope` | `identity`, `house_facts` | `entity_any`, min 1 | disabled |
| `menh_house_interpretation` | One-hop | `medium` | `house_scope`, `star_definition`, `modifier_effect` | `house_facts`, `star_facts`, `special_states` | `entity_any`, min 1 | enabled, min 2 terms |
| `than_cu_interpretation` | One-hop | `medium` | `house_scope`, `relation_rule`, `star_definition` | `than_position`, `house_facts`, `star_facts` | `entity_any`, min 1 | enabled, min 2 terms |
| `menh_cuc_relation` | One-hop | `medium` | `relation_rule`, `house_scope` | `menh_cuc`, `identity` | `entity_all`, min 2 | enabled, min 2 terms |
| `special_state_interpretation` | One-hop | `medium` | `modifier_effect`, `house_scope`, `star_definition` | `special_states`, `house_facts`, `star_facts` | `entity_any`, min 1 | enabled, min 2 terms |
| `dai_van_interpretation` | One-hop | `medium` | `house_scope`, `relation_rule`, `modifier_effect` | `dai_van`, `house_facts`, `star_facts` | `entity_any`, min 1 | enabled, min 2 terms |
| `menh_tam_hop` | Two-hop | `deep` | `relation_rule`, `combination_pattern`, `house_scope`, `star_definition` | `tam_hop`, `house_facts`, `star_facts` | `min_hit_count`, min 2 | enabled, min 2 terms |
| `menh_xung_chieu` | Two-hop | `deep` | `relation_rule`, `combination_pattern`, `house_scope`, `star_definition` | `xung_chieu`, `house_facts`, `star_facts` | `min_hit_count`, min 2 | enabled, min 2 terms |
| `topic_house_plus_relations` | Two-hop | `deep` | `house_scope`, `star_definition`, `modifier_effect`, `relation_rule` | `topic_house`, `related_houses`, `star_facts`, `special_states` | `min_hit_count`, min 2 | enabled, min 2 terms |
| `synthesis_judgement` | Two-hop | `deep` | `house_scope`, `star_definition`, `modifier_effect`, `relation_rule`, `combination_pattern` | `synthesis_core`, `related_houses`, `star_facts`, `special_states` | `min_hit_count`, min 2 | enabled, min 2 terms |

Notes:

- Dataset items can provide `question_family`; live chat falls back to heuristic inference.
- If a family is unknown, the planner falls back to a synthesis-style plan.
- `core_identity` intentionally disables graph/dense/sparse by plan because the answer should come from chart facts when possible.

---

## 6. Evidence roles / Vai trò evidence

| Evidence role | Purpose | Typical evidence |
|---|---|---|
| `house_scope` | Establish what house/topic the question is about. | Mệnh, Thân, Quan Lộc, Phu Thê, Tài Bạch. |
| `star_definition` | Explain a star or canonical concept. | Thiên Mã chủ động/di chuyển; Tử Vi as chủ tinh. |
| `modifier_effect` | Explain special state or modifier effects. | Tuần/Triệt, miếu/hãm, phụ tinh, trạng thái sao. |
| `relation_rule` | Explain relationship rules. | Tam hợp, xung chiếu, Mệnh-Cục, cung đối chiếu. |
| `combination_pattern` | Support synthesis across several factors. | Tổ hợp sao/cung/quan hệ for judgement questions. |

Role-aware retrieval annotates candidates with fields such as:

```text
evidence_role
evidence_roles
retrieval_intent
role_query
```

Role-aware context assembly uses these annotations to select at least one chunk per required role when budget allows.

---

## 7. Chart facts and chart-aware context / Chart facts và context theo lá số

`extract_chart_facts(chart_data, query_entities, retrieval_plan)` is responsible for defensive parsing of chart data. It supports multiple chart shapes and returns a structured object such as:

```text
target_houses
target_stars
house_facts
relations
claims_verified
unverified_claims
warnings
chart_schema_detected
```

Context assembly then prioritizes chart grounding in this order:

```text
chart summary
chart fact block
role-labeled corpus chunks
```

This matters because Direct chart QA should not depend on corpus retrieval. For One-hop and Two-hop queries, chart facts anchor the answer before the model reads interpretive corpus chunks.

---

## 8. Retrieval path behavior / Hành vi các retrieval path

### 8.1 Graph retrieval

Graph retrieval supports three modes:

| Mode | Behavior |
|---|---|
| `entity_any` | Match chunks mentioning any target entity. Good for broad recall. |
| `entity_all` | Require all target entities. Good for relation-heavy One-hop queries. |
| `min_hit_count` | Require at least N target entity hits. Good for Two-hop/synthesis queries. |

If a strict mode returns zero candidates, graph retrieval falls back in a controlled way and records diagnostics:

```text
requested_mode
effective_mode
required_entity_hits
effective_required_entity_hits
fallback_used
fallback_reason
role_metadata
```

### 8.2 Sparse retrieval

Sparse retrieval uses Neo4j fulltext search and supports role-specific queries plus generic fallback. It remains important because many Tử Vi terms are lexical and canonical.

### 8.3 Dense retrieval

Dense retrieval uses BGE-M3 embeddings in the `bge_m3` slot:

```text
Chunk.embedding_bge_m3
chunkVectorBgeM3
dimension 1024
```

Current production default:

```yaml
dense_retrieval_enabled: false
```

Ablation candidate:

```text
configs/w6_planner_gated_dense.yaml
```

Dense retrieval only runs when all gates allow it:

```text
ExperimentConfig.dense_retrieval_enabled == true
retrieval_plan.enabled_retrieval_paths.dense == true
retrieval_plan.dense_gate.enabled == true
query_term_count >= retrieval_plan.dense_gate.min_query_terms
retrieval backend is available
```

Direct chart-only questions should skip dense even under the ablation config.

W6-RAG-07 also added lazy query embedding caching in `DenseQueryEmbeddingService`. It does **not** preload BGE-M3 automatically.

---

## 9. Context assembly / Ghép context

The context assembly policy after W6-RAG-06 is:

1. Always prioritize chart summary and chart fact block.
2. If `retrieval_plan.required_evidence_roles` is present, select chunks by required role first.
3. Select at least one chunk per required role when budget allows.
4. Fill remaining budget by global ranking.
5. Preserve citation mapping and role labels.

Context summary includes:

```text
required_roles
selected_roles
missing_roles
role_coverage_rate
selected_chunks_by_role
chart_context_priority
has_chart_facts
```

This avoids a failure mode where the top-ranked chunks all support the same role while another required role is missing.

### 9.1 Chốt lại sau kiểm thử chat thật ngày 2026-07-16

Sau khi kiểm thử ba nhóm câu hỏi trong giao diện thật, có hai lỗi chất lượng được phát hiện:

1. Câu factual về lá số đã đúng hơn, nhưng citation fallback còn kéo nhiều nguồn sách không cần thiết cho câu hỏi chỉ cần dữ kiện lá số.
2. Câu interpretive và multi-hop đôi khi giữ chunk có chữ “Mệnh” nhưng nói về sao không có trong lá số, ví dụ chunk về Thất Sát trong khi cung Mệnh thực tế có Thái Dương và Thiên Lương.
3. Câu “tam hợp Phúc-Phối-Di” từng bị entity extraction thêm nhầm cung Phụ Mẫu vào chart facts.

Các sửa đổi đã thêm:

- Khối dữ kiện lá số giờ dùng marker chính thức `[CHART]`, không dùng `[CHART_FACTS]` trong context mới. Citation mapper vẫn hiểu `[CHART_FACTS]` như alias cũ để không vỡ dữ liệu hoặc câu trả lời cũ.
- `chart_facts` khóa `target_houses` khi planner đã nhận diện tam hợp tường minh từ câu hỏi, ví dụ `Phúc-Phối-Di`; entity nhiễu không được tự thêm cung khác.
- `chart_facts` ghi quan hệ tam hợp đã nhận diện vào phần `[LIÊN HỆ CUNG]`, ví dụ `Tam hợp Phúc-Phối-Di: Phúc Đức, Phu Thê, Thiên Di`.
- Context assembly có thêm `chart_relevance_filter`: khi đã có đủ candidate chạm tới sao/cung trong lá số, hệ thống loại bớt chunk chỉ liên quan hời hợt. House-only hit vẫn được giữ cho vai trò `house_scope`, `relation_rule`, `combination_pattern`, nhưng với câu luận sao thì ưu tiên chunk có sao thật trong lá số.
- Prompt generation yêu cầu model chỉ dùng `[CHART]` cho dữ kiện lá số, tránh sinh marker lỗi dạng `[[CHART]_FACTS]`.

Các test liên quan:

```powershell
cd backend
python -m pytest tests/test_rag_chart_facts.py tests/test_rag_context_generation_citations.py tests/test_rag_planner.py tests/test_rag_dry_run.py -q
python -m pytest tests/test_rag_diagnostics.py tests/test_rag_role_retrieval.py tests/test_rag_retrieval.py tests/test_rag_ranking.py -q
```

Kỳ vọng sau sửa:

- Factual chart QA nên trả lời từ `[CHART]` là chính, không cần kéo nhiều nguồn sách nếu câu hỏi chỉ hỏi sao/cung nằm trong lá số.
- Interpretive QA vẫn dùng nguồn sách, nhưng nguồn được chọn nên bám hơn vào sao/cung có thật trong chart facts.
- Multi-hop về tam hợp cung phải giữ đúng bộ cung người dùng hỏi; không được tự thêm cung thứ tư do entity extraction nhiễu.

---

## 10. Diagnostics and evaluation aggregation / Diagnostics và aggregation

Each RAG response/dry-run can expose `retrieval_diagnostics` with fields such as:

```text
question_complexity
question_complexity_source
question_family
question_family_source
extracted_entities
candidate_counts
candidate_counts_by_role
retrieval_node_statuses
final_selected_retrieval_paths
selected_evidence_roles
required_evidence_roles
missing_evidence_roles
retrieval_plan
retrieval_plan_source
graph_retrieval
dense_retrieval
chart_facts
context_summary
warnings
```

The evaluation runner can aggregate metrics by:

```text
question_complexity
question_family
```

Important evaluation metrics:

```text
Faithfulness
Answer Relevancy
Context Recall
Graph Hit Rate
Citation Coverage
p95 latency
retrieval p95 latency when node timing exists
dense selected-context rate for dense ablation
```

For Direct chart-only questions, corpus-grounded metrics such as Context Recall and Citation Coverage should be interpreted carefully because chart facts may be the correct source of truth.

---

## 11. Roadmap task mapping / Mapping Task A-G

| Roadmap task | PLAN task | Status | Main implementation |
|---|---|---|---|
| Task A - Diagnostics | W6-RAG-01 | Complete | `backend/app/rag/diagnostics.py`, evaluation aggregation |
| Task B - Query planner | W6-RAG-02 | Complete | `backend/app/rag/planner.py` |
| Task C - Chart facts | W6-RAG-03 | Complete | `backend/app/rag/chart_facts.py` |
| Task D - Role-aware retrieval | W6-RAG-04 | Complete | `backend/app/rag/role_retrieval.py`, retrieval nodes |
| Task E - Conjunctive graph retrieval | W6-RAG-05 | Complete | graph modes and strict fallback in retrieval |
| Task F - Role-aware context assembly | W6-RAG-06 | Complete | `backend/app/rag/context.py` |
| Task G - Planner-gated dense retrieval | W6-RAG-07 | Complete | dense gate, query cache, ablation config |

Next downstream tasks:

- `W6-ABL-02`: compare default no-dense with `configs/w6_planner_gated_dense.yaml` and other retrieval/fusion/reranker configs.
- `W7-OBS-01`: add production Langfuse spans and dashboards.
- `W7-OBS-02`: measure production p95 latency before final dense decision.
- `W7-CONFIG-01`: choose final production config based on evidence.

---

## 12. Known limitations and production decisions / Các quyết định còn mở cho production

### 12.1 Dense production default

Current decision for W6-RAG-07:

- `configs/default_production.yaml` keeps dense off.
- `configs/w6_planner_gated_dense.yaml` enables dense for ablation.

Production recommendation:

- Do not promote dense into `default_production.yaml` until W6/W7 ablation shows quality gain that justifies latency/cost.
- Confirm p95 end-to-end latency remains within target.

### 12.2 BGE-M3 preload / pre-warm

Current decision:

- No automatic preload.
- Lazy-load plus query embedding cache.

Production recommendation:

- Consider startup pre-warm or background preload only after measuring cold-start impact on Render/local runtime.
- If startup preload causes deploy/cold-start problems, keep lazy-load and rely on cache plus planner gate.

### 12.3 Timing and observability

Current decision:

- W6-RAG-07 measures dense node `duration_ms` only.

Production recommendation:

- W7 observability should add Langfuse spans for all major nodes:
  - rewrite
  - extraction
  - planner
  - chart facts
  - graph retrieval
  - dense retrieval
  - sparse retrieval
  - fusion
  - rerank/grading
  - context assembly
  - generation
  - citation mapping

### 12.4 Reranker and fusion

Current default:

- Fusion: config-aware, default `rrf`.
- Reranker: lexical-overlap heuristic.

Production recommendation:

- Choose final fusion/reranker using W6-ABL-02/W7 evidence.
- Consider stronger reranker only if latency budget allows.

### 12.5 Direct chart QA and citations

Direct chart QA may correctly answer from chart facts without corpus citation. Evaluation and UI should distinguish:

- chart-grounded answer;
- corpus-grounded answer with source citation;
- mixed chart + corpus answer.

---

## 13. Validation plan / Kế hoạch kiểm chứng

Recommended regression command after changing the W6 RAG path:

```powershell
cd backend
python -m pytest tests/test_rag_diagnostics.py tests/test_rag_planner.py tests/test_rag_chart_facts.py tests/test_rag_retrieval.py tests/test_rag_context_generation_citations.py tests/test_rag_dry_run.py tests/test_chat_route.py tests/test_runtime_embedding_service.py tests/test_experiment_config.py -p no:cacheprovider -q
```

Recommended manual/dry-run checks:

1. Direct query such as “Cung Mệnh nằm ở đâu?”
   - expected: `question_complexity = Direct`, `question_family = core_identity`, dense skipped.
2. One-hop query such as “Cung Mệnh có Thiên Mã thì luận thế nào?”
   - expected: chart facts present, required roles include `house_scope` and `star_definition`, graph/sparse candidates tagged by role.
3. Two-hop query such as “Mệnh tam hợp và xung chiếu ảnh hưởng công danh thế nào?”
   - expected: graph mode `min_hit_count`, role coverage summary, context contains multiple roles when available.
4. Dense ablation config:
   - run with `configs/w6_planner_gated_dense.yaml`;
   - Direct chart QA should still skip dense;
   - One-hop/Two-hop can run dense when planner and query length allow it.

---

## 14. How to use this doc / Cách dùng tài liệu này

- For implementation context, start with Sections 3-11.
- For production decisions, read Section 12 before changing `default_production.yaml`.
- For ablation planning, compare default production config against `configs/w6_planner_gated_dense.yaml` and inspect diagnostics in Section 10.
- For onboarding, use the file mapping in Section 4 to jump into code.