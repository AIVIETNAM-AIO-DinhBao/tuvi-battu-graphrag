from pathlib import Path

REPLACEMENTS = {
    'TVGM': 'Tử Vi Giảng Minh',
    'TVHS': 'Tử Vi Hàm Số',
    'TVKL': 'Tử Vi Khảo Luận',
    'TVNL': 'Tử Vi Nghiệm Lý, Lý Mệnh Học',
}

FILES = [
    Path('annotations/answer/final_answers_minimal.jsonl'),
    Path('annotations/answer/final_answers.jsonl'),
    Path('release/tuviqa_v1_release.jsonl'),
]


def replace_in_file(path: Path) -> int:
    text = path.read_text(encoding='utf-8')
    count = 0
    for old, new in REPLACEMENTS.items():
        count += text.count(old)
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')
    return count


def main() -> None:
    for path in FILES:
        if not path.exists():
            print(f'File not found: {path}')
            continue
        replaced = replace_in_file(path)
        print(f'Replaced {replaced} occurrences in {path}')


if __name__ == '__main__':
    main()
