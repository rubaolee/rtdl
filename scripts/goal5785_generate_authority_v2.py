#!/usr/bin/env python3
"""Linux-venv-safe Goal5785 authority generator amendment.

V1 called ``Path.resolve()`` on a virtual-environment Python symlink.  On
Linux that selected the system interpreter and discarded the venv site-packages.
This wrapper changes only that path materialization rule and reuses every
authority schema, digest and fail-closed rule from V1.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

try:
    import goal5785_generate_authority as v1
except ModuleNotFoundError:  # Imported as scripts.goal5785_generate_authority_v2.
    from scripts import goal5785_generate_authority as v1


def python_path_without_symlink_resolution(path: Path) -> Path:
    """Return an absolute spelling while preserving a venv Python symlink."""
    return Path(os.path.abspath(path))


def command_prepare(args) -> None:
    bundle = args.bundle.resolve()
    data = args.data_bundle.resolve()
    python = python_path_without_symlink_resolution(args.python)
    manifest = v1._outer_json(bundle, "PORTABLE_MANIFEST.json")
    if manifest.get("run_goal_id") != 5785 \
            or manifest.get("formal_worker_count") != 464 \
            or manifest.get("independent_comparison_row_count") != 34:
        raise RuntimeError("Goal5785 exact bundle manifest is absent")
    nvidia = subprocess.run([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader",
    ], text=True, capture_output=True, check=True, timeout=30)
    lines = [line.strip() for line in nvidia.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("Goal5785 requires exactly one visible GPU")
    gpu = tuple(part.strip() for part in lines[0].split(","))
    if len(gpu) != 4 or gpu[3].replace(".", "") != args.cc:
        raise RuntimeError("Goal5785 target compute capability mismatch")
    version = subprocess.run([
        str(python), "-c",
        "import json,platform,numba,numpy,cupy,scipy; print(json.dumps({"
        "'python':platform.python_version(),'numba':numba.__version__,"
        "'numpy':numpy.__version__,'cupy':cupy.__version__,"
        "'scipy':scipy.__version__},sort_keys=True))",
    ], text=True, capture_output=True, check=True, timeout=60)
    python_identity = {
        **json.loads(version.stdout),
        "python_executable_sha256": v1._sha(python),
    }
    body = v1.prepare_body(
        bundle_sha256=v1._sha(bundle),
        source_sha256=str(manifest["source_archive_sha256"]),
        data_sha256=v1._sha(data),
        expectation_sha256=str(manifest["expected_value_statement_sha256"]),
        gpu=gpu,
        cc=args.cc,
        python_identity=python_identity,
        authorized=args.owner_authorized,
    )
    payload = v1._authorize(body)
    v1._write_create_only(args.output, payload)
    print(json.dumps({
        "output": str(args.output),
        "authority_sha256": payload["authority_sha256"],
        "owner_authorized": args.owner_authorized,
        "gpu": gpu,
        "python_identity": python_identity,
        "amendment": "A2__preserve_linux_venv_python_symlink",
    }, sort_keys=True))


def main() -> None:
    v1.command_prepare = command_prepare
    v1.main()


if __name__ == "__main__":
    main()
