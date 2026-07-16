# W7-CONFIG-01 - Production config decision

- Decision date: `2026-07-16`
- Status: `LOCKED`
- Scope: final operational default for W7 deploy/observability
- Full-dataset status: not run; final scientific evaluation remains deferred to `W8-EVAL-01`

## Decision

The evidence-backed production default is locked at:

| Setting | Selected value |
|---|---|
| Config file | `configs/default_production.yaml` |
| Experiment ID | `default_production_v2` |
| Chunk strategy | `chunk_semantic_embedding_bge_m3` |
| Embedding | `BAAI/bge-m3`, `chunkVectorBgeM3`, 1024 dimensions |
| Retrieval | Graph + Sparse |
| Dense retrieval | Off |
| Fusion | RRF |
| Reranker | `lexical-overlap-v1`, enabled, `top_k=10` |
| Query rewrite | Off |
| Runtime entity extraction | Dictionary rules, enabled |
| Prompt | `tuvi_generation_v1` |
| Generation model | `gemini-3.1-flash-lite-preview` |
| Context assembly | `balanced` |
| Cache | Disabled |

Relative to `default_production_v1`, this lock changes the experiment ID, marks the config as W7 evidence-locked, and promotes chunking from `chunk_fixed_512` to `chunk_semantic_embedding_bge_m3`. The remaining retrieval and generation settings retain the W6 integration/W7 ablation candidate stack.

## Evidence summary

### W6-ABL-03 - Chunking strategy

Source: `benchmark/tuvi_golden_dataset/reports/w6_abl_03/evaluation_report.md`

- Judge: Gemini
- Dataset: 10 balanced items (`TVQA-001..TVQA-010`) covering all 10 question families
- Corpus coverage: all 12 source/strategy pairs were available in Neo4j
- Retrieval control: Graph + Sparse + RRF + lexical reranker, dense off

| Config | Chunk strategy | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms | Retrieval misses |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `fixed_512_graph_sparse_rrf` | `chunk_fixed_512` | 0.81 | 0.70 | **0.5556** | 1.0 | 1.0 | 14074.47 | 3 |
| `parent_child_graph_sparse_rrf` | `chunk_structure_parent_child` | 0.74 | 0.67 | 0.5444 | 1.0 | 1.0 | **7431.16** | 3 |
| `semantic_bge_m3_graph_sparse_rrf` | `chunk_semantic_embedding_bge_m3` | **0.85** | **0.74** | 0.5444 | 1.0 | 1.0 | 18042.16 | **2** |

`chunk_semantic_embedding_bge_m3` is selected for the quality-first W7 default because it has the highest faithfulness and answer relevancy and the fewest retrieval misses, while matching the other strategies on graph hit and citation coverage. It does not win context recall or latency: fixed-512 has a 0.0112 context-recall advantage, and parent-child has substantially lower p95 latency. These trade-offs remain explicit and must be revisited in production latency measurement and the full evaluation.

### W7-ABL-01 - Generation prompt/model

Source: `benchmark/tuvi_golden_dataset/reports/w7_abl_01/evaluation_report.md`

- Judge: Gemini
- Dataset: the same 10-item balanced subset
- Retrieval control: semantic BGE-M3 chunking, Graph + Sparse + RRF + lexical reranker, dense off
- Model control: all three prompt candidates used `gemini-3.1-flash-lite-preview`

| Config | Prompt | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|
| `baseline_v1_flash_lite` | `tuvi_generation_v1` | **0.92** | **0.79** | **0.7000** | 1.0 | 1.0 | **25911.78** |
| `grounded_v2_flash_lite` | `tuvi_generation_grounded_v2` | **0.92** | 0.76 | 0.6444 | 1.0 | 1.0 | 30187.57 |
| `structured_v3_flash_lite` | `tuvi_generation_structured_v3` | 0.67 | 0.52 | 0.3222 | 1.0 | 1.0 | 28321.40 |

`tuvi_generation_v1` is selected because it ties for best faithfulness and leads answer relevancy, context recall, and p95 latency among the three tested prompts, with no citation-coverage or graph-hit regression. The model remains `gemini-3.1-flash-lite-preview` because it is the only generation model controlled in this ablation; this is not evidence that it beats untested model families.

### W6-ABL-02 - Retrieval/fusion/reranker

Source: `benchmark/tuvi_golden_dataset/reports/w6_abl_02/evaluation_report.md`

This report is plumbing evidence only: it used `judge_backend=static-smoke`, 2 items, and 11 configurations. It cannot establish an official quality winner and its generated `baseline_graph_first` recommendation is not used for the production decision.

Graph + Sparse + RRF + lexical reranker is retained as the conservative integration-proven control stack because:

1. W6-ABL-03 and W7-ABL-01 both held this stack fixed and completed their Gemini partial-10 runs.
2. W6-INT-01 passed three representative live-runtime RAG smoke queries with citations and recorded no P0/P1/P2 issue (`benchmark/tuvi_golden_dataset/reports/w6_int_01/integration_report.md`).
3. There is not yet sufficient official retrieval ablation or production latency evidence to promote dense retrieval or another fusion/reranking variant.

