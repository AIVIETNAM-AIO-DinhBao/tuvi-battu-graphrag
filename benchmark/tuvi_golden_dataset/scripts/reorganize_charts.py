import json
import re
import shutil
import unicodedata
from pathlib import Path


BASE = Path(__file__).resolve().parents[1] / "charts"
REG_SRC = BASE / "chart_registry.json"
REG_DST = BASE / "registry" / "chart_registry.json"
EXPORTS = BASE / "exports"

TARGET_DIRS = {
    "registry": BASE / "registry",
    "chart_repr": BASE / "chart_repr",
    "chart_semantic": BASE / "chart_semantic",
    "bundles": BASE / "bundles",
}


def slugify_vn(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    ascii_text = ascii_text.replace("đ", "d").replace("Đ", "D")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> None:
    for target_dir in TARGET_DIRS.values():
        target_dir.mkdir(parents=True, exist_ok=True)

    registry_path = REG_SRC if REG_SRC.exists() else REG_DST
    if not registry_path.exists():
        raise FileNotFoundError(f"Cannot find chart registry at {REG_SRC} or {REG_DST}")

    registry = load_json(registry_path)
    updated_registry = []
    missing = []

    for item in registry:
        chart_id = item["chart_id"]
        birth_info = item["birth_info"]

        old_repr = BASE / f"{chart_id}.json"
        new_repr = TARGET_DIRS["chart_repr"] / f"{chart_id}.json"

        if old_repr.exists() and not new_repr.exists():
            shutil.move(str(old_repr), str(new_repr))
        elif old_repr.exists() and new_repr.exists():
            old_repr.unlink()

        if not new_repr.exists():
            missing.append(str(new_repr))
            continue

        stem = (
            f"{slugify_vn(birth_info['name'])}-"
            f"{birth_info['birth_date']}-"
            f"{birth_info['birth_time'].replace(':', '-')}"
        )
        exported_semantic = EXPORTS / f"{stem}__chart_semantic.json"
        new_semantic = TARGET_DIRS["chart_semantic"] / f"{chart_id}.semantic.json"

        if exported_semantic.exists():
            shutil.copy2(str(exported_semantic), str(new_semantic))
        elif not new_semantic.exists():
            missing.append(str(exported_semantic))
            continue

        chart_repr = load_json(new_repr)
        chart_semantic = load_json(new_semantic)

        if chart_repr.get("schema_role") != "chart_repr":
            raise ValueError(f"{new_repr} is not chart_repr")
        if chart_semantic.get("schema_role") != "chart_semantic":
            raise ValueError(f"{new_semantic} is not chart_semantic")

        bundle = {
            "chart_id": chart_id,
            "birth_info": birth_info,
            "chart_repr": chart_repr,
            "chart_semantic": chart_semantic,
        }
        dump_json(TARGET_DIRS["bundles"] / f"{chart_id}.bundle.json", bundle)

        updated_item = dict(item)
        updated_item["chart_file"] = f"chart_repr/{chart_id}.json"
        updated_item["semantic_file"] = f"chart_semantic/{chart_id}.semantic.json"
        updated_item["bundle_file"] = f"bundles/{chart_id}.bundle.json"
        updated_registry.append(updated_item)

    if missing:
        raise FileNotFoundError("Missing required chart files:\n" + "\n".join(missing))

    if REG_SRC.exists() and REG_SRC != REG_DST:
        shutil.move(str(REG_SRC), str(REG_DST))

    dump_json(REG_DST, updated_registry)
    print(f"Reorganized {len(updated_registry)} charts into registry/chart_repr/chart_semantic/bundles")


if __name__ == "__main__":
    main()