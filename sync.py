#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一编码规范分发脚本。

唯一权威文件：~/.agent-rules/CODING.md
本脚本把它的正文写进各 Agent 工具的入口文件（托管区块，可反复执行）。

用法：
    python ~/.agent-rules/sync.py            # 分发
    python ~/.agent-rules/sync.py --check    # 只检查是否过期，不写
    python ~/.agent-rules/sync.py --list     # 列出目标路径
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HOME = Path.home()
CANON = HOME / ".agent-rules" / "CODING.md"

BEGIN_TPL = "<!-- agent-rules:begin hash={hash} | 自动生成，勿手改；改 CODING.md 后重跑 sync.py -->"
BEGIN_RE_HEAD = "<!-- agent-rules:begin"
END = "<!-- agent-rules:end -->"

# ---------------------------------------------------------------- 目标定义
# kind: "block" = 整段托管（首次创建时写 header）; "pointer" = 只放一行指针
TARGETS = [
    {
        "name": "Codex",
        "path": HOME / ".codex" / "AGENTS.md",
        "kind": "block",
        "header": (
            "# 全局编码规范（Codex）\n\n"
            "> 本文件由 `~/.agent-rules/sync.py` 从 `~/.agent-rules/CODING.md` 生成。\n"
            "> 改规则请改 CODING.md，不要直接改本文件。\n\n"
        ),
    },
    {
        "name": "Claude Code",
        "path": HOME / ".claude" / "CLAUDE.md",
        "kind": "block",
        "header": (
            "# 全局编码规范（Claude Code）\n\n"
            "> 本文件由 `~/.agent-rules/sync.py` 从 `~/.agent-rules/CODING.md` 生成。\n"
            "> 改规则请改 CODING.md，不要直接改本文件。\n\n"
        ),
    },
    {
        "name": "Cursor",
        "path": HOME / ".cursor" / "rules" / "coding-standard.mdc",
        "kind": "block",
        "header": (
            "---\n"
            "description: 统一编码规范（用户级，始终生效）\n"
            "globs:\n"
            "alwaysApply: true\n"
            "---\n\n"
        ),
    },
    {
        "name": "Trae · 用户记忆",
        "path": HOME / ".trae-cn" / "memory" / "user_profile.md",
        "kind": "pointer",
        "header": "",
    },
    {
        "name": "OpenCode",
        "path": HOME / ".config" / "opencode" / "AGENTS.md",
        "kind": "block",
        "header": (
            "# 全局编码规范（OpenCode）\n\n"
            "> 由 `~/.agent-rules/sync.py` 从 `~/.agent-rules/CODING.md` 生成。\n"
            "> 改规则请改 CODING.md。\n\n"
        ),
    },
    {
        "name": "CodeBuddy CN",
        "path": HOME / ".codebuddy" / "skills" / "coding-standard" / "SKILL.md",
        "kind": "pointer",
        "header": (
            "---\n"
            "name: coding-standard\n"
            "description: 写代码统一规范入口。凡是写代码、改代码、重构、写 SQL、代码审查、安全审查、"
            "运行时排错的任务都加载。规则本体在 ~/.agent-rules/CODING.md。\n"
            "---\n\n"
            "# 写代码规范\n\n"
            f"规则本体不在本文件，在 `{CANON}`。\n\n"
        ),
    },
    {
        "name": "ZCode",
        "path": HOME / ".zcode" / "AGENTS.md",
        "kind": "block",
        "header": (
            "# 全局编码规范（ZCode）\n\n"
            "> 由 `~/.agent-rules/sync.py` 生成。改规则请改 `~/.agent-rules/CODING.md`。\n\n"
        ),
        "note": "未验证该工具是否读取此路径",
    },
    {
        "name": "DeepSeek Harness",
        "path": HOME / ".dsh" / "AGENTS.md",
        "kind": "block",
        "header": (
            "# 全局编码规范（DeepSeek Harness）\n\n"
            "> 由 `~/.agent-rules/sync.py` 生成。改规则请改 `~/.agent-rules/CODING.md`。\n\n"
        ),
        "note": "未验证该工具是否读取此路径",
    },
]


def canon_text() -> str:
    if not CANON.exists():
        sys.exit(f"[错误] 找不到权威文件：{CANON}")
    return CANON.read_text(encoding="utf-8").rstrip() + "\n"


def digest(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:12]


