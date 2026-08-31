"""Build the deterministic Goal5793 X1 retrospective S0 reproduction capsule."""

from __future__ import annotations

import argparse
import gzip
import io
import json
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

try:
    import goal5793_x1_canonical as canonical
    import goal5793_x1_verify_s0_reproduction_capsule as verifier
except ModuleNotFoundError:
    from scripts import goal5793_x1_canonical as canonical  # type: ignore
    from scripts import goal5793_x1_verify_s0_reproduction_capsule as verifier  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-22"
ARCHIVE_NAME = "goal5793_x1_s0_reproduction_capsule_20260822.tar.gz"
TWIN_NAME = "goal5793_x1_s0_reproduction_capsule_twin_20260822.tar.gz"
MANIFEST_NAME = "goal5793_x1_s0_reproduction_capsule_manifest_20260822.json"
AUDIT_NAME = "goal5793_x1_s0_reproduction_capsule_audit_20260822.json"

V26 = ROOT / "history/internal_docs/goal5791_portable_source_v26_20260820.tar.gz"
SOURCE = ROOT / "history/internal_docs/goal5793_s0_source_and_admission_freeze_20260822.json"

S0_NAMES = [
    verifier.SOURCE_NAME,
    verifier.CANDIDATE_NAME,
    verifier.PROTOCOL_NAME,
    verifier.REPORT_NAME,
    verifier.SELF_REVIEW_NAME,
    verifier.RESULT_NAME,
    verifier.INDEPENDENT_AUDIT_NAME,
    verifier.CFR_NAME,
    verifier.REVIEW_NAME,
    verifier.RECEIPT_NAME,
    verifier.ABSORPTION_NAME,
    verifier.CLOSURE_NAME,
]

PREDECESSOR_NAMES = [
    "goal5753_held_out_candidate_universe_20260811.json",
    "goal5753_core_freeze_and_selection_protocol_20260811.json",
    "goal5789_a2_postreview_closure_and_goal5793_s0_entry_20260822.json",
]

AUTHORING_TOOL_NAMES = [
    "scripts/goal5793_build_s0_preregistration.py",
    "scripts/goal5793_audit_s0_preregistration.py",
    "tests/goal5793_s0_preregistration_test.py",
]

HISTORICAL_ROOTS = [
    (
        "89079f4c0d60b8a8517b8b302170868de1e3e4a7",
        "docs/reports/goal519_rt_workload_universe_from_2603_28771_2026-04-17.md",
        verifier.GOAL519_BLOB_PATH,
    ),
    (
        "ccd86697daa54467ab256aeba49798bf9ee06d64",
        "docs/reports/goal521_v0_8_workload_scope_decision_matrix_2026-04-17.md",
        verifier.GOAL521_BLOB_PATH,
    ),
]


def _git_blob(commit: str, path: str) -> bytes:
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git is required only while building the capsule")
    return subprocess.check_output([git, "show", f"{commit}:{path}"], cwd=ROOT)


def _json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def _payloads() -> tuple[dict[str, bytes], dict[str, str]]:
    payloads: dict[str, bytes] = {}
    roles: dict[str, str] = {}

    def add(rel: str, data: bytes, role: str) -> None:
        path = PurePosixPath(rel)
        if path.as_posix() != rel or path.is_absolute() or ".." in path.parts or rel in payloads:
            raise RuntimeError(f"invalid/duplicate payload path: {rel}")
        payloads[rel] = data
        roles[rel] = role

    add(verifier.V26_PATH, V26.read_bytes(), "V26_EXACT_SOURCE_ARCHIVE")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = {
        row["path"]: row
        for row in source["declared_product_native_source_zero_drift_authority"]["rows"]
    }
    for name, rel in (
        ("VERSION", verifier.DELTA_VERSION_PATH),
        ("requirements.txt", verifier.DELTA_REQUIREMENTS_PATH),
    ):
        data = (ROOT / name).read_bytes()
        row = rows[name]
        if len(data) != row["size_bytes"] or canonical.sha256_bytes(data) != row["sha256"]:
            raise RuntimeError(f"current source delta differs from S0 authority: {name}")
        add(rel, data, "CURRENT_SOURCE_DELTA")
    for commit, repository_path, rel in HISTORICAL_ROOTS:
        add(rel, _git_blob(commit, repository_path), "PINNED_HISTORICAL_GIT_BLOB")
    docs = ROOT / "history/internal_docs"
    for name in S0_NAMES:
        role = "S0_ROOT"
        if name == verifier.CFR_NAME:
            role = "S0_SINGLE_CFR"
        elif name == verifier.REVIEW_NAME:
            role = "S0_RETURNED_REVIEW"
        elif name == verifier.RECEIPT_NAME:
            role = "S0_OWNER_SEND_RECEIPT"
        elif name == verifier.ABSORPTION_NAME:
            role = "S0_OWNER_ABSORPTION"
        elif name == verifier.CLOSURE_NAME:
            role = "S0_POSTREVIEW_CLOSURE"
        add(f"payload/s0/{name}", (docs / name).read_bytes(), role)
    for name in PREDECESSOR_NAMES:
        add(f"payload/predecessors/{name}", (docs / name).read_bytes(), "S0_PREDECESSOR_AUTHORITY")
    for repository_path in AUTHORING_TOOL_NAMES:
        add(
            f"payload/authoring_tools/{PurePosixPath(repository_path).name}",
            (ROOT / repository_path).read_bytes(),
            "S0_FROZEN_AUTHORING_TOOL",
        )
    add(
        "tools/goal5793_x1_canonical.py",
        (ROOT / "scripts/goal5793_x1_canonical.py").read_bytes(),
        "X1_CANONICAL_HELPER",
    )
    add(
        "tools/goal5793_x1_verify_s0_reproduction_capsule.py",
        (ROOT / "scripts/goal5793_x1_verify_s0_reproduction_capsule.py").read_bytes(),
        "STANDALONE_CAPSULE_VERIFIER",
    )
    return payloads, roles


