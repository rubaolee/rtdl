#!/usr/bin/env python3
"""Preserve exact Goal5843 executable/provider bytes before worker zero."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from experiments.goal5843_post_r1_baseline.contracts import (
    BOUND_ARTIFACTS_SCHEMA,
    digest,
    sha256_file,
)
from experiments.goal5843_post_r1_baseline.runtime import (
    create_json,
    load_execution_authority,
)


ROOT = Path(__file__).resolve().parents[1]


def copy_create_only(source: Path, destination: Path) -> dict[str, object]:
    source = source.resolve(strict=True)
    destination = destination.absolute()
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with source.open("rb") as input_stream, os.fdopen(
            descriptor, "wb", closefd=False
        ) as output_stream:
            for block in iter(lambda: input_stream.read(1024 * 1024), b""):
                output_stream.write(block)
            output_stream.flush()
            os.fsync(output_stream.fileno())
    finally:
        os.close(descriptor)
    source_mode = source.stat().st_mode & 0o777
    os.chmod(destination, source_mode)
    if sha256_file(destination) != sha256_file(source):
        raise RuntimeError(f"preserved artifact differs from source: {destination}")
    return {
        "source_path": str(source),
        "archived_path": destination.name,
        "bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
        "source_mode": source_mode,
    }


def preserve(
    authority: dict[str, object], destination_root: Path
) -> list[dict[str, object]]:
    destination_root.mkdir(parents=True, exist_ok=False)
    paths = authority["execution_paths"]
    pyoptix = authority["pyoptix"]
    rows = []
    fixed = (
        ("execution_paths.native_library", paths["native_library"], "native/librtdl_optix.so"),
        (
            "execution_paths.native_build_manifest",
            paths["native_build_manifest"],
            "native/NATIVE_BUILD_MANIFEST.json",
        ),
        (
            "execution_paths.direct_binary",
            paths["direct_binary"],
            "direct/goal5843_direct_measurement",
        ),
    )
    for binding, source_text, relative_text in fixed:
        relative = Path(relative_text)
        row = copy_create_only(Path(str(source_text)), destination_root / relative)
        row["authority_binding"] = binding
        row["archived_path"] = relative.as_posix()
        rows.append(row)

    module_tree = pyoptix["module_tree"]
    module_root = Path(str(module_tree["root"]))
    for module_row in module_tree["files"]:
        relative_source = Path(str(module_row["path"]))
        relative_archive = Path("pyoptix_module") / relative_source
        row = copy_create_only(
            module_root / relative_source,
            destination_root / relative_archive,
        )
        if (
            row["bytes"] != module_row["bytes"]
            or row["sha256"] != module_row["sha256"]
        ):
            raise RuntimeError("preserved PyOptiX module differs from authority")
        row["authority_binding"] = f"pyoptix.module_tree:{relative_source.as_posix()}"
        row["archived_path"] = relative_archive.as_posix()
        rows.append(row)

    cupy_file = pyoptix["cupy_module_file"]
    cupy_relative = Path("cupy_module") / Path(str(cupy_file["path"])).name
    row = copy_create_only(Path(str(cupy_file["path"])), destination_root / cupy_relative)
    if row["bytes"] != cupy_file["bytes"] or row["sha256"] != cupy_file["sha256"]:
        raise RuntimeError("preserved CuPy module file differs from authority")
    row["authority_binding"] = "pyoptix.cupy_module_file"
    row["archived_path"] = cupy_relative.as_posix()
    rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prereg, authority = load_execution_authority(
        args.execution_authority,
        preregistration_path=args.preregistration,
        root=ROOT,
        require_clean_repository=True,
    )
    rows = preserve(authority, args.destination_root.absolute())
    result: dict[str, object] = {
        "schema": BOUND_ARTIFACTS_SCHEMA,
        "status": "PASS__EXACT_BOUND_EXECUTABLE_AND_PROVIDER_BYTES_PRESERVED",
        "source_commit": authority["source_commit"],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "artifact_count": len(rows),
        "artifacts": rows,
        "gpu_complete_execution_count": 0,
        "goal5843_registered_estimand_timing_observation_count": 0,
    }
    result["custody_sha256"] = digest(result)
    create_json(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