This is an evidence-preserving choice, not a claim that the stack won a full official retrieval ablation.

## Rationale by setting

- **Semantic BGE-M3 chunking:** strongest answer-quality profile in W6-ABL-03 (faithfulness 0.85, relevancy 0.74) and one fewer retrieval miss than either alternative. The higher observed p95 is accepted temporarily under a quality-first policy.
- **Graph + Sparse + RRF:** this is the fixed stack behind the successful chunk and prompt candidates. Changing it during config lock would introduce an unvalidated variable.
- **Lexical reranker enabled:** kept from the controlled candidate stack; W6-ABL-02 is too small/static to justify disabling or replacing it.
- **Dense retrieval off:** no official evidence yet shows an adequate quality gain relative to latency/cost. Keeping it off is the safer production default until retrieval ablation and p95 evidence exist.
- **Query rewrite off:** it adds an external Gemini call before retrieval and has no dedicated ablation demonstrating sufficient benefit to justify latency, cost, and failure-surface growth.
- **Prompt v1:** best overall quality/latency balance in W7-ABL-01.
- **Gemini Flash Lite preview:** retained because it is the tested W7 generation control and current runtime model. Alternative models were not compared, so the selection is operational rather than cross-model proof.
- **Balanced context assembly and cache disabled:** unchanged from the tested integration/ablation candidate to avoid adding uncontrolled config changes during the lock.

## Locked config hash

```text
config_hash=c40227a029588b7793201702798e96e640d7a436131d6f5f0437f67151803d96
```

The hash is the SHA-256 produced by `backend/app/rag/config.py::config_hash` over the sorted, JSON-serialized, Pydantic-normalized `ExperimentConfig` payload, with all `Path` values canonicalized to POSIX form for Windows/Linux stability. It is not a raw-file checksum. Any semantic config change requires a new experiment ID/decision entry and a recomputed hash.

Recompute on the repository's Windows environment:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe -c "from pathlib import Path; from app.rag.config import load_experiment_config, config_hash; c=load_experiment_config(Path('configs/default_production.yaml')); print(config_hash(c))"
```

## Experiments and measurements not run / deferred

| Deferred work | Reason / next gate |
|---|---|
| Full 100-item golden-dataset evaluation of `default_production_v2` | Gemini quota/time/capacity; planned for `W8-EVAL-01` or a pre-release full run |
| Full/official Gemini W6-ABL-02 retrieval/fusion/reranker matrix | Existing evidence is only static smoke on 2 items; run when quota and live-service capacity permit |
| Dense-retrieval production promotion study | Needs official quality delta plus retrieval/end-to-end p95 and cost evidence |
| Query-rewrite ablation | Extra Gemini call increases latency/cost; no isolated evidence yet |
| Alternative generation models beyond Gemini Flash Lite preview | W7-ABL-01 varied prompts only; additional model access/quota is required |
| W7-OBS-02 production p95 over 20 mixed queries | Depends on deploy/observability; the current partial evaluation latency is not production p95 |
| Persisted official experiment runs in Supabase | Live PostgREST cannot see `public.experiment_runs`; runs used `--skip-persistence` |

## Caveats and blockers

1. **Partial evidence:** W6-ABL-03 and W7-ABL-01 each use 10 balanced items, not all 100 release items. The selected config is the final W7 operational default, not a completed full-dataset scientific conclusion.
2. **Latency target is not established:** semantic chunking had W6 p95 `18042.16 ms`, and prompt v1 had W7 end-to-end p95 `25911.78 ms`. These cross-run figures are diagnostic, not production `W7-OBS-02` measurements, and exceed the PLAN target of 8 seconds; latency optimization remains required.
3. **Retrieval evidence gap:** W6-ABL-02 cannot prove a retrieval/fusion/reranker winner because it is a 2-item static smoke run.
4. **Supabase persistence blocker:** the observed error is `Could not find the table 'public.experiment_runs' in the schema cache` (`PGRST205`). Apply `infra/supabase/migrations/20260709_experiment_runs.sql` to the live project and reload PostgREST schema cache before persisted final runs.
5. **SDK technical debt:** runtime/evaluation still imports deprecated `google.generativeai`; migrate to `google.genai` separately.
6. **Neo4j technical debt:** prior live logs contain `CALL subquery without a variable scope clause is deprecated`; this warning did not block the evaluated runs but should be removed before a future Neo4j upgrade.

## Acceptance

`configs/default_production.yaml` is unambiguous and locked for the next W7 tasks as `default_production_v2`. Deployment must expose the experiment ID, config hash, chunk strategy, and prompt metadata so the deployed runtime can be checked against this decision. Full evaluation and production p95 remain explicit follow-up gates rather than implied completed work.
