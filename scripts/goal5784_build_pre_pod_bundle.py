#!/usr/bin/env python3
"""Build the exact deterministic Goal5784 targeted pre-POD bundle."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "history/internal_docs/goal5782_portable_source_v5_20260814.tar.gz"
PREREGISTRATION = ROOT / "history/internal_docs/goal5784_targeted_modern_rtx_preregistration_20260814.json"
RUNTIME_BUDGET = ROOT / "history/internal_docs/goal5784_targeted_formal_runtime_budget_20260814.json"
EXPECTATION = ROOT / "history/internal_docs/goal5784_pre_registered_expected_value_statement_20260814.md"
HARNESS = (
    "scripts/goal5776_target_prepare.py",
    "scripts/goal5784_mechanism_binding.py",
    "scripts/goal5784_targeted_formal_contract.py",
    "scripts/goal5784_targeted_runtime_inputs.py",
    "scripts/goal5784_targeted_worker.py",
    "scripts/goal5784_targeted_controller.py",
    "scripts/goal5784_targeted_evaluate.py",
    "scripts/goal5784_targeted_recount.py",
    "scripts/goal5784_target_functional_prepare.py",
    "scripts/goal5784_target_prepare.py",
    "tests/goal5784_targeted_pre_pod_test.py",
)
EXPECTED_SOURCE_SHA256 = "3237354adeb10dc42858956fe98d33f3f6f41f241c9739820b84aba64e45ebec"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as out:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith((".py", ".sh")) else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                out.addfile(info, io.BytesIO(data))
    return output.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output, args.twin):
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    source = SOURCE.read_bytes()
    if _sha(source) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("Goal5784 exact Goal5782 source drifted")
    data = args.data_bundle.read_bytes()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        manifest_handle = archive.extractfile("DATA_MANIFEST.json")
        if manifest_handle is None:
            raise RuntimeError("Goal5784 data bundle omitted manifest")
        data_manifest = json.load(manifest_handle)
    if data_manifest.get("run_goal_id") != 5784 \
            or data_manifest.get("file_count") != 5:
        raise RuntimeError("Goal5784 targeted data bundle is not exact")
    payloads = {
        "SOURCE.tar.gz": source,
        "PREREGISTRATION.json": PREREGISTRATION.read_bytes(),
        "RUNTIME_BUDGET.json": RUNTIME_BUDGET.read_bytes(),
        "EXPECTED_VALUE_STATEMENT.md": EXPECTATION.read_bytes(),
    }
    for name in HARNESS:
        path = ROOT / name
        payloads[f"HARNESS/{path.name}"] = path.read_bytes()
    readme = (
        "# Goal5784 targeted modern-RTX confirmation\n\n"
        "This create-only bundle prepares four exact V2/V4 units, sixteen "
        "untimed functional lanes, and a separately authorized 128-worker / "
        "eight-row formal cohort. It contains no target native and cannot "
        "execute formal workers without a second exact owner authority.\n"
    ).encode()
    payloads["README.md"] = readme
    rows = [{"path": name, "size_bytes": len(blob), "sha256": _sha(blob)}
            for name, blob in sorted(payloads.items())]
    manifest = {
        "schema": "rtdl.goal5784.targeted_pre_pod_manifest.v1",
        "goal": 5784,
        "bundle_version": 5,
        "source_archive_sha256": _sha(source),
        "data_archive_sha256": _sha(data),
        "data_payload_count": 5,
        "focused_test_count": 33,
        "target_unit_count": 4,
        "target_functional_trial_count": 16,
        "formal_worker_count": 128,
        "independent_comparison_row_count": 8,
        "v3_required_or_executed": False,
        "contains_target_native": False,
        "formal_execution_authorized": False,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    payloads["PORTABLE_MANIFEST.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    bundle = _archive(payloads)
    for path in (args.output, args.twin):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(bundle)
    if args.output.read_bytes() != args.twin.read_bytes():
        raise RuntimeError("Goal5784 bundle twin mismatch")
    print(json.dumps({
        "bundle_sha256": _sha(bundle),
        "data_archive_sha256": _sha(data),
        "source_archive_sha256": _sha(source),
        "payload_count": len(rows),
        "payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
