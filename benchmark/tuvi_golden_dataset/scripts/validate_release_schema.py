import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def read_json(path: Path) -> Dict[str, Any]:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def expect_type(value: Any, expected: str) -> bool:
    if expected == 'string':
        return isinstance(value, str)
    if expected == 'integer':
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == 'array':
        return isinstance(value, list)
    if expected == 'object':
        return isinstance(value, dict)
    return False


def validate_record(record: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required = schema.get('required', [])
    properties = schema.get('properties', {})

    for key in required:
        if key not in record:
            errors.append(f"missing required field '{key}'")

    for key, value in record.items():
        prop = properties.get(key)
        if not prop:
            continue
        expected_type = prop.get('type')
        if expected_type and not expect_type(value, expected_type):
            errors.append(f"field '{key}' expected type {expected_type} but got {type(value).__name__}")
            continue

        if key == 'question_complexity':
            enum = prop.get('enum', [])
            if value not in enum:
                errors.append(f"invalid question_complexity '{value}', must be one of {enum}")

        if key == 'birth_info' and isinstance(value, dict):
            birth_props = prop.get('properties', {})
            for child_key, child_prop in birth_props.items():
                if child_key not in value:
                    errors.append(f"birth_info missing '{child_key}'")
                elif not expect_type(value[child_key], child_prop.get('type', '')):
                    errors.append(f"birth_info.{child_key} expected type {child_prop.get('type')} but got {type(value[child_key]).__name__}")

        if key == 'gold_context_spans' and isinstance(value, list):
            item_props = prop.get('items', {}).get('properties', {})
            for index, item in enumerate(value):
                if not isinstance(item, dict):
                    errors.append(f"gold_context_spans[{index}] must be object")
                    continue
                for sub_key, sub_val in item.items():
                    sub_prop = item_props.get(sub_key)
                    if not sub_prop:
                        continue
                    if not expect_type(sub_val, sub_prop.get('type', '')):
                        errors.append(f"gold_context_spans[{index}].{sub_key} expected type {sub_prop.get('type')} but got {type(sub_val).__name__}")

        if key in {'gold_chunk_ids', 'required_entities'} and isinstance(value, list):
            item_type = prop.get('items', {}).get('type')
            for index, item in enumerate(value):
                if not expect_type(item, item_type):
                    errors.append(f"{key}[{index}] expected type {item_type} but got {type(item).__name__}")

    return errors


def audit_dataset_rules(records: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    ids = [rec.get('id') for rec in records]
    if len(ids) != len(set(ids)):
        duplicates = [item for item in set(ids) if ids.count(item) > 1]
        errors.append(f"duplicate ids found: {sorted(duplicates)}")

    if len(records) != 100:
        errors.append(f"expected 100 records but found {len(records)}")

    complexity_counts = {'Direct': 0, 'One-hop': 0, 'Two-hop': 0}
    for rec in records:
        complexity = rec.get('question_complexity')
        if complexity in complexity_counts:
            complexity_counts[complexity] += 1
        spans = rec.get('gold_context_spans', []) or []
        if complexity == 'Direct' and spans:
            errors.append(f"Direct sample '{rec.get('id')}' must have empty gold_context_spans")

    if complexity_counts['Direct'] != 10:
        errors.append(f"expected 10 Direct records but found {complexity_counts['Direct']}")
    if complexity_counts['One-hop'] != 40:
        errors.append(f"expected 40 One-hop records but found {complexity_counts['One-hop']}")
    if complexity_counts['Two-hop'] != 50:
        errors.append(f"expected 50 Two-hop records but found {complexity_counts['Two-hop']}")

    return errors


def validate_against_schema(data_file: Path, schema_file: Path) -> bool:
    schema = read_json(schema_file)
    records = read_jsonl(data_file)
    errors = []
    for index, record in enumerate(records, start=1):
        record_errors = validate_record(record, schema)
        if record_errors:
            for error in record_errors:
                errors.append(f"row {index} id={record.get('id')} {error}")
    if errors:
        print('Schema validation errors:')
        for error in errors:
            print(f"- {error}")
        return False
    return True


def audit_dataset_rules_main(data_file: Path) -> dict:
    records = read_jsonl(data_file)
    issues = audit_dataset_rules(records)
    return {'valid': len(issues) == 0, 'issues': issues}


if __name__ == '__main__':
    schema_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'guideline' / 'schema_release.json'
    data_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / 'release' / 'golden_v1_release.jsonl'

    if not schema_path.exists():
        print(f"Schema file not found: {schema_path}")
        sys.exit(1)
    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        sys.exit(1)

    valid_schema = validate_against_schema(data_path, schema_path)
    audit = audit_dataset_rules_main(data_path)

    if not valid_schema:
        print('Validation FAILED')
        sys.exit(1)

    if not audit['valid']:
        print('Dataset audit FAILED')
        for issue in audit['issues']:
            print(f"- {issue}")
        sys.exit(1)

    print(f"Validation PASSED: {len(read_jsonl(data_path))} records conform to schema and audit rules")
    sys.exit(0)
