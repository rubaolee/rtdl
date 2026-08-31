#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(
    name: str,
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    stdout_path: Path,
    stderr_path: Path,
) -> dict[str, Any]:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        completed = subprocess.run(command, cwd=cwd, env=env, stdout=stdout, stderr=stderr, check=False)
    elapsed = time.perf_counter() - started
    return {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "elapsed_sec": elapsed,
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _file_info(path: Path) -> dict[str, Any]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": _sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--pair-name", default="top4_county_zipcode")
    parser.add_argument("--author-build", default="Paper-reproduction-apps/rayjoin-paper/_work/author_official/release")
    parser.add_argument("--rtdl-optix-lib", default="build/librtdl_optix.so")
    parser.add_argument("--skip-author", action="store_true")
    parser.add_argument("--skip-text", action="store_true")
    parser.add_argument("--skip-numba", action="store_true")
    parser.add_argument("--skip-binary", action="store_true")
    parser.add_argument("--bounded-exact-lsi-capacity", type=int, default=1_000_000)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    left = Path(args.left).resolve()
    right = Path(args.right).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    app_dir = repo / "Paper-reproduction-apps" / "rayjoin-paper"
    author_build = (repo / args.author_build).resolve()
    polyover_exec = author_build / "bin" / "polyover_exec"
    python = sys.executable

    env = dict(os.environ)
    env["PYTHONPATH"] = f"{repo / 'src'}:{repo}"
    env["RTDL_OPTIX_LIB"] = str((repo / args.rtdl_optix_lib).resolve())
    env["RTDL_OPTIX_LIBRARY"] = env["RTDL_OPTIX_LIB"]
    cuda_home = env.get("CUDA_HOME") or "/usr/local/cuda"
    env["CUDA_HOME"] = cuda_home
    env["PATH"] = f"{Path(cuda_home) / 'bin'}:" + env.get("PATH", "")

    summary: dict[str, Any] = {
        "schema": "rtdl.paper_reproduction.rayjoin.goal4970_section57_top4_matrix.v1",
        "pair_name": args.pair_name,
        "left": str(left),
        "right": str(right),
        "routes": {},
    }

    author_output = out_dir / "author_official_section57_overlay.txt"
    if not args.skip_author:
        (out_dir / "author_serialize").mkdir(parents=True, exist_ok=True)
        author = _run(
            "author_official_polyover",
            [
                str(polyover_exec),
                "-poly1",
                str(left),
                "-poly2",
                str(right),
                f"-serialize={out_dir / 'author_serialize'}",
                "-grid_size=15000",
                "-mode=rt",
                "-v=1",
                "-fau",
                "-xsect_factor=0.1",
                "-enlarge=3.5",
                "-check=false",
                f"-output={author_output}",
            ],
            cwd=repo,
            env=env,
            stdout_path=out_dir / "author_official.stdout.txt",
            stderr_path=out_dir / "author_official.stderr.txt",
        )
        if author_output.exists():
            author["output"] = _file_info(author_output)
        summary["routes"]["author_official"] = author
    elif author_output.exists():
        summary["routes"]["author_official"] = {
            "name": "author_official_polyover",
            "reused_output": True,
            "output": _file_info(author_output),
        }

    if author_output.exists() and not args.skip_text:
        text_output = out_dir / "rtdl_text_section57_overlay.txt"
        text_summary = out_dir / "rtdl_text_section57_overlay.json"
        text = _run(
            "rtdl_text_public_primitives",
            [
                python,
                str(app_dir / "section57_overlay.py"),
                "--left",
                str(left),
                "--right",
                str(right),
                "--author-output",
                str(author_output),
                "--output",
                str(text_output),
                "--summary",
                str(text_summary),
                "--pair-name",
                args.pair_name,
                "--dataset-label",
                "representative_current_source",
                "--cache-dir",
                str(out_dir / "rtdl_packed_cache"),
            ],
            cwd=repo,
            env=env,
            stdout_path=out_dir / "rtdl_text.stdout.txt",
            stderr_path=out_dir / "rtdl_text.stderr.txt",
        )
        if text_output.exists():
            text["output"] = _file_info(text_output)
            text["byte_equal_to_author"] = (
                text["output"]["bytes"] == summary["routes"]["author_official"]["output"]["bytes"]
                and text["output"]["sha256"] == summary["routes"]["author_official"]["output"]["sha256"]
            )
        text["route_summary"] = _load_json(text_summary)
        summary["routes"]["rtdl_text"] = text

    if author_output.exists() and not args.skip_numba:
        numba_output = out_dir / "rtdl_numba_section57_overlay.txt"
        numba_summary = out_dir / "rtdl_numba_section57_overlay.json"
        numba = _run(
            "rtdl_numba_text_public_primitives",
            [
                python,
                str(app_dir / "section57_overlay_numba.py"),
                "--left",
                str(left),
                "--right",
                str(right),
                "--author-output",
                str(author_output),
                "--output",
                str(numba_output),
                "--summary",
                str(numba_summary),
                "--pair-name",
                args.pair_name,
                "--dataset-label",
                "representative_current_source",
                "--cache-dir",
                str(out_dir / "rtdl_packed_cache"),
            ],
            cwd=repo,
            env=env,
            stdout_path=out_dir / "rtdl_numba.stdout.txt",
            stderr_path=out_dir / "rtdl_numba.stderr.txt",
        )
        if numba_output.exists():
            numba["output"] = _file_info(numba_output)
            numba["byte_equal_to_author"] = (
                numba["output"]["bytes"] == summary["routes"]["author_official"]["output"]["bytes"]
                and numba["output"]["sha256"] == summary["routes"]["author_official"]["output"]["sha256"]
            )
        numba["route_summary"] = _load_json(numba_summary)
        summary["routes"]["rtdl_numba"] = numba

    if not args.skip_binary:
        binary_summary = out_dir / "rtdl_binary_fresh_section57_overlay.json"
        binary = _run(
            "rtdl_binary_device_columnar_fresh",
            [
                python,
                str(app_dir / "section57_overlay_columnar_binary.py"),
                "--left",
                str(left),
                "--right",
                str(right),
                "--summary",
                str(binary_summary),
                "--pair-name",
                args.pair_name,
                "--cache-dir",
                str(out_dir / "rtdl_packed_cache"),
                "--device-columnar",
                "--validate-device-order",
                "--compiled-group",
            ],
            cwd=repo,
            env=env,
            stdout_path=out_dir / "rtdl_binary_fresh.stdout.txt",
            stderr_path=out_dir / "rtdl_binary_fresh.stderr.txt",
        )
        binary["route_summary"] = _load_json(binary_summary)
        summary["routes"]["rtdl_binary_fresh"] = binary

        exact_lsi_summary = out_dir / "rtdl_binary_exact_lsi_device_columns_section57_overlay.json"
        exact_lsi = _run(
            "rtdl_binary_device_columnar_exact_lsi_device_columns",
            [
                python,
                str(app_dir / "section57_overlay_columnar_binary.py"),
                "--left",
                str(left),
                "--right",
                str(right),
                "--summary",
                str(exact_lsi_summary),
                "--pair-name",
                args.pair_name,
                "--cache-dir",
                str(out_dir / "rtdl_packed_cache"),
                "--device-columnar",
                "--validate-device-order",
                "--compiled-group",
                "--exact-lsi-device-columns",
            ],
            cwd=repo,
            env=env,
            stdout_path=out_dir / "rtdl_binary_exact_lsi_device_columns.stdout.txt",
            stderr_path=out_dir / "rtdl_binary_exact_lsi_device_columns.stderr.txt",
        )
        exact_lsi["route_summary"] = _load_json(exact_lsi_summary)
        summary["routes"]["rtdl_binary_exact_lsi_device_columns"] = exact_lsi

        bounded_exact_lsi_summary = out_dir / "rtdl_binary_bounded_exact_lsi_device_columns_section57_overlay.json"
        bounded_exact_lsi = _run(
            "rtdl_binary_device_columnar_bounded_exact_lsi_device_columns",
            [
                python,
                str(app_dir / "section57_overlay_columnar_binary.py"),
                "--left",
                str(left),
                "--right",
                str(right),
                "--summary",
                str(bounded_exact_lsi_summary),
                "--pair-name",
                args.pair_name,
                "--cache-dir",
                str(out_dir / "rtdl_packed_cache"),
                "--device-columnar",
                "--validate-device-order",
                "--compiled-group",
                "--bounded-exact-lsi-device-columns",
                "--bounded-exact-lsi-capacity",
                str(args.bounded_exact_lsi_capacity),
            ],
            cwd=repo,
            env=env,
            stdout_path=out_dir / "rtdl_binary_bounded_exact_lsi_device_columns.stdout.txt",
            stderr_path=out_dir / "rtdl_binary_bounded_exact_lsi_device_columns.stderr.txt",
        )
        bounded_exact_lsi["route_summary"] = _load_json(bounded_exact_lsi_summary)
        summary["routes"]["rtdl_binary_bounded_exact_lsi_device_columns"] = bounded_exact_lsi

        prepared_summary = out_dir / "rtdl_binary_prepared_replay_section57_overlay.json"
        prepared = _run(
            "rtdl_binary_device_columnar_prepared_lsi_replay",
            [
                python,
                str(app_dir / "section57_overlay_columnar_binary.py"),
                "--left",
                str(left),
                "--right",
                str(right),
                "--summary",
                str(prepared_summary),
                "--pair-name",
                args.pair_name,
                "--cache-dir",
                str(out_dir / "rtdl_packed_cache"),
                "--device-columnar",
                "--validate-device-order",
                "--compiled-group",
                "--prepared-lsi-replay",
            ],
            cwd=repo,
            env=env,
            stdout_path=out_dir / "rtdl_binary_prepared_replay.stdout.txt",
            stderr_path=out_dir / "rtdl_binary_prepared_replay.stderr.txt",
        )
        prepared["route_summary"] = _load_json(prepared_summary)
        summary["routes"]["rtdl_binary_prepared_replay"] = prepared

    summary_path = out_dir / "goal4970_top4_section57_matrix_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
