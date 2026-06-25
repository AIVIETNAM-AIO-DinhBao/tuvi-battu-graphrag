import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1] / "charts"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    registry_path = BASE / "registry" / "chart_registry.json"
    registry = load_json(registry_path)

    assert len(registry) == 10, f"Expected 10 registry entries, got {len(registry)}"
    assert len(list((BASE / "chart_repr").glob("CHART-*.json"))) == 10
    assert len(list((BASE / "chart_semantic").glob("CHART-*.semantic.json"))) == 10
    assert len(list((BASE / "bundles").glob("CHART-*.bundle.json"))) == 10
    assert not list(BASE.glob("CHART-*.json")), "Legacy CHART-*.json files still exist at charts/ root"
    assert not (BASE / "chart_registry.json").exists(), "Legacy chart_registry.json still exists at charts/ root"

    for item in registry:
        chart_id = item["chart_id"]
        assert item["chart_file"] == f"chart_repr/{chart_id}.json"
        assert item["semantic_file"] == f"chart_semantic/{chart_id}.semantic.json"
        assert item["bundle_file"] == f"bundles/{chart_id}.bundle.json"

        chart_repr = load_json(BASE / item["chart_file"])
        chart_semantic = load_json(BASE / item["semantic_file"])
        bundle = load_json(BASE / item["bundle_file"])

        assert chart_repr["schema_role"] == "chart_repr", chart_id
        assert chart_semantic["schema_role"] == "chart_semantic", chart_id
        assert bundle["chart_id"] == chart_id
        assert bundle["birth_info"] == item["birth_info"]
        assert bundle["chart_repr"] == chart_repr
        assert bundle["chart_semantic"] == chart_semantic

    print("OK chart reorg verified: registry=10 repr=10 semantic=10 bundles=10")


if __name__ == "__main__":
    main()