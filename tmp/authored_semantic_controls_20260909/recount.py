"""Offline exact-file recount. Imports no RTDL/compiler/runtime/driver."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import oracle


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(predicate, detail):
    if not predicate:
        raise AssertionError(detail)


def recount(root):
    request = read(root / "REQUEST.json")
    matrix = read(root / "MATRIX.json")
    cpu = request["mode"] == "cpu-preflight"
    cells = ["stale_plan", "P2-normal", "P2-swapped", "P3-normal", "P3-swapped"]
    require(matrix["mode"] == request["mode"], "matrix mode differs from request")
    require(matrix["attempted"] == [{"cell": v, "returncode": 0} for v in cells], "matrix incomplete or failure")
    require(matrix["not_attempted"] == [] and matrix["consistency_errors"] == [], "unfinished/drifting matrix")
    require(matrix["performance_result"] is False, "semantic controls cannot report performance")
    oracle_path = str(Path(oracle.__file__).resolve())
    # The source may be adopted at another absolute location; find its unique registered file.
    matches = [value for path, value in request["source"].items()
               if Path(path).name == "oracle.py" and Path(path).parent.name == Path(oracle_path).parent.name]
    require(matches == [sha(oracle_path)], "recount oracle does not bind registered oracle bytes")
    summaries = []
    for cell in cells:
        directory = root / cell
        result = read(directory / "RESULT.json")
        started = read(directory / "STARTED.json")
        require(started["config"] == request["config"], cell + ": target configuration drift")
        require(started["cpu_only"] is cpu, cell + ": mode drift")
        require(result["errors"] == [] and result["passed_at_declared_scope"] is True, cell + ": failure")
        for label in ("SOURCE_BEFORE.json", "SOURCE_AFTER.json"):
            require(read(directory / label) == request["source"], cell + ": source drift")
        if cell == "stale_plan":
            value = result["result"]
            require(value["code"] == "callback_binding", "wrong rejection")
            require(value["p2_ir"] != value["p3_ir"], "same source IR")
            require(value["materialize_called"] is False and value["gpu_execute_called"] is False,
                    "negative control executed GPU")
            continue
        power = int(cell[1])
        binding = cell.split("-")[1]
        identity = read(directory / "program_identity.json")
        require(identity["source_sha256"] == sha(directory / "AUTHORED_SOURCE.py.txt"), "authored source hash")
        wrapper_sha = sha(directory / "expected_wrapper.cu")
        row = {"cell": cell, "source_sha256": identity["source_sha256"],
               "ir_sha256": identity["callback_ir_sha256"], "effect_digest": identity["effect_digest"],
               "plan_sha256": identity["physical_plan_sha256"], "wrapper_sha256": wrapper_sha}
        for reverse in (False, True):
            expected = oracle.expected_rows(power, binding, reversed_order=reverse)
            stored_expected = np.load(directory / f"expected-{int(reverse)}.npy", allow_pickle=False)
            require(stored_expected.dtype == np.dtype("<u4") and np.array_equal(stored_expected, expected),
                    cell + ": frozen expected bytes differ from independent formula")
            if not cpu:
                actual_path = directory / f"actual-{int(reverse)}.npy"
                actual = np.load(actual_path, allow_pickle=False)
                comparison = read(directory / f"comparison-{int(reverse)}.json")
                require(actual.dtype == np.dtype("<u4") and actual.shape == (64, 3), "wrong full output type/shape")
                require(np.array_equal(actual, expected), cell + ": wrong full output")
                require(comparison["actual_file_sha256"] == sha(actual_path), "stored output hash changed")
                require(comparison["expected_file_sha256"] == sha(directory / f"expected-{int(reverse)}.npy"),
                        "stored expected hash changed")
                retained = read(directory / f"receipt-{int(reverse)}.json")
                require(retained["output"] == actual.tolist(), "receipt output bytes differ")
                executable_identity = read(directory / "materialized_identity.json")
                require(retained["executable_identity"] == executable_identity, "executable identity drift")
                require(executable_identity["native_library_sha256"] == request["config"]["native_sha256"],
                        "native identity drift")
                require(executable_identity["composed_ptx_sha256"] == sha(directory / "composed.ptx"),
                        "composed PTX identity drift")
                require(executable_identity["wrapper_source_sha256"] == wrapper_sha, "wrapper identity drift")
                require(retained["protocol_contract_decision"]["verdict"] == "ACCEPT", "contract not accepted")
                # Public runtime already validates the receipt; recount must retain and expose it,
                # not claim an RTDL-free reimplementation of receipt verification here.
                require(isinstance(retained["traversal_receipt"], dict) and retained["traversal_receipt"],
                        "no full public traversal receipt")
        summaries.append(row)
    a, b, c, d = summaries
    require(a["source_sha256"] == b["source_sha256"] != c["source_sha256"] == d["source_sha256"],
            "unexpected source factorial")
    require(a["ir_sha256"] == b["ir_sha256"] != c["ir_sha256"] == d["ir_sha256"], "unexpected IR factorial")
    require(len({v["effect_digest"] for v in summaries}) == 1, "effect class changed")
    require(len({v["plan_sha256"] for v in summaries}) == 4, "four distinct plan identities required")
    require(len({v["wrapper_sha256"] for v in summaries}) == 4, "four distinct wrappers required")
    return {"status": "CPU_CONTROLS_RECOUNTED" if cpu else "GPU_OUTPUT_AND_IDENTITY_RECOUNTED",
            "gpu_executed": not cpu, "performance_result": False, "cells": summaries,
            "geometry": oracle.independently_check_geometry(),
            "gpu_receipt_semantics_independently_reimplemented": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    value = recount(args.root)
    with args.out.open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
