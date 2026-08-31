#!/usr/bin/env python3
"""One fresh-process Goal5776 real-scale V2-direct or V4 endpoint.

The worker does not decide an application algorithm and does not compute a
ratio.  It binds one frozen schedule item, executes one method/lifecycle
front door, verifies the exact output and behavioral OptiX receipt, and emits
the raw registered observations consumed by two independent statistics paths.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import sys
from typing import Callable, Mapping

import numba
import numpy as np

from goal5776_evaluate_real_scale_v2_v4 import BOUNDARY
from goal5776_real_scale_formal_contract import (
    COLD,
    PREPARED,
    UNIT_BY_ID,
    V2,
    V4,
    contract_sha256,
    schedule,
)
from goal5776_symmetric_endpoint import validate_behavioral_true_optix


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _validate_receipt_row_binding(
    receipt: Mapping[str, object], rows: list[Mapping[str, object]],
) -> None:
    binding = receipt.get("registered_row_binding")
    if not isinstance(binding, Mapping) or set(binding) != {
        "schema", "binding_scope", "row_count", "ordered_rows_sha256",
        "unbound_traversal_receipt_sha256",
    }:
        raise RuntimeError("Goal5776 receipt omitted registered-row binding")
    canonical_rows = [{
        "row_id": str(row["row_id"]),
        "input_sha256": str(row["input_sha256"]),
        "output_sha256": str(row["output_sha256"]),
    } for row in rows]
    unbound_receipt = dict(receipt)
    del unbound_receipt["registered_row_binding"]
    if (
        binding["schema"] != "rtdl.goal5776.registered_row_binding.v1"
        or binding["binding_scope"]
        != "post_timer_evidence_binding__not_native_claim"
        or binding["row_count"] != len(canonical_rows)
        or binding["ordered_rows_sha256"] != _digest(canonical_rows)
        or binding["unbound_traversal_receipt_sha256"]
        != _digest(unbound_receipt)
    ):
        raise RuntimeError("Goal5776 registered-row receipt binding mismatch")
    if receipt.get("schema") \
            == "rtdl.goal5776.combined_behavioral_optix_receipt.v1":
        components = receipt.get("component_receipts")
        if not isinstance(components, list) or (
            receipt.get("component_receipt_count") != len(components)
            or receipt.get("component_receipts_sha256") != _digest(components)
        ):
            raise RuntimeError("Goal5776 combined receipt omitted components")
        for component in components:
            if not isinstance(component, Mapping):
                raise RuntimeError("Goal5776 combined receipt component is malformed")
            validate_behavioral_true_optix(component)


def _load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def installed_partner_versions() -> dict[str, str]:
    """Read optional partner identities without making them import-time gates."""

    result = {}
    for name in ("cupy", "scipy"):
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError:
            result[name] = "__not_installed__"
        else:
            result[name] = str(module.__version__)
    return result


def _validate_runtime(runtime: Mapping[str, object]) -> tuple[Path, Path]:
    required = {
        "schema", "source_root", "bundle_sha256", "data_archive_sha256",
        "execution_source_sha256", "source_tree_sha256",
        "rtdbscan_evidence_sha256",
        "native_library_path", "native_library_sha256",
        "target_identity_sha256", "prepared_identity_sha256",
        "plan_sha256", "formal_identity_sha256",
        "leaf_cache_root", "leaf_cache_manifest_path",
        "leaf_cache_manifest_sha256", "formal_contract_sha256",
        "expected_value_statement_path", "expected_value_statement_sha256",
        "python_executable", "python_executable_sha256",
        "python_version", "numba_version", "numpy_version",
        "cupy_version", "scipy_version", "inputs",
    }
    if not required.issubset(runtime):
        raise RuntimeError("Goal5776 runtime identity is incomplete")
    if runtime["schema"] != "rtdl.goal5776.real_scale_runtime.v1":
        raise RuntimeError("Goal5776 runtime schema is not exact")
    if runtime["formal_contract_sha256"] != contract_sha256():
        raise RuntimeError("Goal5776 runtime binds a different formal contract")
    python = Path(sys.executable).resolve()
    partners = installed_partner_versions()
    if (
        python != Path(str(runtime["python_executable"])).resolve()
        or _sha(python) != runtime["python_executable_sha256"]
        or platform.python_version() != runtime["python_version"]
        or numba.__version__ != runtime["numba_version"]
        or np.__version__ != runtime["numpy_version"]
        or partners["cupy"] != runtime["cupy_version"]
        or partners["scipy"] != runtime["scipy_version"]
    ):
        raise RuntimeError(
            "Goal5776 Python/Numba/NumPy/CuPy/SciPy identity mismatch")
    native = Path(str(runtime["native_library_path"])).resolve()
    manifest = Path(str(runtime["leaf_cache_manifest_path"])).resolve()
    expected_value_statement = Path(
        str(runtime["expected_value_statement_path"])).resolve()
    if not native.is_file() or _sha(native) != runtime["native_library_sha256"]:
        raise RuntimeError("Goal5776 native identity mismatch")
    if not manifest.is_file() or _sha(manifest) != runtime["leaf_cache_manifest_sha256"]:
        raise RuntimeError("Goal5776 leaf-cache manifest identity mismatch")
    if not expected_value_statement.is_file() or _sha(
        expected_value_statement
    ) != runtime["expected_value_statement_sha256"]:
        raise RuntimeError("Goal5776 expected-value statement identity mismatch")
    return native, manifest


def _cache_delta(before: Mapping[str, object], after: Mapping[str, object]) -> dict[str, object]:
    return {
        "mode": "sealed_read_only_manifest",
        "hit_count": int(after["hit_count"]) - int(before["hit_count"]),
        "miss_count": int(after["miss_count"]) - int(before["miss_count"]),
        "disabled_count": (
            int(after["disabled_count"]) - int(before["disabled_count"])
        ),
    }


def _validate_endpoint(
    endpoint: Mapping[str, object], *, worker_spec: Mapping[str, object]
) -> None:
    lifecycle = str(worker_spec["lifecycle"])
    unit = UNIT_BY_ID[str(worker_spec["unit_id"])]
    expected_ids = set(unit.statistical_row_ids_for(lifecycle))
    if (
        endpoint.get("matched") is not True
        or endpoint.get("default_selected_between_application_algorithms") is not False
        or endpoint.get("comparator_inside_registered_timer") is not False
        or endpoint.get("close_inside_registered_timer") is not (lifecycle == COLD)
    ):
        raise RuntimeError("Goal5776 front door violated the endpoint contract")
    loading = endpoint.get("loading_seconds_reported_separately")
    preparation = endpoint.get("preparation_seconds_reported_separately")
    if lifecycle == COLD:
        if loading is not None or preparation is not None:
            raise RuntimeError("cold endpoint moved required work outside the timer")
    else:
        for name, value in (("loading", loading), ("preparation", preparation)):
            if not isinstance(value, (int, float)) or not math.isfinite(
                float(value)
            ) or float(value) < 0.0:
                    raise RuntimeError(f"prepared endpoint omitted {name} seconds")
    session_wall = endpoint.get(
        "prepared_session_complete_wall_seconds_reported_separately"
    )
    if unit.app == "rayjoin" and lifecycle == PREPARED:
        if not isinstance(session_wall, (int, float)) or not math.isfinite(
            float(session_wall)
        ) or float(session_wall) <= 0.0:
            raise RuntimeError(
                "prepared RayJoin endpoint omitted its overlapping complete-session wall"
            )
    elif session_wall is not None:
        raise RuntimeError("unexpected prepared-session wall observation")
    receipt = endpoint.get("traversal_receipt")
    if not isinstance(receipt, Mapping):
        raise RuntimeError("Goal5776 front door omitted traversal receipt")
    validate_behavioral_true_optix(receipt)
    rows = endpoint.get("rows")
    accounting = endpoint.get("phase_accounting")
    if not isinstance(accounting, Mapping) or set(accounting) != {
        "loading_seconds", "preparation_seconds", "close_seconds",
        "row_execute_seconds", "same_worker_mutually_exclusive_phases",
        "nested_phase_medians_summed",
    }:
        raise RuntimeError("Goal5776 front door omitted exact phase accounting")
    if (
        accounting["same_worker_mutually_exclusive_phases"] is not True
        or accounting["nested_phase_medians_summed"] is not False
        or any(
            not isinstance(accounting[name], (int, float))
            or not math.isfinite(float(accounting[name]))
            or float(accounting[name]) < 0.0
            for name in ("loading_seconds", "preparation_seconds", "close_seconds")
        )
        or not isinstance(accounting["row_execute_seconds"], Mapping)
    ):
        raise RuntimeError("Goal5776 front-door phase accounting is malformed")
    if not isinstance(rows, list) or len(rows) != len(expected_ids) or {
        str(row.get("row_id")) for row in rows if isinstance(row, Mapping)
    } != expected_ids:
        raise RuntimeError("Goal5776 front door emitted the wrong statistical rows")
    _validate_receipt_row_binding(receipt, rows)
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {
            "row_id", "input_sha256", "output_sha256",
            "registered_complete_endpoint_seconds",
        }:
            raise RuntimeError("Goal5776 front-door row schema mismatch")
        seconds = row["registered_complete_endpoint_seconds"]
        if not isinstance(seconds, (int, float)) or not math.isfinite(
            float(seconds)
        ) or float(seconds) <= 0.0:
            raise RuntimeError("Goal5776 front door emitted invalid seconds")
        if any(
            not isinstance(row[name], str) or len(row[name]) != 64
            for name in ("input_sha256", "output_sha256")
        ):
            raise RuntimeError("Goal5776 front door emitted invalid digests")
        execute = accounting["row_execute_seconds"].get(row["row_id"])
        if not isinstance(execute, (int, float)) or not math.isfinite(
            float(execute)
        ) or float(execute) <= 0.0:
            raise RuntimeError("Goal5776 row lacks direct execute observation")
        expected = float(execute)
        if lifecycle == COLD:
            expected += sum(float(accounting[name]) for name in (
                "loading_seconds", "preparation_seconds", "close_seconds"
            ))
        if not math.isclose(
            float(row["registered_complete_endpoint_seconds"]), expected,
            rel_tol=0.0, abs_tol=1.0e-12,
        ):
            raise RuntimeError("registered endpoint does not equal direct phase sum")


def run_worker(
    *,
    runtime_path: Path,
    worker_index: int,
    output: Path,
    runner: Callable[..., Mapping[str, object]] | None = None,
) -> Path:
    if output.exists():
        raise FileExistsError(output)
    frozen_schedule = schedule()
    if not isinstance(worker_index, int) or not 0 <= worker_index < len(frozen_schedule):
        raise ValueError("Goal5776 worker index out of range")
    worker_spec = frozen_schedule[worker_index]
    runtime = _load_json(runtime_path.resolve())
    native, manifest = _validate_runtime(runtime)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_V4_FORMAL_LEAF_CACHE"] = str(
        Path(str(runtime["leaf_cache_root"])).resolve()
    )
    os.environ["RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST"] = str(manifest)
    os.environ["RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256"] = str(
        runtime["leaf_cache_manifest_sha256"]
    )

    from rtdsl.v4_callback_numba_codegen import (
        formal_numba_leaf_cache_lifecycle_metadata,
    )

    if runner is None:
        from goal5776_real_scale_frontdoors import run_real_scale_endpoint
        runner = run_real_scale_endpoint
    cache_before = formal_numba_leaf_cache_lifecycle_metadata()
    endpoint = dict(runner(
        unit_id=str(worker_spec["unit_id"]),
        method=str(worker_spec["method"]),
        lifecycle=str(worker_spec["lifecycle"]),
        runtime=runtime,
    ))
    cache_after = formal_numba_leaf_cache_lifecycle_metadata()
    _validate_endpoint(endpoint, worker_spec=worker_spec)
    if worker_spec["method"] == V4:
        leaf_cache = _cache_delta(cache_before, cache_after)
        unit = UNIT_BY_ID[str(worker_spec["unit_id"])]
        if unit.v4_numba_leaf_cache_required:
            if (
                leaf_cache["hit_count"] <= 0
                or leaf_cache["miss_count"] != 0
                or leaf_cache["disabled_count"] != 0
            ):
                raise RuntimeError("V4 worker did not consume only frozen cache entries")
            leaf_cache["mode"] = "sealed_read_only_manifest"
        else:
            if any(leaf_cache[key] != 0 for key in (
                "hit_count", "miss_count", "disabled_count")):
                raise RuntimeError("non-leaf V4 worker touched frozen leaf cache")
            leaf_cache["mode"] = "not_applicable_no_numba_leaf"
    else:
        leaf_cache = {"mode": "not_applicable_to_v2_direct"}

    payload = {
        "schema": "rtdl.goal5776.real_scale_formal_worker.v1",
        "worker_index": worker_index,
        "parent_pid": os.getpid(),
        "lifecycle": worker_spec["lifecycle"],
        "unit_id": worker_spec["unit_id"],
        "method": worker_spec["method"],
        "pair_index": worker_spec["pair_index"],
        "order_ordinal": worker_spec["order_ordinal"],
        "formal_worker": True,
        "matched": True,
        "registered_endpoint_boundary_id": BOUNDARY,
        "comparator_inside_registered_timer": False,
        "close_inside_registered_timer": endpoint[
            "close_inside_registered_timer"
        ],
        "loading_seconds_reported_separately": endpoint[
            "loading_seconds_reported_separately"
        ],
        "preparation_seconds_reported_separately": endpoint[
            "preparation_seconds_reported_separately"
        ],
        "prepared_session_complete_wall_seconds_reported_separately": endpoint.get(
            "prepared_session_complete_wall_seconds_reported_separately"
        ),
        "default_selected_between_application_algorithms": False,
        "retry_resume_replacement_row_drop_relabel_used": False,
        "traversal_receipt": endpoint["traversal_receipt"],
        "phase_accounting": endpoint["phase_accounting"],
        "rows": endpoint["rows"],
        "leaf_cache": leaf_cache,
        "bundle_sha256": runtime["bundle_sha256"],
        "data_archive_sha256": runtime["data_archive_sha256"],
        "execution_source_sha256": runtime["execution_source_sha256"],
        "source_tree_sha256": runtime["source_tree_sha256"],
        "rtdbscan_evidence_sha256": runtime["rtdbscan_evidence_sha256"],
        "native_library_sha256": runtime["native_library_sha256"],
        "target_identity_sha256": runtime["target_identity_sha256"],
        "prepared_identity_sha256": runtime["prepared_identity_sha256"],
        "plan_sha256": runtime["plan_sha256"],
        "formal_identity_sha256": runtime["formal_identity_sha256"],
        "leaf_cache_manifest_sha256": runtime[
            "leaf_cache_manifest_sha256"
        ],
        "expected_value_statement_sha256": runtime[
            "expected_value_statement_sha256"
        ],
        "formal_contract_sha256": runtime["formal_contract_sha256"],
        "runtime_sha256": _sha(runtime_path),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--worker-index", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(run_worker(
        runtime_path=args.runtime,
        worker_index=args.worker_index,
        output=args.output,
    ))


if __name__ == "__main__":
    main()
