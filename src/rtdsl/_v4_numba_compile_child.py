"""Isolated compiler child for Goal5749.

This process executes only RTDL-generated source whose digest is supplied by
the verified parent.  It never receives the original user module/callable.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from pathlib import Path


def _compile_one(request, *, np, numba, cuda, types):
    source = request["generated_source"]
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    if digest != request["generated_source_sha256"]:
        raise RuntimeError("generated source digest mismatch")
    schema = request.get("schema")
    if schema not in (
        "rtdl.v4.generated_numba_leaf.v1",
        "rtdl.v4.generated_numba_scalar_probe.v1",
        "rtdl.v4.generated_formal_numba_leaf.v1",
    ):
        raise RuntimeError("generated source schema mismatch")
    # Only compiler-owned helpers required by deterministic generated source
    # are visible.  The original user callable/globals/defaults never enter
    # this child.
    namespace = {
        "__builtins__": {},
        "math": math,
        "_f32": np.float32,
        "range": range,
        "abs": abs,
    }
    exec(compile(source, "<rtdl-v4-generated>", "exec"), namespace, namespace)
    function = namespace.get(request["abi_name"])
    if not callable(function):
        raise RuntimeError("generated ABI function is missing")

    if schema == "rtdl.v4.generated_formal_numba_leaf.v1":
        # Helper bodies are deterministic compiler output from verified IR,
        # never user callables.  Register those generated bodies as internal
        # Numba device functions before compiling the public C-ABI leaf.  The
        # leaf and helpers share this isolated, compiler-owned namespace.
        helper_names = sorted(
            name for name, value in namespace.items()
            if name.startswith("_rtdl_helper_") and callable(value)
        )
        for name in helper_names:
            namespace[name] = cuda.jit(device=True, inline=True)(namespace[name])

    if schema == "rtdl.v4.generated_numba_scalar_probe.v1":
        signature = types.float32(types.float32)
    elif schema == "rtdl.v4.generated_formal_numba_leaf.v1":
        scalar = {
            "bool": types.boolean,
            "i32": types.int32,
            "u32": types.uint32,
            "i64": types.int64,
            "u64": types.uint64,
            "f32": types.float32,
            "f64": types.float64,
        }

        def abi_type(name):
            if name.startswith("ptr<") and name.endswith(">"):
                return types.CPointer(scalar[name[4:-1]])
            if name.startswith("device_ptr<") and name.endswith(">"):
                return types.CPointer(scalar[name[11:-1]])
            return scalar[name]

        signature = types.void(*(abi_type(item) for item in request["parameter_types"]))
    else:
        scalar = {"f32": types.float32, "u32": types.uint32}
        pointer = types.CPointer
        args = [scalar[item] for item in request["argument_types"]]
        args.extend((pointer(types.uint32), pointer(types.uint32), pointer(types.float32),
                     pointer(types.uint32), pointer(types.uint32)))
        signature = types.void(*args)
    ptx, _ = cuda.compile(
        function,
        signature,
        debug=False,
        lineinfo=True,
        device=True,
        fastmath=request["numeric_mode"] == "fast",
        cc=tuple(request["compute_capability"]),
        opt=True,
        abi="c",
        abi_info={"abi_name": request["abi_name"]},
        output="ptx",
    )
    return {
        "schema": "rtdl.v4.numba_compile_response.v1",
        "generated_source_sha256": digest,
        "ptx": ptx,
        "numba_version": numba.__version__,
        "numpy_version": np.__version__,
        "python_version": platform.python_version(),
        "cuda_available_was_queried": False,
        "explicit_compute_capability": request["compute_capability"],
    }


def _main(request_path: Path, response_path: Path) -> None:
    request = json.loads(request_path.read_text(encoding="utf-8"))
    import numpy as np
    import numba
    from numba import cuda, types

    if request.get("schema") == "rtdl.v4.generated_formal_numba_leaf_batch.v1":
        if set(request) != {"schema", "requests"} \
                or not isinstance(request["requests"], list) \
                or not request["requests"]:
            raise RuntimeError("generated formal leaf batch is malformed")
        responses = [
            _compile_one(item, np=np, numba=numba, cuda=cuda, types=types)
            for item in request["requests"]
        ]
        response = {
            "schema": "rtdl.v4.numba_compile_batch_response.v1",
            "responses": responses,
        }
    else:
        response = _compile_one(
            request, np=np, numba=numba, cuda=cuda, types=types)
    response_path.write_text(
        json.dumps(response, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: _v4_numba_compile_child.py REQUEST RESPONSE")
    _main(Path(sys.argv[1]), Path(sys.argv[2]))
