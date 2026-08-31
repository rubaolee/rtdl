#!/usr/bin/env python3
"""Run the bounded Goal5749 P1 two-module diagnostic with zero timings."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import platform
from pathlib import Path

from goal5749_v4_callback_poc_driver import (
    POLICY_PATH,
    ROOT,
    SOURCE_PATH,
    _preflight,
    _sha256,
    _stable,
    _target_identity,
)
from rtdsl.v4_callback_poc import (
    CallbackRole,
    compile_numba_leaf_isolated,
    compile_numba_scalar_probe_isolated,
    generate_numba_leaf,
    generate_numba_scalar_probe,
    module_identity,
    verify_callback_source,
)
from rtdsl.v4_optix_callback_runtime import run_verified_callback_poc


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)

    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    lane = "home_linux_behavioral_feasibility"
    cc = _preflight(policy, lane)
    target_identity = _target_identity(policy, lane, cc)
    module = verify_callback_source(SOURCE_PATH.read_text(encoding="utf-8"))
    artifacts = []
    artifact_rows = []
    for role in CallbackRole:
        artifact = compile_numba_leaf_isolated(
            generate_numba_leaf(module, role, numeric_mode="strict"),
            compute_capability=cc,
            accepted_ptx_isa=(policy["backend"]["ptx_isa_min"],
                              policy["backend"]["ptx_isa_max"]),
            allowed_external_symbols=frozenset(),
        )
        artifacts.append(artifact)
        path = output / f"strict__{role.value}.ptx"
        path.write_text(artifact.ptx, encoding="utf-8")
        row = dataclasses.asdict(artifact)
        row.pop("ptx")
        row["ptx_path"] = path.name
        artifact_rows.append(row)
    scalar = compile_numba_scalar_probe_isolated(
        generate_numba_scalar_probe(module, numeric_mode="strict"),
        compute_capability=cc,
        accepted_ptx_isa=(policy["backend"]["ptx_isa_min"],
                          policy["backend"]["ptx_isa_max"]),
        allowed_external_symbols=frozenset(),
    )
    scalar_path = output / "strict__scalar_probe.ptx"
    scalar_path.write_text(scalar.ptx, encoding="utf-8")

    spheres = (((5.0, 0.0, 0.0), 1.0, 9),
               ((5.0, 0.0, 0.0), 1.0, 3),
               ((8.0, 0.0, 0.0), 1.0, 3))
    rays = (((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
            ((0.0, 4.0, 0.0), (1.0, 0.0, 0.0)),
            ((10.0, 0.0, 0.0), (-1.0, 0.0, 0.0)))
    result = run_verified_callback_poc(
        module,
        artifacts,
        spheres=spheres,
        rays=rays,
        tmin=0.0,
        tmax=100.0,
        route="ordinary_external_two_module_diagnostic",
        wrapper_numeric_mode="strict",
        scalar_probe=scalar,
    )
    receipt_path = output / "TRAVERSAL_RECEIPT.json"
    receipt_path.write_text(
        json.dumps(result.traversal_receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result_row = dataclasses.asdict(result)
    result_row.pop("traversal_receipt")
    record = {
        "schema": "rtdl.goal5749.p1_two_module_diagnostic.v1",
        "goal": 5749,
        "scope": "functional_only__zero_timing__p1_causal_closure",
        "construction": {
            "module_count": 2,
            "wrapper_module_contains_numba_leaf_definitions": False,
            "leaf_module_contains_verified_numba_leaf_definitions": True,
            "leaf_module_optix_anchor": "__direct_callable__rtdl_v4_leaf_module_anchor",
            "anchor_invoked": False,
            "numba_environment_declarations_safely_stripped": True,
        },
        "callback_module": module_identity(module),
        "numba_artifacts": artifact_rows,
        "scalar_probe": {
            **{key: value for key, value in dataclasses.asdict(scalar).items()
               if key != "ptx"},
            "ptx_path": scalar_path.name,
        },
        "result": result_row,
        "traversal_receipt_path": receipt_path.name,
        "target_identity": target_identity,
        "python": platform.python_version(),
        "source_archive_sha256": os.environ["RTDL_V4_SOURCE_ARCHIVE_SHA256"],
        "source_commit": os.environ["RTDL_V4_SOURCE_COMMIT"],
        "native_sha256": target_identity["native_sha256"],
        "registered_performance_timing_count": 0,
        "accepted_goal5749_result_rerun_or_changed": False,
        "performance_claimed": False,
    }
    record["record_sha256"] = _stable(record)
    result_path = output / "RESULT.json"
    result_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    manifest = [{
        "path": path.name,
        "size": path.stat().st_size,
        "sha256": _sha256(path),
    } for path in sorted(output.iterdir()) if path.is_file()]
    (output / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": str(result_path), "sha256": _sha256(result_path)},
                     sort_keys=True))


if __name__ == "__main__":
    main()
