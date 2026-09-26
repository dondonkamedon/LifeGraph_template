#!/usr/bin/env python3
"""公開ファイルに連絡先や利用者固有のパスが含まれていないか確認する。"""

# 実行例: python3 check_privacy.py

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent
HTML_FILE = "LifeGraph_template.html"
PATTERNS = {
    "メールアドレス": re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    "電話番号": re.compile(r"(?<!\d)0\d{1,4}[-－]?\d{1,4}[-－]?\d{3,4}(?!\d)"),
    "利用者固有のパス": re.compile(
        r"/(?:home|Users)/[^/\s<>\"']+|/mnt/[a-z]/Users/[^/\s<>\"']+|[A-Za-z]:[\\/]Users[\\/][^\\/\s<>\"']+",
        re.IGNORECASE,
    ),
    "社内向けドメイン": re.compile(r"\b[a-z0-9.-]+\.(?:internal|corp|local)\b", re.IGNORECASE),
}


def main():
    problems = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.name == Path(__file__).name:
            continue
        if path.name.startswith(".env") or any(word in path.name.lower() for word in ("secret", "credential", "production")):
            continue
        name = str(path.relative_to(ROOT))
        try:
            data = path.read_bytes()
            if b"\0" in data[:4096]:
                continue
            lines = data.decode("utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            print(f"読み取りに失敗しました: {name}: {exc}", file=sys.stderr)
            return 2
        for number, line in enumerate(lines, 1):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    problems.append(f"{name}:{number}: {label}")

    try:
        html = (ROOT / HTML_FILE).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"読み取りに失敗しました: {HTML_FILE}: {exc}", file=sys.stderr)
        return 2
    if not re.search(r'birthYear:\s*""\s*,\s*rangeStart:', html):
        problems.append("LifeGraph_template.html: 初期の生まれ年が空欄ではありません")

    if problems:
        print("公開前の確認で問題が見つかりました:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print("公開ファイルの連絡先・利用者固有のパス・初期生年を確認しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
