from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "local_tools"
NOTEBOOK_DIR = ROOT / "notebooks"


def lines(text: str) -> list[str]:
    return [line + "\n" for line in text.strip("\n").splitlines()]


def markdown(text: str) -> dict[str, Any]:
    return {"cell_type": "markdown", "metadata": {}, "source": lines(text)}


def code(text: str, *, tags: list[str] | None = None) -> dict[str, Any]:
    metadata = {"tags": tags} if tags else {}
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": metadata,
        "outputs": [],
        "source": lines(text),
    }


def write_notebook(name: str, cells: list[dict[str, Any]]) -> None:
    metadata: dict[str, Any] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.x"},
    }
    payload = {"cells": cells, "metadata": metadata, "nbformat": 4, "nbformat_minor": 5}
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    (NOTEBOOK_DIR / name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )


def standalone_source(module_name: str) -> str:
    """Embed canonical helpers in a notebook without package-relative imports or CLI entry points."""
    common = (TOOLS_DIR / "common.py").read_text(encoding="utf-8")
    module = (TOOLS_DIR / module_name).read_text(encoding="utf-8")
    common = common.replace("from __future__ import annotations\n", "")
    module = module.replace("from __future__ import annotations\n", "")
    module = re.sub(
        r"from \.common import (?:\([\s\S]*?\)\r?\n|[^\r\n]*\r?\n)",
        "",
        module,
        count=1,
    )
    module = module.split("\ndef main() -> None:", 1)[0]
    return "# AUTO-EMBEDDED: standalone runtime; no repo import is required.\n" + common + "\n" + module


PREPARE_RUNTIME = standalone_source("prepare_model.py")
INFERENCE_RUNTIME = standalone_source("run_inference.py")


write_notebook(
    "00_prepare_model_dataset_kaggle.ipynb",
    [
        markdown(
            """
# 00 — Prepare private model dataset (Kaggle, Internet ON)

Notebook **standalone**: không cần repo, không cần dataset code. Chạy hai version, mỗi version chọn một `MODEL_KEY`. Gemma 3 cần chấp nhận license trên Hugging Face và Kaggle Secret `HF_TOKEN`.
"""
        ),
        code(
            """
# ===== CONFIG DUY NHẤT CẦN ĐỔI =====
MODEL_KEY = 'qwen25_7b'  # qwen25_7b | gemma3_4b

MODEL_REGISTRY = {
    'qwen25_7b': {
        'model_id': 'Qwen/Qwen2.5-7B-Instruct',
        'loader': 'causal_lm',
        'gated': False,
    },
    'gemma3_4b': {
        'model_id': 'google/gemma-3-4b-it',
        'loader': 'gemma3_conditional',
        'gated': True,
    },
}
DOWNLOAD_WHEELS = True
HASH_LARGE_FILES = True
assert MODEL_KEY in MODEL_REGISTRY
MODEL_SPEC = MODEL_REGISTRY[MODEL_KEY]
MODEL_SPEC
"""
        ),
        code(
            """
# Internet phải ON ở notebook 00. Phiên bản >=4.51 cần cho Gemma 3.
%pip install -q "transformers>=4.51,<5" "accelerate>=0.34,<2" "bitsandbytes>=0.43,<1" "huggingface-hub>=0.27,<2" "safetensors>=0.4,<1" "tokenizers>=0.20,<1" "sentencepiece>=0.2,<1"
"""
        ),
        code(PREPARE_RUNTIME, tags=["standalone-runtime"]),
        code(
            """
hf_token = None
if MODEL_SPEC['gated']:
    from kaggle_secrets import UserSecretsClient
    hf_token = UserSecretsClient().get_secret('HF_TOKEN')
    assert hf_token, 'Thiếu Kaggle Secret HF_TOKEN hoặc chưa được cấp quyền Gemma'

MODEL_CONFIG = {
    'model_key': MODEL_KEY,
    'model_id': MODEL_SPEC['model_id'],
    'loader': MODEL_SPEC['loader'],
    'revision': 'main',
    'hf_token': hf_token,
    'download_wheels': DOWNLOAD_WHEELS,
    'hash_large_files': HASH_LARGE_FILES,
    'output_root': f'/kaggle/working/{MODEL_KEY}_offline_dataset',
}
print({key: ('<set>' if key == 'hf_token' and value else value) for key, value in MODEL_CONFIG.items()})
manifest = prepare_model_assets(MODEL_CONFIG)
"""
        ),
        code(
            """
from pathlib import Path
output_root = Path(MODEL_CONFIG['output_root'])
assert (output_root / 'asset_manifest.json').exists()
assert (output_root / 'model' / 'config.json').exists()
assert list((output_root / 'model').glob('*.safetensors'))
assert manifest['model_id'] == MODEL_SPEC['model_id']
assert manifest['loader'] == MODEL_SPEC['loader']
print({
    'PASS': True,
    'output_root': str(output_root),
    'model_id': manifest['model_id'],
    'revision': manifest['resolved_revision'],
    'size_GB': round(manifest['total_size_bytes'] / 1e9, 2),
})
"""
        ),
        markdown(
            """
## Sau khi chạy

Save Version, sau đó tạo **private Kaggle Dataset** từ toàn bộ output folder. Không tải hoặc chia sẻ `HF_TOKEN`. Xem `KAGGLE_DATASET_GUIDE.md` trong repo để biết từng bước.
"""
        ),
    ],
)


