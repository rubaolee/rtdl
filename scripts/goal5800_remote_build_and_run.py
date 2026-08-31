#!/usr/bin/env python3
"""Build and execute the Goal5800 OWL residual once, without any timer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_and_capture(argv: list[str], stdout_path: Path,
                    stderr_path: Path) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(argv, capture_output=True, check=False)
    stdout_path.write_bytes(completed.stdout)
    stderr_path.write_bytes(completed.stderr)
    return completed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--build-root", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    args = parser.parse_args()
    if not (args.source_root / "GOAL5800_SOURCE_MANIFEST.json").is_file():
        raise FileNotFoundError("Goal5800 source manifest missing")
    if args.build_root.exists() or args.result_dir.exists():
        raise FileExistsError("build and result roots are create-only")
    args.build_root.mkdir(parents=True)
    args.result_dir.mkdir(parents=True)

    tools_dir = args.source_root / "goal5800_tools"
    sys.path.insert(0, str(tools_dir))
    from goal5800_capture_owl_untimed import verify_source_manifest

    source_manifest, source_manifest_sha = verify_source_manifest(
        args.source_root)
    if shutil.which("ninja"):
        generator = "Ninja"
    elif shutil.which("make"):
        generator = "Unix Makefiles"
    else:
        raise RuntimeError("neither Ninja nor make is available")
    configure_command = [
        "cmake", "-S", str(args.source_root), "-B", str(args.build_root),
        "-G", generator, "-DOWL_BUILD_SAMPLES=ON", "-DBUILD_TESTING=OFF",
        "-DOWL_USE_TBB=OFF", "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_CUDA_ARCHITECTURES=61",
    ]
    configure_stdout = args.result_dir / "cmake_configure_stdout.bin"
    configure_stderr = args.result_dir / "cmake_configure_stderr.bin"
    configured = run_and_capture(
        configure_command, configure_stdout, configure_stderr)

    build_command = [
        "cmake", "--build", str(args.build_root), "--target",
        "goal5800-owl-residual", "--parallel", "2",
    ]
    build_stdout = args.result_dir / "cmake_build_stdout.bin"
    build_stderr = args.result_dir / "cmake_build_stderr.bin"
    if configured.returncode == 0:
        built = run_and_capture(build_command, build_stdout, build_stderr)
    else:
        build_stdout.write_bytes(b"")
        build_stderr.write_bytes(b"")
        built = subprocess.CompletedProcess(build_command, 125, b"", b"")

    receipt = {
        "schema": "rtdl.goal5800.owl_build_receipt.v1",
        "scope": {
            "untimed_functional_build": True,
            "registered_performance_timing_count": 0,
            "performance_claimed": False,
        },
        "source_manifest_sha256": source_manifest_sha,
        "source_file_count_excluding_manifest": len(source_manifest["files"]),
        "cmake_generator": generator,
        "configure": {
            "argv": configure_command,
            "returncode": configured.returncode,
            "stdout_bytes": configure_stdout.stat().st_size,
            "stdout_sha256": sha256_file(configure_stdout),
            "stderr_bytes": configure_stderr.stat().st_size,
            "stderr_sha256": sha256_file(configure_stderr),
        },
        "build": {
            "argv": build_command,
            "returncode": built.returncode,
            "stdout_bytes": build_stdout.stat().st_size,
            "stdout_sha256": sha256_file(build_stdout),
            "stderr_bytes": build_stderr.stat().st_size,
            "stderr_sha256": sha256_file(build_stderr),
        },
    }
    build_receipt_path = args.result_dir / "goal5800_owl_build_receipt.json"
    build_receipt_path.write_bytes(
        json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    if configured.returncode != 0 or built.returncode != 0:
        raise RuntimeError(
            f"OWL build failed: configure={configured.returncode}, "
            f"build={built.returncode}")

    candidates = list(args.build_root.rglob("goal5800-owl-residual"))
    candidates = [path for path in candidates if path.is_file()]
    if len(candidates) != 1:
        raise RuntimeError(f"expected one OWL executable, found {candidates}")
    preserved_binary = args.result_dir / "goal5800-owl-residual"
    shutil.copy2(candidates[0], preserved_binary)
    capture_script = tools_dir / "goal5800_capture_owl_untimed.py"
    capture_command = [
        sys.executable, str(capture_script),
        "--source-root", str(args.source_root),
        "--binary", str(preserved_binary),
        "--result-dir", str(args.result_dir),
    ]
    captured = subprocess.run(capture_command, check=False)
    if captured.returncode != 0:
        raise RuntimeError(f"OWL capture failed: {captured.returncode}")
    print(json.dumps({
        "status": "PASS__BUILD_AND_UNTIMED_FUNCTIONAL_EXECUTION",
        "build_receipt_sha256": sha256_file(build_receipt_path),
        "result_sha256": sha256_file(
            args.result_dir / "goal5800_owl_untimed_result.json"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
