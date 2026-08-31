#!/usr/bin/env python3
"""Freeze an exact shell-free Direct BUILD_COLD compilation recipe."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-directory", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    library_arguments: list[str] = []
    for raw in args.library_directory:
        directory = Path(raw).resolve(strict=True)
        if not directory.is_dir():
            raise RuntimeError(f"Direct library directory invalid: {directory}")
        library_arguments.append(f"-L{directory}")
    argv = [
        "{CXX}", "-std=c++17", "-O3", "-DNDEBUG",
        "-Wall", "-Wextra", "-Werror",
        "-I{OPTIX_INCLUDE}", "-I{CUDA_INCLUDE}",
        "-I{CUDA_INCLUDE}/nv", "{DIRECT_SOURCE}",
        *library_arguments,
        "-lcuda", "-lnvrtc", "-ldl", "-o", "{OUTPUT}",
    ]
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.direct_build_recipe.v2",
        "argv_template": argv,
    }
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")
    value["recipe_sha256"] = hashlib.sha256(encoded).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({"status": "PASS__RECIPE_FROZEN",
                      "recipe_sha256": value["recipe_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