write_notebook(
    "01_build_retrieval_bundle_local.ipynb",
    [
        markdown(
            """
# 01 — Build frozen retrieval bundle (LOCAL)

Notebook này chạy từ clone của repo, dùng Neo4j/BGE/reranker hiện tại và `local_tools` trong repo. Nó capture 3 config × 100 prompt/context mà không gọi model generation.
"""
        ),
        code(
            """
from pathlib import Path
import sys

# Nếu auto-detect không được, điền đường dẫn repo tuyệt đối vào đây.
REPO_ROOT = None
RUN_MODE = 'smoke'  # smoke | official

def find_repo(explicit=None):
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        assert (candidate / 'backend' / 'app').exists(), candidate
        return candidate
    starts = [Path.cwd().resolve(), *Path.cwd().resolve().parents]
    direct = [p for p in starts if (p / 'backend' / 'app').exists()]
    children = [p / 'tuvi-battu-graphrag' for p in starts if (p / 'tuvi-battu-graphrag' / 'backend' / 'app').exists()]
    matches = sorted(set(direct + children))
    assert len(matches) == 1, f'Hãy đặt REPO_ROOT; tìm thấy {matches}'
    return matches[0]

REPO_ROOT = find_repo(REPO_ROOT)
KIT_ROOT = REPO_ROOT / 'benchmark' / 'tuvi_golden_dataset' / 'local_llm_ablation'
sys.path.insert(0, str(KIT_ROOT))
print({'repo': str(REPO_ROOT), 'kit': str(KIT_ROOT), 'mode': RUN_MODE})
"""
        ),
        code(
            """
is_official = RUN_MODE == 'official'
BUNDLE_CONFIG = {
    'repo_root': str(REPO_ROOT),
    'kit_root': str(KIT_ROOT),
    'plan_path': str(KIT_ROOT / 'experiment_plan.json'),
    'suites': ['report_shortlist_3'],
    'item_limit': None if is_official else 2,
    'candidate_log_k': 100,
    'retry_failed': True,
    'output_dir': str(KIT_ROOT / 'artifacts' / ('context_bundle_v1' if is_official else 'context_bundle_smoke')),
}
from local_tools.build_bundle import build_context_bundle
manifest = build_context_bundle(BUNDLE_CONFIG)
manifest
"""
        ),
        code(
            """
expected = 300 if is_official else 6
assert manifest['config_count'] == 3, manifest
assert manifest['planned_pair_count'] == expected, manifest
assert manifest['completed_pair_count'] == expected, manifest
assert manifest['failed_pair_count'] == 0, manifest
assert manifest['is_complete'], manifest
assert manifest['failed_this_run'] == 0, manifest

import shutil
bundle_dir = Path(BUNDLE_CONFIG['output_dir'])
archive = shutil.make_archive(str(bundle_dir), 'zip', root_dir=bundle_dir)
print('PASS — upload file này thành private Kaggle Dataset:', archive)
"""
        ),
    ],
)