def _manifest(payloads: dict[str, bytes], roles: dict[str, str]) -> dict[str, Any]:
    rows = [
        {
            "path": rel,
            "bytes": len(payloads[rel]),
            "sha256": canonical.sha256_bytes(payloads[rel]),
            "role": roles[rel],
        }
        for rel in sorted(payloads, key=lambda item: item.encode("utf-8"))
    ]
    document: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.s0_reproduction_capsule.manifest.v1",
        "goal": 5793,
        "stage": "X1_S0_REPRODUCTION_CAPSULE",
        "date": DATE,
        "status": "DETERMINISTIC_SELF_CONTAINED_RETROSPECTIVE_S0_REPRODUCTION_CAPSULE",
        "canonicalization": canonical.CANONICALIZATION_NAME,
        "payloads": rows,
        "payload_summary": {
            "file_count": len(rows),
            "total_bytes": sum(row["bytes"] for row in rows),
            "rows_sha256": canonical.sha256_bytes(canonical.canonical_json_bytes(rows)),
        },
        "hostile_fail_ids": verifier.HOSTILE_IDS,
        "historical_boundary": {
            "original_s0_send_included_this_capsule": False,
            "reviewed_s0_bytes_modified": False,
            "retrospective_x1_reviewability_repair": True,
        },
    }
    document["manifest_sha256"] = canonical.seal_document(
        document,
        seal_field="manifest_sha256",
        domain=verifier.MANIFEST_DOMAIN,
        version=1,
    )
    return document


def _materialize_for_audit(
    root: Path, payloads: dict[str, bytes], manifest_bytes: bytes
) -> dict[str, Any]:
    for rel, data in payloads.items():
        path = root.joinpath(*PurePosixPath(rel).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (root / "manifest.json").write_bytes(manifest_bytes)
    # The manifest verifier expects the control filename to exist while it
    # rehashes the payload set; a placeholder is never read in this phase.
    (root / "audit.json").write_bytes(b"{}\n")
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    return verifier.recompute_audit(root, manifest)


def _archive_bytes(files: dict[str, bytes]) -> bytes:
    raw = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
            for rel in sorted(files, key=lambda item: item.encode("utf-8")):
                name = f"{verifier.CAPSULE_DIRNAME}/{rel}"
                data = files[rel]
                info = tarfile.TarInfo(name=name)
                info.size = len(data)
                info.mode = 0o644
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                info.mtime = 0
                archive.addfile(info, io.BytesIO(data))
    return raw.getvalue()


def build_outputs() -> dict[str, bytes]:
    payloads, roles = _payloads()
    manifest = _manifest(payloads, roles)
    manifest_bytes = _json_bytes(manifest)
    with tempfile.TemporaryDirectory(prefix="goal5793_x1_capsule_build_") as temp:
        audit = _materialize_for_audit(Path(temp), payloads, manifest_bytes)
    audit_bytes = _json_bytes(audit)
    archive_files = dict(payloads)
    archive_files["manifest.json"] = manifest_bytes
    archive_files["audit.json"] = audit_bytes
    archive = _archive_bytes(archive_files)
    return {
        ARCHIVE_NAME: archive,
        TWIN_NAME: archive,
        MANIFEST_NAME: manifest_bytes,
        AUDIT_NAME: audit_bytes,
    }


def output_summary(outputs: dict[str, bytes]) -> dict[str, Any]:
    return {
        "status": "DRY_RUN_PASS",
        "outputs": [
            {
                "path": name,
                "bytes": len(outputs[name]),
                "sha256": canonical.sha256_bytes(outputs[name]),
            }
            for name in (ARCHIVE_NAME, TWIN_NAME, MANIFEST_NAME, AUDIT_NAME)
        ],
        "archive_twin_byte_identical": outputs[ARCHIVE_NAME] == outputs[TWIN_NAME],
    }


def write_create_only(output_dir: Path, outputs: dict[str, bytes]) -> None:
    output_dir = output_dir.resolve()
    paths = [output_dir / name for name in outputs]
    existing = [path for path in paths if path.exists() or path.is_symlink()]
    if existing:
        raise FileExistsError("create-only output exists: " + ", ".join(str(path) for path in existing))
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (output_dir / name).write_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--create-only", action="store_true")
    args = parser.parse_args()
    if (args.output_dir is None) != (not args.create_only):
        parser.error("formal writes require both --output-dir and --create-only; omit both for dry-run")
    outputs = build_outputs()
    summary = output_summary(outputs)
    if args.output_dir is not None:
        write_create_only(args.output_dir, outputs)
        summary["status"] = "CREATE_ONLY_WRITE_PASS"
        summary["output_dir"] = str(args.output_dir.resolve())
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
