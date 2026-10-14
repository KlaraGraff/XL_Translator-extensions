"""检查扩展列表的条目（PR 的自动检查）。

用法::

    python scripts/check_entries.py --translator <Translator 源码目录> [extensions/<id>.json ...] [--all]

对每个条目：

1. 字段与 schema/entry.schema.json 一致，并按 Translator 自己的规则校验（``core.adapter_registry.RegistryEntry``）；
   文件名是 ``<id>.json``；``official`` 只用于 Translator 项目自己维护的扩展；
2. 从 ``download`` 的每个地址下载 zip，大小和 SHA-256 须与条目一致；
3. 用 Translator 的 ``python -m cli adapter test <zip>`` 做与安装时相同的检查，并在 ``samples/`` 上试运行；
   扩展包的 id、版本和扩展名须与条目一致。

没有给条目也没有 ``--all`` 时什么都不做。全部通过时退出码为 0。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_OWNER = "https://github.com/KlaraGraff/"
_TIMEOUT = 60


def _download(url: str, limit: int) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "XL_Translator-extensions-check"})
    with urllib.request.urlopen(request, timeout=_TIMEOUT) as response:  # noqa: S310 - https only, checked by the schema
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"超过条目写的大小 {limit} 字节")
    return data


def check(path: Path, translator: Path, schema_keys: set[str]) -> list[str]:
    from core.adapter_registry import RegistryEntry  # noqa: PLC0415 - from the Translator checkout

    problems: list[str] = []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"无法读取：{exc}"]
    if not isinstance(raw, dict):
        return ["条目须是一个 JSON 对象"]
    unknown = sorted(set(raw) - schema_keys)
    if unknown:
        problems.append(f"schema 里没有这些字段：{', '.join(unknown)}")
    if raw.get("id") != path.stem:
        problems.append(f"文件名须是 <id>.json（id 是 {raw.get('id')!r}）")
    try:
        entry = RegistryEntry.model_validate(raw)
    except Exception as exc:  # noqa: BLE001 - pydantic's ValidationError, printed as is
        return [*problems, f"条目不合规：{exc}"]
    official = entry.status == "official"
    if official and not entry.repo.startswith(OFFICIAL_OWNER):
        problems.append("official 只用于 Translator 项目自己维护的扩展")

    payloads = []
    for url in entry.download:
        try:
            data = _download(url, entry.size)
        except Exception as exc:  # noqa: BLE001 - every network failure is one line
            problems.append(f"无法下载 {url}：{exc}")
            continue
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != entry.size or digest != entry.sha256:
            problems.append(f"{url}：大小或 SHA-256 与条目不一致（{len(data)} 字节，{digest}）")
            continue
        payloads.append(data)
    if not payloads:
        return problems

    with tempfile.TemporaryDirectory(prefix="extension-check-") as work:
        archive = Path(work) / f"{entry.id}-{entry.version}.zip"
        archive.write_bytes(payloads[0])
        command = [sys.executable, "-m", "cli", "adapter", "test", str(archive), "--json"]
        if official:
            command.append("--skip-id-check")
        result = subprocess.run(command, cwd=translator, capture_output=True, text=True, encoding="utf-8", check=False)
    try:
        report = json.loads(result.stdout)
    except ValueError:
        return [*problems, f"adapter test 没有给出结果（退出码 {result.returncode}）：{result.stderr.strip()[-2000:]}"]
    for run in report.get("runs") or ():
        modes = "、".join(f"{mode} {state}" for mode, state in (run.get("modes") or {}).items())
        print(f"  {run.get('file')}：{run.get('units')} 段，{modes}，{run.get('seconds')} 秒")
    for warning in report.get("warnings") or ():
        print(f"  提醒：{warning}")
    problems.extend(f"adapter test：{problem}" for problem in report.get("problems") or ())
    if report.get("id") and report["id"] != entry.id:
        problems.append(f"扩展包的 id 是 {report['id']}，条目写的是 {entry.id}")
    if report.get("version") and report["version"] != entry.version:
        problems.append(f"扩展包的版本是 {report['version']}，条目写的是 {entry.version}")
    if report.get("extensions") and sorted(report["extensions"]) != sorted(entry.extensions):
        problems.append(f"扩展包处理 {report['extensions']}，条目写的是 {entry.extensions}")
    if result.returncode != 0 and not problems:
        problems.append(f"adapter test 未通过（退出码 {result.returncode}）")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="检查扩展列表的条目")
    parser.add_argument("entries", nargs="*", help="要检查的条目文件")
    parser.add_argument("--translator", required=True, help="Translator 源码目录（已安装 requirements.txt）")
    parser.add_argument("--all", action="store_true", help="检查 extensions/ 下的全部条目")
    args = parser.parse_args()
    translator = Path(args.translator).resolve()
    sys.path.insert(0, str(translator))
    schema = json.loads((ROOT / "schema" / "entry.schema.json").read_text(encoding="utf-8"))
    paths = sorted((ROOT / "extensions").glob("*.json")) if args.all else [Path(item) for item in args.entries]
    if not paths:
        print("没有要检查的条目。")
        return 0
    failed = 0
    for path in paths:
        print(f"{path.name}")
        problems = check(path, translator, set(schema["properties"]))
        for problem in problems:
            print(f"  问题：{problem}")
        print("  通过" if not problems else "  未通过")
        failed += bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