write_notebook(
    "02_generate_offline_kaggle.ipynb",
    [
        markdown(
            """
# 02 — Offline generation (Kaggle GPU, Internet OFF)

Notebook **standalone**: không cần repo hay code dataset. Add Input gồm frozen context dataset và đúng private model dataset, rồi đổi ba biến config bên dưới.
"""
        ),
        code(
            """
# ===== CONFIG DUY NHẤT CẦN ĐỔI =====
RUNNER = 'B'               # B | C | D
MODEL_KEY = 'qwen25_7b'    # qwen25_7b | gemma3_4b
RUN_MODE = 'smoke'         # smoke | official

RUNNER_CONFIGS = {
    'B': 'report_shortlist_3::graph_dense_rrf',
    'C': 'report_shortlist_3::semantic_gs_rrf_rerank_k40',
    'D': 'report_shortlist_3::semantic_gs_rrf_no_rerank_reference',
}
MODEL_REGISTRY = {
    'qwen25_7b': 'Qwen/Qwen2.5-7B-Instruct',
    'gemma3_4b': 'google/gemma-3-4b-it',
}

# Chỉ điền khi auto-detect báo nhiều hơn một input phù hợp.
BUNDLE_INPUT = None       # folder chứa bundle_manifest.json hoặc file context_bundle_v1.zip
MODEL_ASSET_DIR = None    # folder chứa asset_manifest.json

assert RUNNER in RUNNER_CONFIGS
assert MODEL_KEY in MODEL_REGISTRY
assert RUN_MODE in {'smoke', 'official'}
"""
        ),
        code(
            """
from pathlib import Path
import json, zipfile

def safe_extract(archive_path, destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if destination not in target.parents and target != destination:
                raise RuntimeError(f'Unsafe ZIP member: {member.filename}')
        archive.extractall(destination)
    matches = sorted({p.parent for p in destination.rglob('bundle_manifest.json')})
    assert len(matches) == 1, f'ZIP phải chứa đúng một bundle: {matches}'
    return matches[0]

def resolve_bundle(explicit=None):
    if explicit:
        path = Path(explicit)
        if path.is_file() and path.suffix.lower() == '.zip':
            return safe_extract(path, '/kaggle/working/_context_bundle_input')
        assert (path / 'bundle_manifest.json').exists(), path
        return path
    raw = sorted({p.parent for p in Path('/kaggle/input').rglob('bundle_manifest.json')})
    if len(raw) == 1:
        return raw[0]
    archives = []
    for path in Path('/kaggle/input').rglob('*.zip'):
        try:
            with zipfile.ZipFile(path) as archive:
                if any(Path(name).name == 'bundle_manifest.json' for name in archive.namelist()):
                    archives.append(path)
        except zipfile.BadZipFile:
            pass
    assert len(archives) == 1, f'Hãy đặt BUNDLE_INPUT; raw={raw}, zip={archives}'
    return safe_extract(archives[0], '/kaggle/working/_context_bundle_input')

def resolve_model_asset(expected_model_id, explicit=None):
    candidates = [Path(explicit)] if explicit else sorted({p.parent for p in Path('/kaggle/input').rglob('asset_manifest.json')})
    matches = []
    for path in candidates:
        manifest_path = path / 'asset_manifest.json'
        if manifest_path.exists() and json.loads(manifest_path.read_text(encoding='utf-8')).get('model_id') == expected_model_id:
            matches.append(path)
    assert len(matches) == 1, f'Hãy đặt MODEL_ASSET_DIR cho {expected_model_id}; tìm thấy {matches}'
    return matches[0]

BUNDLE_DIR = resolve_bundle(BUNDLE_INPUT)
MODEL_ASSET_DIR = resolve_model_asset(MODEL_REGISTRY[MODEL_KEY], MODEL_ASSET_DIR)
print({'bundle': str(BUNDLE_DIR), 'model_assets': str(MODEL_ASSET_DIR)})
"""
        ),
        code(INFERENCE_RUNTIME, tags=["standalone-runtime"]),
        code(
            """
INFERENCE_CONFIG = {
    'bundle_dir': str(BUNDLE_DIR),
    'model_asset_dir': str(MODEL_ASSET_DIR),
    'expected_model_id': MODEL_REGISTRY[MODEL_KEY],
    'suites': ['report_shortlist_3'],
    'selected_config_keys': [RUNNER_CONFIGS[RUNNER]],
    'shard_id': 0,
    'num_shards': 1,
    'limit': 2 if RUN_MODE == 'smoke' else None,
    'seed': 42,
    'quantization': '4bit',
    'max_input_tokens': 24576,
    'max_new_tokens': 1024,
    'retry_errors': True,
    'install_wheelhouse': True,
    'output_root': '/kaggle/working/local_llm_ablation_smoke' if RUN_MODE == 'smoke' else '/kaggle/working/local_llm_ablation',
}
summary = run_offline_inference(INFERENCE_CONFIG)
"""
        ),
        code(
            """
expected = 2 if RUN_MODE == 'smoke' else 100
assert summary['assigned_pair_count'] == expected, summary
assert summary['completed_pair_count'] == expected, summary
assert summary['failed_pair_count'] == 0, summary
assert summary['is_complete'], summary
print('PASS — tải ZIP này về gửi A:', summary['archive_path'])
"""
        ),
    ],
)


