"""Fail-closed audit of the documented RTDL V3.0 release surface."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import rtdsl
from rtdsl.canonical_physical_resolution import current_canonical_provider_registry


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = (
    ROOT / "docs/v3/README.md",
    ROOT / "docs/v3/architecture.md",
    ROOT / "docs/v3/correctness_and_extension.md",
    ROOT / "docs/v3/support_matrix.md",
    ROOT / "docs/v3/release.md",
    ROOT / "docs/v3/release_notes_3_0_0.md",
    ROOT / "tutorials/v3_canonical_lowering.md",
)
PAPER_APPS = (
    "rtnn-paper",
    "raydb-paper",
    "librts-paper",
    "x-hd-paper",
    "rt-dbscan-paper",
    "rayjoin-paper",
    "rt-barneshut-paper",
    "triangle-counting-paper",
    "arkade-paper",
)


def _relative_markdown_links(path: Path) -> tuple[Path, ...]:
    targets: list[Path] = []
    for raw in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        target = raw.split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        targets.append((path.parent / target).resolve())
    return tuple(targets)


def main() -> int:
    checks: dict[str, bool] = {}
    version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    front_page = (ROOT / "README.md").read_text(encoding="utf-8")
    checks["release_version_is_3_0_0"] = (
        version_file == "v3.0.0"
        and rtdsl.__version__ == "3.0.0"
        and 'version = "3.0.0"' in pyproject
        and "RTDL 3.0.0" in front_page
    )
    checks["all_v3_docs_present"] = all(path.is_file() for path in REQUIRED_DOCS)
    links = tuple(target for path in REQUIRED_DOCS for target in _relative_markdown_links(path))
    checks["all_v3_relative_links_resolve"] = all(path.exists() for path in links)
    private_path_markers = ("c:/users/", "c:\\users\\", "/home/")
    checks["v3_docs_have_no_private_absolute_dependency"] = all(
        not any(marker in path.read_text(encoding="utf-8").lower() for marker in private_path_markers)
        for path in REQUIRED_DOCS
    )
    checks["nine_app_directories_present"] = all(
        (ROOT / "Paper-reproduction-apps" / name).is_dir() for name in PAPER_APPS
    )

    registry = current_canonical_provider_registry()
    canonical_pairs = [
        (row.statement_stable_id, row.backend_contract_id)
        for row in registry.bindings
        if not row.compatibility_fallback
    ]
    checks["canonical_binding_pairs_unique"] = len(canonical_pairs) == len(
        set(canonical_pairs)
    )
    checks["standalone_provider_sources_verified"] = bool(
        registry.standalone_providers
    )

    example = ROOT / "examples/current/v3_canonical_mapping.py"
    completed = subprocess.run(
        [sys.executable, str(example)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    checks["tutorial_example_runs"] = completed.returncode == 0
    checks["tutorial_example_resolves_linf_optix"] = (
        "status: RESOLVED" in completed.stdout
        and "metric_knn_linf_filter_refine_3d/optix" in completed.stdout
        and "candidate executed: False" in completed.stdout
        and "behavioral receipt still required: True" in completed.stdout
    )

    result = {
        "schema": "rtdl.v3_release_surface_audit.v2",
        "checks": checks,
        "passed": all(checks.values()),
        "registry": {
            "semantic_statement_count": len(registry.statements),
            "binding_count": len(registry.bindings),
            "standalone_provider_count": len(registry.standalone_providers),
            "registry_sha256": registry.digest,
        },
        "tutorial_stdout": completed.stdout.splitlines(),
        "tutorial_stderr": completed.stderr.splitlines(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
