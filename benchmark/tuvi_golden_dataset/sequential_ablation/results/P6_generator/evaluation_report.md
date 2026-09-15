# P6 generator × prompt matrix — summary

- Status: `completed`
- Dataset: TuViQA v1 release, 100 items per row
- Judge: Gemini Flash Lite, protocol `blind-v2`, evaluator SHA-256
  `78dce3092a4e28ee915bbfdad61341d6f0ad1761070d0c12240ab7b5b4202464`
- Matrix: 3 generators × 2 shortlisted prompts = 6 rows
- All six rows: 100/100 completed, zero failed pairs and zero invalid markers.

## Overall metrics

| Model | Prompt | Faithfulness | Answer Relevancy | p95 latency ms |
|---|---|---:|---:|---:|
| Gemini Flash Lite | Prompt 1 (`tuvi_generation_v1`) | **0.9380** | 0.839 | 162862.24 |
| Qwen2.5-7B-Instruct 4-bit | Prompt 1 (`tuvi_generation_v1`) | 0.4350 | 0.577 | 164319.99 |
| Gemma-3-4B-IT 4-bit | Prompt 1 (`tuvi_generation_v1`) | 0.3460 | 0.444 | 164261.92 |
| Gemini Flash Lite | Prompt 3 (`tuvi_generation_answer_first_v4`) | 0.8755 | **0.898** | 163276.75 |
| Qwen2.5-7B-Instruct 4-bit | Prompt 3 (`tuvi_generation_answer_first_v4`) | 0.3030 | 0.519 | 163615.79 |
| Gemma-3-4B-IT 4-bit | Prompt 3 (`tuvi_generation_answer_first_v4`) | 0.2980 | 0.503 | 167223.43 |

## Interpretation

P5's registered primary metric is Faithfulness. Prompt 1 is therefore the
P5 winner and also has higher Faithfulness for all three generators in this
P6 prompt-sensitivity matrix. Gemini Flash Lite + Prompt 1 is the final
candidate for P7 confirmation. Prompt 3 improves Answer Relevancy for Gemini
and Gemma, but does not replace Prompt 1 as the primary-metric selection.

Compare generators only within a prompt, and prompts only within a generator.
P6 is a frozen-context generation comparison; P7 is the live end-to-end
confirmation.

## Canonical artifacts

The complete artifacts remain in their original directories because they also
contain the frozen bundle, Kaggle notebooks, prediction ZIPs, checkpoints and
per-item records:

- Prompt 1 report: `../../p6_kaggle/judge_final/evaluation_report.md`
- Prompt 3 report: `../../p6_prompt3/judge_final/evaluation_report.md`

This summary intentionally does not duplicate those large artifacts.