write_notebook(
    "03_gemini_judge_local.ipynb",
    [
        markdown(
            """
# 03 — Distributed Gemini judge và final merge (LOCAL)

B/C/D chọn `ACTION='judge'` để mỗi người chấm 200 answers của config mình. A chọn `ACTION='merge'` sau khi nhận ba judge-shard ZIP; merge không gọi Gemini lại.

Một answer thành công dùng **một Gemini API call** và nhận cả ba score trong cùng JSON. `retry_attempts=3` chỉ áp dụng khi call lỗi.
"""
        ),
        code(
            """
from pathlib import Path
import sys

REPO_ROOT = None
ACTION = 'judge'  # judge | merge
RUNNER = 'B'      # B | C | D khi ACTION='judge'
MINIMUM_KEY_COUNT = 2

RUNNER_CONFIGS = {
    'B': 'report_shortlist_3::graph_dense_rrf',
    'C': 'report_shortlist_3::semantic_gs_rrf_rerank_k40',
    'D': 'report_shortlist_3::semantic_gs_rrf_no_rerank_reference',
}
KEY_OFFSETS = {'B': 0, 'C': 1, 'D': 2}
assert ACTION in {'judge', 'merge'}
assert RUNNER in RUNNER_CONFIGS

def find_repo(explicit=None):
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        assert (candidate / 'backend' / 'app').exists(), candidate
        return candidate
    starts = [Path.cwd().resolve(), *Path.cwd().resolve().parents]
    direct = [p for p in starts if (p / 'backend' / 'app').exists()]
    children = [p / 'tuvi-battu-graphrag' for p in starts if (p / 'tuvi-battu-graphrag' / 'backend' / 'app').exists()]
    matches = sorted(set(direct + children))
    assert len(matches) == 1, f'Hãy đặt REPO_ROOT; tìm thấy {matches}'
    return matches[0]

REPO_ROOT = find_repo(REPO_ROOT)
KIT_ROOT = REPO_ROOT / 'benchmark' / 'tuvi_golden_dataset' / 'local_llm_ablation'
BUNDLE_DIR = KIT_ROOT / 'artifacts' / 'context_bundle_v1'
assert (BUNDLE_DIR / 'bundle_manifest.json').exists(), BUNDLE_DIR
sys.path.insert(0, str(KIT_ROOT))
"""
        ),
        code(
            """
if ACTION == 'judge':
    prediction_dir = KIT_ROOT / 'artifacts' / 'judge_inputs' / RUNNER
    output_dir = KIT_ROOT / 'artifacts' / 'gemini_judge_shards' / RUNNER
    judge_config = {
        'repo_root': str(REPO_ROOT),
        'bundle_dir': str(BUNDLE_DIR),
        'prediction_roots': [str(prediction_dir)],
        'suites': ['report_shortlist_3'],
        'selected_config_keys': [RUNNER_CONFIGS[RUNNER]],
        'expected_model_ids': ['Qwen/Qwen2.5-7B-Instruct', 'google/gemma-3-4b-it'],
        'judge_model': 'gemini-3.1-flash-lite-preview',
        'initial_key_offset': KEY_OFFSETS[RUNNER],
        'minimum_key_count': MINIMUM_KEY_COUNT,
        'retry_attempts': 3,
        'retry_base_seconds': 2.0,
        'retry_failed': True,
        'allow_incomplete': False,
        'shard_name': RUNNER,
        'output_dir': str(output_dir),
    }
    from local_tools.run_judge import run_gemini_judge
    result = run_gemini_judge(judge_config)
else:
    shard_dir = KIT_ROOT / 'artifacts' / 'downloaded_judge_shards'
    output_dir = KIT_ROOT / 'artifacts' / 'gemini_judge_final'
    merge_config = {
        'repo_root': str(REPO_ROOT),
        'kit_root': str(KIT_ROOT),
        'bundle_dir': str(BUNDLE_DIR),
        'judge_shard_roots': [str(shard_dir)],
        'suites': ['report_shortlist_3'],
        'expected_model_ids': ['Qwen/Qwen2.5-7B-Instruct', 'google/gemma-3-4b-it'],
        'output_dir': str(output_dir),
    }
    from local_tools.merge_judge_shards import merge_gemini_judge_shards
    result = merge_gemini_judge_shards(merge_config)
result
"""
        ),
        code(
            """
if ACTION == 'judge':
    assert result['retrieval_pair_count'] == 100, result
    assert result['expected_prediction_count'] == 200, result
    assert result['judged_completed_count'] == 200, result
    assert result['judged_failed_count'] == 0, result
    assert result['is_complete'], result
    assert result['key_rotation']['key_count'] >= MINIMUM_KEY_COUNT, result
    print('PASS — gửi judge-shard ZIP này cho A:', result['archive_path'])
else:
    assert result['source_shard_count'] == 3, result
    assert result['expected_pair_count'] == 600, result
    assert result['completed_pair_count'] == 600, result
    assert result['failed_pair_count'] == 0, result
    assert result['config_result_count'] == 6, result
    assert result['is_complete'], result
    print('PASS — canonical final report:', output_dir / 'evaluation_report.json')
"""
        ),
    ],
)

print(f"Generated four notebooks in {NOTEBOOK_DIR}")
