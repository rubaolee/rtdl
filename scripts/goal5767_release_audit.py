#!/usr/bin/env python3
"""Independent static/usability audit for the Goal5767 V4 research RC."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    "README.md",
    "docs/v4/README.md",
    "docs/v4/tutorial.md",
    "docs/v4/api_reference.md",
    "docs/v4/security_model.md",
    "docs/v4/nine_app_coverage.md",
    "docs/v4/migration_from_v3.md",
)
APP_TOKENS = re.compile(
    r"\b(rtnn|raydb|librts|x_hd|xhd|rt_dbscan|dbscan|rayjoin|barneshut|arkade|"
    r"triangle_counting|particle_tracking|paper|publication|application_id|app_id)\b",
    re.IGNORECASE,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _doc_links() -> list[dict[str, object]]:
    rows = []
    for name in DOCS:
        path = ROOT / name
        if not path.is_file():
            raise RuntimeError(f"missing documentation: {name}")
        text = path.read_text(encoding="utf-8")
        missing = []
        for link in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            if "://" in link or link.startswith("#"):
                continue
            target = (path.parent / link.split("#", 1)[0]).resolve()
            if not target.exists():
                missing.append(link)
        if missing:
            raise RuntimeError(f"broken documentation links in {name}: {missing}")
        rows.append({"path": name, "sha256": _sha(path), "local_links_missing": 0})
    return rows


def _dispatch_audit() -> list[dict[str, object]]:
    rows = []
    for path in sorted((ROOT / "src/rtdsl").glob("v4*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        hits = []
        for node in ast.walk(tree):
            expression = None
            if isinstance(node, ast.If):
                expression = node.test
            elif isinstance(node, ast.Match):
                expression = node.subject
            if expression is None:
                continue
            text = ast.get_source_segment(source, expression) or ast.dump(expression)
            if APP_TOKENS.search(text):
                hits.append({"line": getattr(node, "lineno", None), "expression": text})
        if hits:
            raise RuntimeError(f"application/publication identity dispatch in {path}: {hits}")
        rows.append({"path": path.relative_to(ROOT).as_posix(), "dispatch_hits": 0})
    return rows


def _public_surface() -> dict[str, object]:
    path = ROOT / "src/rtdsl/v4.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            imported.append(node.module)
    forbidden_modules = [
        name for name in imported
        if name and any(token in name for token in ("runtime", "cache", "composer", "codegen"))
    ]
    if forbidden_modules:
        raise RuntimeError(f"public API exposes backend/runtime modules: {forbidden_modules}")
    return {
        "path": "src/rtdsl/v4.py",
        "sha256": _sha(path),
        "backend_runtime_module_imports": forbidden_modules,
        "arbitrary_provider_escape_present": bool(re.search(
            r"\b(load_user_ptx|register_provider|candidate_override|arbitrary_callback)\b", source
        )),
    }


def _quickstart() -> dict[str, object]:
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    completed = subprocess.run(
        [sys.executable, str(ROOT / "examples/current/v4_restricted_callback_quickstart.py")],
        cwd=ROOT,
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    result = json.loads(completed.stdout)
    if result.get("status") != "verified_cpu_semantics" \
            or result.get("user_source_executed_by_python") is not False \
            or result.get("gpu_execution_claimed") is not False:
        raise RuntimeError(f"quickstart contract mismatch: {result}")
    return result


def main() -> None:
    public = _public_surface()
    if public["arbitrary_provider_escape_present"]:
        raise RuntimeError("public escape hatch detected")
    result = {
        "schema": "rtdl.goal5767.release_audit.v1",
        "goal": 5767,
        "documentation": _doc_links(),
        "v4_module_dispatch_audit": _dispatch_audit(),
        "public_surface": public,
        "quickstart": _quickstart(),
        "version": "4.0.0rc1",
        "performance_claimed": False,
        "pod_used_or_authorized": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
