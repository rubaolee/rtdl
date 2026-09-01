#!/usr/bin/env python3
"""Build one deterministic, self-contained Goal5836 Mac continuation capsule."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile


PREFIX = PurePosixPath("rtdl_goal5836_macbook_handoff")
SOURCE_SUFFIXES = {
    ".c", ".cc", ".cpp", ".cu", ".h", ".hpp", ".json", ".md", ".mm",
    ".ps1", ".py", ".sh", ".toml", ".txt",
}
ROOT_FILES = {
    ".gitattributes", ".gitignore", "AGENTS.md", "LICENSE", "README.md",
    "pyproject.toml", "requirements.txt",
}
HANDOFF = Path(
    "history/internal_docs/handoff_macbook_pre_goal5836_cgo_checkpoint_20260831.md"
)
CURRENT_PAPER_FILES = {
    "paper/cgo2027/README.md",
    "paper/cgo2027/anonymization_gate.md",
    "paper/cgo2027/anonymization_gate_final_20260829.md",
    "paper/cgo2027/main.pdf",
    "paper/cgo2027/main.tex",
    "paper/cgo2027/references.bib",
}
CONTEXT_DOC_NAMES = {
    "call_for_review_goal5794_callback_protocol_ir_pyoptix_and_related_work_strategy_20260823.md",
    "cgo_related_work_taxonomy_owl_and_repurposed_landscape_revision_report_20260829.md",
    "goal5794_cgo_callback_protocol_ir_strategy_summary_20260823.md",
    "goal5794_to_goal5799_cgo_execution_plan_v2_owl_aware_20260823.md",
    "goal5804_cgo_three_questions_two_concerns_and_goals5801_5804_strategy_20260824.md",
    "goal5815_cgo_manuscript_claim_spine_20260829.md",
    "goal5821_cgo_claim_branch_skeleton_20260829.md",
    "review_goal5794_callback_protocol_ir_pyoptix_and_related_work_strategy_20260823.md",
    "reviewer_guidance_path_to_strong_accept_20260829.md",
    "reviewer_guidance_twelve_day_submission_plan_20260829.md",
    "self_review_pre_goal5836_macbook_handoff_a1_20260831.md",
    "goal5836_sui_same_input_preaction_authority_20260901.json",
    "goal5836_sui_same_input_preaction_technical_plan_20260901.md",
    "goal5836_a0_owner_authorization_20260901.md",
    "goal5836_a0_source_acquisition_technical_report_20260901.md",
    "self_review_goal5836_a0_source_acquisition_20260901.md",
}
EVIDENCE_DIRECTORIES = {
    "goal5833_builtin_sphere_home_evidence_20260830",
    "goal5834_b1_fixture_preaction_20260830",
    "goal5834_b1_home_failure_20260830",
    "goal5834_b1_source_projection_20260830",
    "goal5834_b2_home_failure_20260830",
    "goal5834_b2_source_projection_20260830",
    "goal5834_b3_home_result_20260830",
    "goal5834_b3_source_projection_20260830",
    "goal5834_final_adversarial_self_review_20260830",
    "goal5836_a0_source_acquisition_20260901",
}
VERIFY_SOURCE = r'''#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "CAPSULE_MANIFEST.json").read_text(encoding="utf-8"))
expected = manifest["payloads"]
optional_outer_capsule = {
    "history/internal_docs/goal5836_macbook_complete_handoff_capsule_20260831.tar.gz"
}


def is_environment_artifact(path: Path) -> bool:
    relative = path.relative_to(root)
    return (
        relative.parts[0] in {".git", ".venv-goal5836"}
        or "__pycache__" in relative.parts
        or ".pytest_cache" in relative.parts
        or any(part.endswith(".egg-info") for part in relative.parts)
        or path.name == ".DS_Store"
        or path.suffix in {".pyc", ".pyo"}
    )


actual_paths = {
    p.relative_to(root).as_posix() for p in root.rglob("*")
    if p.is_file()
    and p.name != "CAPSULE_MANIFEST.json"
    and not is_environment_artifact(p)
}
expected_paths = {row["path"] for row in expected}
if actual_paths - optional_outer_capsule != expected_paths:
    missing = sorted(expected_paths - actual_paths)
    extra = sorted(actual_paths - expected_paths - optional_outer_capsule)
    raise SystemExit(f"path-set mismatch missing={missing} extra={extra}")
for row in expected:
    path = root / row["path"]
    data = path.read_bytes()
    observed = hashlib.sha256(data).hexdigest()
    if len(data) != row["bytes"] or observed != row["sha256"]:
        raise SystemExit(f"payload mismatch: {row['path']}")
print(json.dumps({
    "status": "PASS__GOAL5836_MACBOOK_CAPSULE",
    "payload_count": len(expected),
    "payload_bytes": sum(row["bytes"] for row in expected),
}, sort_keys=True))
'''


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_source(path: Path) -> bool:
    return (
        path.is_file()
        and "__pycache__" not in path.parts
        and not any(part.endswith(".egg-info") for part in path.parts)
        and path.suffix.lower() in SOURCE_SUFFIXES
        and path.suffix.lower() not in {".pyc", ".pyo", ".nbi", ".nbc"}
    )


def _collect(repo: Path) -> dict[str, bytes]:
    selected: set[Path] = set()

    for name in ROOT_FILES:
        path = repo / name
        if path.is_file():
            selected.add(path)

    for directory in (
        "src", "scripts", "experiments", "examples", "tests", "memory",
    ):
        root = repo / directory
        if root.is_dir():
            selected.update(path for path in root.rglob("*") if _safe_source(path))

    for directory in ("case_studies/sui_derived_edge_crossing_core",):
        root = repo / directory
        selected.update(path for path in root.rglob("*") if _safe_source(path))

    for rel in CURRENT_PAPER_FILES:
        path = repo / rel
        if path.is_file():
            selected.add(path)

    internal = repo / "history/internal_docs"
    for path in internal.iterdir():
        if not path.is_file():
            continue
        name = path.name
        if (
            re.search(r"(?:goal|review_goal|self_review_goal)583[0-5]", name)
            or name in CONTEXT_DOC_NAMES
            or path == repo / HANDOFF
        ):
            selected.add(path)

    for directory in internal.iterdir():
        if not directory.is_dir() or directory.name not in EVIDENCE_DIRECTORIES:
            continue
        selected.update(path for path in directory.rglob("*") if path.is_file())

    payloads: dict[str, bytes] = {}
    for path in sorted(selected, key=lambda item: item.relative_to(repo).as_posix()):
        relative = path.relative_to(repo).as_posix()
        payloads[relative] = path.read_bytes()

    handoff_bytes = (repo / HANDOFF).read_bytes()
    payloads["START_HERE.md"] = handoff_bytes
    payloads["VERIFY_CAPSULE.py"] = VERIFY_SOURCE.encode("utf-8")
    return dict(sorted(payloads.items()))


def _tar_info(name: PurePosixPath, data: bytes) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name.as_posix())
    info.size = len(data)
    info.mode = 0o444
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = 0
    info.type = tarfile.REGTYPE
    return info


def build(repo: Path, output: Path) -> dict[str, object]:
    repo = repo.resolve(strict=True)
    payloads = _collect(repo)
    rows = [
        {"path": path, "bytes": len(data), "sha256": _sha(data)}
        for path, data in payloads.items()
    ]
    manifest = {
        "schema": "rtdl.goal5836.macbook_complete_handoff_capsule.v1",
        "status": "PRE_GOAL5836__NO_EXECUTION_AUTHORIZED",
        "entrypoint": "START_HERE.md",
        "verify_command": "python3 VERIFY_CAPSULE.py",
        "goal5836_authorized": False,
        "pod_authorized": False,
        "performance_authorized": False,
        "external_review_authorized": False,
        "payload_count": len(rows),
        "payload_bytes": sum(row["bytes"] for row in rows),
        "payloads": rows,
    }
    manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")

    output.parent.mkdir(parents=True, exist_ok=True)
    raw_tar = io.BytesIO()
    with tarfile.open(fileobj=raw_tar, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for path, data in payloads.items():
            info = _tar_info(PREFIX / PurePosixPath(path), data)
            tf.addfile(info, io.BytesIO(data))
        info = _tar_info(PREFIX / "CAPSULE_MANIFEST.json", manifest_bytes)
        tf.addfile(info, io.BytesIO(manifest_bytes))
    with output.open("wb") as target:
        with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as gz:
            gz.write(raw_tar.getvalue())

    data = output.read_bytes()
    return {
        "status": "PASS__BUILT_GOAL5836_MACBOOK_COMPLETE_HANDOFF_CAPSULE",
        "output": str(output),
        "bytes": len(data),
        "sha256": _sha(data),
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.repo, args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