def build_block(text: str) -> str:
    return f"{BEGIN_TPL.format(hash=digest(text))}\n\n{text}\n{END}\n"


def build_pointer(text_hash: str) -> str:
    return (
        f"{BEGIN_TPL.format(hash=text_hash)}\n\n"
        "## 编码规范（写代码前必读）\n\n"
        f"统一编码规范全文：`{CANON}`\n\n"
        "写或改任何代码前，先读该文件；深主题分册在 `~/.agent-rules/references/`。\n"
        "核心：方法 ≤80 行且叙事性、**数据载体与业务逻辑分包（model/）、不建内部类、"
        "协议取值用枚举、常量按职责归位、参数 >3 个建上下文对象、循环外声明只用于复用对象、"
        "集合处理优先 stream**、集合变量带 List/Map 后缀、禁裸 `List<Map>`、跑通才算完不许虚报。\n\n"
        f"{END}\n"
    )


def replace_managed(existing: str, block: str) -> str:
    """把托管区块替换/追加，保留用户的其它内容。"""
    lines = existing.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith(BEGIN_RE_HEAD)), None)
    if start is None:
        sep = "" if existing.endswith("\n\n") or not existing.strip() else (
            "\n" if existing.endswith("\n") else "\n\n"
        )
        return existing + sep + block
    end = next((i for i in range(start, len(lines)) if lines[i].strip() == END), None)
    if end is None:
        return "\n".join(lines[:start]) + block
    before = "\n".join(lines[:start])
    after = "\n".join(lines[end + 1:])
    mid = block.rstrip("\n")
    out = (before + "\n" if before else "") + mid
    if after.strip():
        out += "\n\n" + after.lstrip("\n")
    return out + "\n"


def current_hash(existing: str):
    for ln in existing.splitlines():
        if ln.startswith(BEGIN_RE_HEAD):
            for part in ln.split():
                if part.startswith("hash="):
                    return part[5:].rstrip("|").strip()
    return None


def strip_managed(existing: str) -> str:
    """返回托管区块之外的内容。"""
    lines = existing.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith(BEGIN_RE_HEAD)), None)
    if start is None:
        return existing
    end = next((i for i in range(start, len(lines)) if lines[i].strip() == END), None)
    if end is None:
        return "\n".join(lines[:start])
    return "\n".join(lines[:start] + lines[end + 1:])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只检查是否过期")
    ap.add_argument("--list", action="store_true", help="列出目标路径")
    ap.add_argument("--force", action="store_true",
                    help="强制重写（只改了 build_pointer/build_block 模板、CODING.md 内容未变时用）")
    args = ap.parse_args()

    if args.list:
        print(f"权威文件：{CANON}")
        for t in TARGETS:
            print(f"  {t['name']:<16} {t['path']}")
        return 0

    text = canon_text()
    h = digest(text)
    block = build_block(text)
    pointer = build_pointer(h)

    rows, stale = [], 0
    for t in TARGETS:
        p: Path = t["path"]
        payload = block if t["kind"] == "block" else pointer
        exists = p.exists()
        existing = p.read_text(encoding="utf-8") if exists else ""
        old = current_hash(existing)

        if not exists:
            status = "新建"
        elif old is None:
            status = "追加"
        elif old == h:
            status = "最新"
        else:
            status = "待更新"
            stale += 1

        if not args.check and (old != h or args.force):
            p.parent.mkdir(parents=True, exist_ok=True)
            if not exists or not strip_managed(existing).strip():
                # 文件为空或只有托管区块 → 整体重写（带 header）
                p.write_text(t["header"] + payload, encoding="utf-8", newline="\n")
                status = "新建"
            else:
                p.write_text(replace_managed(existing, payload), encoding="utf-8", newline="\n")
                status = "已写入"
        elif not args.check:
            status = "最新(跳过)"
        rows.append((t["name"], str(p), status, t.get("note", "")))

    print(f"权威文件：{CANON}  hash={h}")
    print("-" * 78)
    width = max(len(r[0]) for r in rows) + 2
    for name, path, status, note in rows:
        tail = f"   ⚠ {note}" if note else ""
        print(f"{name:<{width}} {status:<10} {path}{tail}")
    print("-" * 78)

    if args.check:
        print("✅ 全部最新" if stale == 0 else f"⚠️ {stale} 个目标已过期，跑一次 sync.py")
        return 0 if stale == 0 else 1
    print("✅ 分发完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
