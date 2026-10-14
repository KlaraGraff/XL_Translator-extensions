"""从 extensions/*.json 生成 index.json（Translator「浏览扩展」读的就是它）。

用法：python scripts/build_index.py [--check]

``--check`` 只核对 index.json 是否与条目一致，不一致时退出码为 1。只用 Python 标准库；
条目的完整检查在 scripts/check_entries.py。输出不带时间戳：条目不变，index.json 就不变。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_SCHEMA = 1


def build() -> str:
    entries = []
    for path in sorted((ROOT / "extensions").glob("*.json")):
        entry = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(entry, dict) or entry.get("id") != path.stem:
            raise SystemExit(f"{path.name}：文件名须是 <id>.json，与条目的 id 一致")
        entries.append(entry)
    entries.sort(key=lambda entry: (entry.get("status") != "official", entry["id"]))
    return json.dumps({"schema": INDEX_SCHEMA, "extensions": entries}, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="只核对，不写入")
    args = parser.parse_args()
    text = build()
    index = ROOT / "index.json"
    if args.check:
        current = index.read_text(encoding="utf-8") if index.exists() else ""
        if current != text:
            print("index.json 与 extensions/ 不一致，请运行 python scripts/build_index.py", file=sys.stderr)
            return 1
        return 0
    index.write_text(text, encoding="utf-8")
    print(f"index.json：{len(json.loads(text)['extensions'])} 个扩展")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
