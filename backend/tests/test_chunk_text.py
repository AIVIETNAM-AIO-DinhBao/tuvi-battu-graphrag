import sys
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

import chunk_text  # noqa: E402


CONFIG_PATH = ROOT_DIR / "configs" / "chunking_strategies.yaml"
CORPUS_DIR = ROOT_DIR / "benchmark" / "tuvi_golden_dataset" / "corpus"


def sample_registry() -> dict[str, dict]:
    return {
        "TVGM": {"title": "Tử Vi Giảng Minh", "domain": "tu_vi"},
        "TVNL": {"title": "Tử Vi Nghiệm Lý Toàn Thư", "domain": "tu_vi"},
    }


def test_config_declares_six_strategies_and_blocks_unimplemented() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)

    assert set(config["strategies"]) == {
        "chunk_structure_parent_child",
        "chunk_fixed_256",
        "chunk_fixed_512",
        "chunk_fixed_1024",
        "chunk_sentence_merge",
        "chunk_semantic",
    }
    assert chunk_text.get_strategy_config(config, "chunk_structure_parent_child")["implemented"]
    with pytest.raises(NotImplementedError, match="not implemented"):
        chunk_text.get_strategy_config(config, "chunk_fixed_256")


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


def test_parent_child_schema_and_parent_references() -> None:
    config = chunk_text.load_chunking_config(CONFIG_PATH)
    text = (
        "Thiên Cơ ở Cung Tý luận về Giáp Tý và Ngũ Hành. "
        "Cung Mệnh cần xét cùng Cung Thân để giữ bối cảnh. "
    ) * 70
    unit = chunk_text.SourceUnit(
        doc_id="TVGM",
        section_id="TVGM_TEST_SEC01",
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

    chunks = chunk_text.chunk_units(
        [unit], config=config, strategy_id="chunk_structure_parent_child"
    )
    parents = [chunk for chunk in chunks if chunk["chunk_type"] == "parent"]
    children = [chunk for chunk in chunks if chunk["chunk_type"] == "child"]
    parent_ids = {chunk["chunk_id"] for chunk in parents}
    required_fields = {
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

    assert parents
    assert children
    assert all(required_fields <= set(chunk) for chunk in chunks)
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
