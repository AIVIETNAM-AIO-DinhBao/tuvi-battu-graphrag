import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import chunk_text  # noqa: E402


CONFIG_PATH = ROOT_DIR / "configs" / "chunking_strategies.yaml"
CORPUS_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "corpus"
ALL_STRATEGIES = [
    "chunk_structure_parent_child",
    "chunk_fixed_256",
    "chunk_fixed_512",
    "chunk_fixed_1024",
    "chunk_sentence_merge",
    "chunk_semantic",
]
REQUIRED_FIELDS = {
    "chunk_id",
    "parent_id",
    "chunk_type",
    "chunk_text",
    "text",
    "source_id",
    "source_name",
    "source_page",
    "domain",
    "chunk_strategy_id",
    "chunk_hash",
    "provenance",
    "metadata",
    "doc_id",
    "section_id",
    "char_start",
    "char_end",
    "token_count",
    "chunking_version",
    "preserved_entities",
}


def sample_registry() -> dict[str, dict]:
    return {
        "TVGM": {"title": "Tử Vi Giảng Minh", "domain": "tu_vi"},
        "TVNL": {"title": "Tử Vi Nghiệm Lý Toàn Thư", "domain": "tu_vi"},
    }


def make_test_unit(text: str, section_id: str = "TVGM_TEST_SEC01") -> chunk_text.SourceUnit:
    return chunk_text.SourceUnit(
        doc_id="TVGM",
        section_id=section_id,
        text=text,
        source_name="Tử Vi Giảng Minh",
        source_page=1,
        domain="TUVI",
        input_format="clean_json",
        page_pdf_start=1,
        page_pdf_end=1,
        page_book=None,
        metadata={"page_pdf": 1},
    )


def test_config_declares_six_implemented_strategies() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)

    assert set(config["strategies"]) == set(ALL_STRATEGIES)
    assert all(chunk_text.get_strategy_config(config, strategy)["implemented"] for strategy in ALL_STRATEGIES)


def test_load_clean_json_records() -> None:
    clean_path = CORPUS_DIR / "TVGM" / "TVGM_clean.json"

    units = chunk_text.load_clean_json(clean_path, sample_registry())

    assert len(units) > 1
    assert units[0].doc_id == "TVGM"
    assert units[0].source_name == "Tử Vi Giảng Minh"
    assert units[0].source_page == 1
    assert units[0].domain == "TUVI"
    assert units[0].input_format == "clean_json"


def test_load_sections_jsonl_records() -> None:
    sections_path = CORPUS_DIR / "TVGM" / "TVGM_sections.jsonl"

    units = chunk_text.load_sections_jsonl(sections_path, sample_registry())

    assert len(units) > 1
    assert units[0].section_id
    assert units[0].source_page == 1
    assert units[0].page_pdf_end == 1
    assert units[0].input_format == "sections_jsonl"


def test_domain_is_tuvi_only() -> None:
    assert chunk_text.normalize_domain(None) == "TUVI"
    assert chunk_text.normalize_domain("tu_vi") == "TUVI"
    with pytest.raises(ValueError, match="Tử Vi-only"):
        chunk_text.normalize_domain("bat_tu")


def test_tvnl_clean_path_is_used_and_thnl_typo_is_reported() -> None:
    tvnl_clean = CORPUS_DIR / "TVNL" / "TVNL_clean.json"
    thnl_typo = CORPUS_DIR / "TVNL" / "THNL_clean.json"

    assert tvnl_clean.exists()
    assert not thnl_typo.exists()
    assert tvnl_clean.resolve() in chunk_text.discover_input_files([tvnl_clean.parent])
    with pytest.raises(FileNotFoundError, match="Did you mean TVNL_clean.json"):
        chunk_text.discover_input_files([thnl_typo])


def test_chunk_hash_changes_when_strategy_changes() -> None:
    common = {
        "chunking_version": "chunking_v1",
        "config_version": "chunking_v1",
        "chunk_type": "child",
        "doc_id": "TVGM",
        "section_id": "TVGM_SEC01",
        "source_page": 1,
        "char_start": 0,
        "char_end": 42,
        "chunk_text": "Thiên Cơ ở Cung Tý.",
    }

    strategy_a_hash = chunk_text.make_chunk_hash(
        chunk_strategy_id="chunk_structure_parent_child", **common
    )
    fixed_hash = chunk_text.make_chunk_hash(chunk_strategy_id="chunk_fixed_256", **common)

    assert strategy_a_hash != fixed_hash


@pytest.mark.parametrize("strategy_id", ALL_STRATEGIES)
def test_all_strategies_generate_chunks_with_shared_schema(strategy_id: str) -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    text = (
        "Thiên Cơ ở Cung Tý luận về Giáp Tý và Ngũ Hành. "
        "Cung Mệnh cần xét cùng Cung Thân để giữ bối cảnh. "
        "Tử Vi và Thiên Phủ tạo thành một nhóm luận đoán riêng. "
    ) * 90

    chunks = chunk_text.chunk_units([make_test_unit(text)], config=config, strategy_id=strategy_id)

    assert chunks
    assert all(REQUIRED_FIELDS <= set(chunk) for chunk in chunks)
    assert all(chunk["chunk_strategy_id"] == strategy_id for chunk in chunks)
    assert all(chunk["domain"] == "TUVI" for chunk in chunks)
    assert all(chunk["source_id"] == "TVGM" for chunk in chunks)
    assert all(chunk["source_page"] == 1 for chunk in chunks)
    assert all(chunk["text"] == chunk["chunk_text"] for chunk in chunks)
    assert all(chunk["provenance"]["source_id"] == "TVGM" for chunk in chunks)
    assert all(chunk["metadata"]["chunk_strategy_id"] == strategy_id for chunk in chunks)


