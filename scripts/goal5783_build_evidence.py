"""Build a deterministic reviewer-visible Goal5783 evidence archive."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


PAYLOADS = (
    "history/internal_docs/review_v4_cgo_next_stage_plan_after_goal5776_20260814.md",
    "history/internal_docs/v4_cgo_next_stage_plan_amendment_a1_preregistrations_20260814.json",
    "history/internal_docs/v4_post_goal5779_5781_mandatory_decision_register_20260814.json",
    "history/internal_docs/goal5782_unified_v4_performance_candidate_and_home_closure_result_20260814.json",
    "history/internal_docs/goal5783_postfreeze_held_out_selection_20260814.json",
    "history/internal_docs/goal5783_author_source_pin_20260814.json",
    "history/internal_docs/goal5783_frozen_core_audit_20260814.json",
    "history/internal_docs/goal5783_home_functional_result_20260814/GOAL5783_FUNCTIONAL_RECEIPT.json",
    "history/internal_docs/goal5783_home_functional_result_20260814/PREFINAL_V1_FUNCTIONAL_RECEIPT.json",
    "history/internal_docs/goal5783_home_functional_result_20260814/PREFINAL_V2_FUNCTIONAL_RECEIPT.json",
    "history/internal_docs/goal5783_home_functional_result_20260814/functional_stdout.json",
    "history/internal_docs/goal5783_home_functional_result_20260814/functional_stderr.log",
    "history/internal_docs/goal5783_home_functional_independent_recount_20260814.json",
    "Paper-reproduction-apps/goal5783-held-out-rtxrmq/README.md",
    "Paper-reproduction-apps/goal5783-held-out-rtxrmq/independent_oracle.py",
    "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
    "Paper-reproduction-apps/goal5783-held-out-rtxrmq/run_functional_receipt.py",
    "tests/goal5783_postfreeze_rtxrmq_exam_test.py",
    "scripts/goal5783_audit_frozen_core.py",
    "scripts/goal5783_recount_home_functional.py",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add(handle: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mtime = 0
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mode = 0o644
    handle.addfile(info, io.BytesIO(data))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    rows = []
    blobs = []
    for name in PAYLOADS:
        data = (root / name).read_bytes()
        rows.append({"path": name, "size": len(data), "sha256": sha(data)})
        blobs.append((name, data))
    manifest = {
        "schema": "rtdl.goal5783.evidence_manifest.v1",
        "payload_count": len(rows),
        "payload_bytes": sum(row["size"] for row in rows),
        "payloads": rows,
    }
    manifest_data = (json.dumps(
        manifest, indent=2, sort_keys=True) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w") as handle:
                for name, data in blobs:
                    add(handle, name, data)
                add(handle, "GOAL5783_EVIDENCE_MANIFEST.json", manifest_data)
    print(json.dumps({
        "archive": str(args.output),
        "archive_sha256": sha(args.output.read_bytes()),
        "payload_count": len(rows),
        "payload_bytes": manifest["payload_bytes"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