@pytest.mark.parametrize(
    ("strategy_id", "max_tokens"),
    [
        ("chunk_fixed_256", 256),
        ("chunk_fixed_512", 512),
        ("chunk_fixed_1024", 1024),
    ],
)
def test_fixed_strategies_respect_configured_token_caps(strategy_id: str, max_tokens: int) -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    text = (
        "Thiên Cơ ở Cung Tý luận về Giáp Tý và Ngũ Hành. "
        "Cung Mệnh cần xét cùng Cung Thân để giữ bối cảnh. "
    ) * 140

    chunks = chunk_text.chunk_units([make_test_unit(text)], config=config, strategy_id=strategy_id)

    assert chunks
    assert all(chunk["chunk_type"] == "chunk" for chunk in chunks)
    assert all(chunk["parent_id"] is None for chunk in chunks)
    assert max(chunk["token_count"] for chunk in chunks) <= max_tokens


def test_sentence_merge_does_not_merge_across_source_units() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    first = make_test_unit(
        "Thiên Cơ ở Cung Tý. Cung Mệnh giữ một đoạn riêng. " * 25,
        section_id="TVGM_TEST_SEC01",
    )
    second = make_test_unit(
        "Tử Vi ở Cung Thân. Thiên Phủ giữ một đoạn riêng. " * 25,
        section_id="TVGM_TEST_SEC02",
    )

    chunks = chunk_text.chunk_units(
        [first, second], config=config, strategy_id="chunk_sentence_merge"
    )

    section_ids = {chunk["section_id"] for chunk in chunks}
    assert section_ids == {"TVGM_TEST_SEC01", "TVGM_TEST_SEC02"}
    assert all(chunk["chunk_type"] == "chunk" for chunk in chunks)


def test_semantic_strategy_splits_clear_topic_shift() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    strategy = {
        "chunking_version": "chunk_semantic_test_v1",
        "min_tokens": 10,
        "target_tokens": 20,
        "max_tokens": 80,
        "similarity_threshold": 0.2,
    }
    unit = make_test_unit(
        (
            "Thiên Cơ Cung Mệnh luận sao chính tinh. "
            "Thiên Cơ Cung Mệnh xét thêm Tử Vi Thiên Phủ. "
            "Điền Trạch đất nhà ruộng vườn tài sản. "
            "Điền Trạch nhà cửa đất đai sản nghiệp. "
        )
        * 4
    )

    windows = list(
        chunk_text.iter_semantic_windows(
            [unit],
            strategy=strategy,
            protected_terms=["Thiên Cơ", "Cung Mệnh", "Điền Trạch"],
        )
    )

    assert len(windows) >= 2


def test_parent_child_schema_and_parent_references() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    text = (
        "Thiên Cơ ở Cung Tý luận về Giáp Tý và Ngũ Hành. "
        "Cung Mệnh cần xét cùng Cung Thân để giữ bối cảnh. "
    ) * 70
    unit = make_test_unit(text)

    chunks = chunk_text.chunk_units(
        [unit], config=config, strategy_id="chunk_structure_parent_child"
    )
    parents = [chunk for chunk in chunks if chunk["chunk_type"] == "parent"]
    children = [chunk for chunk in chunks if chunk["chunk_type"] == "child"]
    parent_ids = {chunk["chunk_id"] for chunk in parents}
    assert parents
    assert children
    assert all(REQUIRED_FIELDS <= set(chunk) for chunk in chunks)
    assert all(parent["parent_id"] is None for parent in parents)
    assert all(child["parent_id"] in parent_ids for child in children)
    assert all(chunk["metadata"]["chunk_strategy_id"] == "chunk_structure_parent_child" for chunk in chunks)
    assert all(chunk["domain"] == "TUVI" for chunk in chunks)
    assert all(chunk["source_id"] == "TVGM" for chunk in chunks)
    assert all(chunk["text"] == chunk["chunk_text"] for chunk in chunks)
    assert all(chunk["provenance"]["source_id"] == "TVGM" for chunk in chunks)
    assert any("Thiên Cơ" in chunk["preserved_entities"] for chunk in chunks)


def test_protected_terms_are_not_split_by_long_segment_fallback() -> None:
    segment = (
        "a b c d Thiên Cơ e f g h Cung Tý i j k l Giáp Tý m n o p"
    )
    atoms = chunk_text.split_long_segment(
        segment,
        absolute_start=0,
        protected_terms=["Thiên Cơ", "Cung Tý", "Giáp Tý"],
        max_tokens=5,
    )
    atom_texts = [atom.text for atom in atoms]

    assert any("Thiên Cơ" in text for text in atom_texts)
    assert any("Cung Tý" in text for text in atom_texts)
    assert any("Giáp Tý" in text for text in atom_texts)
    assert all(not text.endswith("Thiên") for text in atom_texts)
    assert all(not text.startswith("Cơ ") for text in atom_texts)
    assert all(not text.endswith("Cung") for text in atom_texts)
    assert all(not text.startswith("Tý ") for text in atom_texts)
    assert all(not text.endswith("Giáp") for text in atom_texts)
    assert all(not text.startswith("Tý ") for text in atom_texts)
