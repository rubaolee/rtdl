from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.rayjoin_paper_suite import RAYJOIN_PREPROCESSED_SHARE_URL
from rtdsl.rayjoin_paper_suite import RAYJOIN_SECTION57_TABLE4_SECONDS
from rtdsl.rayjoin_paper_suite import availability_matrix
from rtdsl.rayjoin_paper_suite import paper_cases
from rtdsl.rayjoin_paper_suite import paper_pairs


IMPLEMENTATIONS = ("author_rt", "rtdl_optix", "rtdl_embree", "v4_numba")


def _split_csv(value: str | None, *, default: Iterable[str]) -> tuple[str, ...]:
    if value is None or value.strip() == "":
        return tuple(default)
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _overlay_cases(pair_ids: Iterable[str] | None = None):
    selected = set(pair_ids) if pair_ids is not None else None
    return tuple(
        case
        for case in paper_cases(program_ids=("overlay",))
        if selected is None or case.pair.pair_id in selected
    )


def _json_default(value):
    if isinstance(value, Path):
        return str(value)
    return value


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=_json_default) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _overlay_output_digest(path: Path | None) -> dict[str, object] | None:
    if path is None or not path.exists():
        return None
    data = path.read_bytes()
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return {
        "path": str(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "line_count": len(lines),
    }


def _overlay_output_path_from_command(command: list[str]) -> Path | None:
    for flag in ("--overlay-output", "-output"):
        if flag not in command:
            continue
        index = command.index(flag)
        if index + 1 >= len(command):
            raise ValueError(f"command has {flag} without a following path")
        return Path(command[index + 1])
    return None


def _artifact_paths(output_dir: Path, pair_id: str) -> dict[str, Path]:
    return {
        "author_rt": output_dir / f"section57_overlay_{pair_id}_author_rt.json",
        "rtdl_optix": output_dir / f"section57_overlay_{pair_id}_rtdl_optix.json",
        "rtdl_embree": output_dir / f"section57_overlay_{pair_id}_rtdl_embree.json",
        "v4_numba": output_dir / f"section57_overlay_{pair_id}_v4_numba.json",
    }


def _availability_by_pair(dataset_root: Path, pair_ids: Iterable[str]) -> dict[str, object]:
    rows = availability_matrix(dataset_root, pair_ids=pair_ids, program_ids=("overlay",))
    return {row.pair_id: row for row in rows}


def _author_command(args: argparse.Namespace, case, output_json: Path) -> list[str]:
    if args.query_exec is None or args.polyover_exec is None:
        raise ValueError("author_rt requires --query-exec and --polyover-exec")
    command = [
        sys.executable,
        str(ROOT / "scripts" / "rayjoin_paper_reproduction_suite.py"),
        "run-author",
        "--dataset-root",
        str(args.dataset_root),
        "--query-exec",
        str(args.query_exec),
        "--polyover-exec",
        str(args.polyover_exec),
        "--case-id",
        case.case_id,
        "--mode",
        args.mode,
        "--serialize-prefix",
        args.serialize_prefix,
        "--grid-size",
        str(args.grid_size),
        "--xsect-factor",
        str(args.xsect_factor),
        "--enlarge",
        str(args.enlarge),
        "--warmup",
        str(args.author_warmup),
        "--repeat",
        str(args.author_repeat),
        "--output-json",
        str(output_json),
    ]
    if args.assemble_overlay_output:
        command.extend(["--overlay-output", str(output_json.with_suffix(".overlay.txt"))])
    return command


def _rtdl_command(args: argparse.Namespace, case, backend: str, output_json: Path) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "rayjoin_paper_reproduction_suite.py"),
        "run-rtdl",
        "--dataset-root",
        str(args.dataset_root),
        "--case-id",
        case.case_id,
        "--backend",
        backend,
        "--warmup",
        str(args.rtdl_warmup),
        "--repeat",
        str(args.rtdl_repeat),
        "--input-provenance",
        args.input_provenance,
        "--output-json",
        str(output_json),
    ]
    if args.packed_cache_dir is not None:
        command.extend(["--packed-cache-dir", str(args.packed_cache_dir)])
    if args.disable_packed_cache:
        command.append("--disable-packed-cache")
    if args.assemble_overlay_output:
        command.append("--assemble-overlay-output")
        command.extend(["--overlay-output", str(output_json.with_suffix(".overlay.txt"))])
    return command


def _v4_numba_command(args: argparse.Namespace, case, output_json: Path) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "examples" / "paper_reproduction" / "rayjoin.py"),
        "--section57-auto-numba",
        "--dataset-root",
        str(args.dataset_root),
        "--output-dir",
        str(args.output_dir),
        "--pairs",
        case.pair.pair_id,
        "--partner",
        "numba",
        "--select",
        args.v4_numba_select,
        "--input-provenance",
        args.input_provenance,
        "--rtdl-warmup",
        str(args.rtdl_warmup),
        "--rtdl-repeat",
        str(args.rtdl_repeat),
        "--output-json",
        str(output_json),
        "--output-md",
        str(output_json.with_suffix(".md")),
    ]
    if args.query_exec is not None:
        command.extend(["--query-exec", str(args.query_exec)])
    if args.polyover_exec is not None:
        command.extend(["--polyover-exec", str(args.polyover_exec)])
    if args.v4_numba_skip_runtime_probe:
        command.append("--skip-runtime-probe")
    if args.v4_numba_section57_device_columns_ready:
        command.append("--section57-device-columns-ready")
    if args.v4_numba_measurements is not None:
        command.extend(["--v4-numba-measurements", str(args.v4_numba_measurements)])
    return command


def _planned_commands(args: argparse.Namespace, case, paths: dict[str, Path]) -> dict[str, list[str] | None]:
    commands: dict[str, list[str] | None] = {}
    for implementation in _split_csv(args.implementations, default=IMPLEMENTATIONS):
        if implementation == "author_rt":
            if args.query_exec is None or args.polyover_exec is None:
                commands[implementation] = None
            else:
                commands[implementation] = _author_command(args, case, paths[implementation])
        elif implementation == "rtdl_optix":
            commands[implementation] = _rtdl_command(args, case, "optix", paths[implementation])
        elif implementation == "rtdl_embree":
            commands[implementation] = _rtdl_command(args, case, "embree", paths[implementation])
        elif implementation == "v4_numba":
            commands[implementation] = _v4_numba_command(args, case, paths[implementation])
        else:
            raise ValueError(f"unknown implementation: {implementation}")
    return commands


def build_plan(args: argparse.Namespace) -> dict[str, object]:
    pair_ids = _split_csv(args.pairs, default=[pair.pair_id for pair in paper_pairs()])
    cases = _overlay_cases(pair_ids)
    availability = _availability_by_pair(args.dataset_root, pair_ids)
    rows = []
    for case in cases:
        paths = _artifact_paths(args.output_dir, case.pair.pair_id)
        available = availability[case.pair.pair_id]
        rows.append(
            {
                "case_id": case.case_id,
                "pair_id": case.pair.pair_id,
                "paper_label": case.pair.paper_label,
                "exact_input_ready": bool(available.exact_input_ready),
                "blocker": available.blocker,
                "left_path": available.left.path,
                "right_path": available.right.path,
                "paper_table4_seconds": {
                    artifact: {
                        "processing_sec": values[0],
                        "preprocessing_sec": values[1],
                    }
                    for artifact, by_pair in RAYJOIN_SECTION57_TABLE4_SECONDS.items()
                    for values in (by_pair[case.pair.pair_id],)
                },
                "result_paths": {key: str(value) for key, value in paths.items()},
                "commands": _planned_commands(args, case, paths),
            }
        )
    ready = sum(1 for row in rows if row["exact_input_ready"])
    return {
        "schema": "rtdl.rayjoin.section57_overlay_matrix.plan.v1",
        "dataset_root": str(args.dataset_root),
        "output_dir": str(args.output_dir),
        "input_provenance": args.input_provenance,
        "preprocessed_share_url": RAYJOIN_PREPROCESSED_SHARE_URL,
        "coverage": {
            "overlay_pairs_total": len(rows),
            "overlay_pairs_input_ready": ready,
            "overlay_pairs_blocked": len(rows) - ready,
            "required_for_section57_full_reproduction": "8/8 overlay pairs with author_rt, rtdl_optix, and rtdl_embree results",
        },
        "rows": rows,
    }


def _run_one(command: list[str], *, output_json: Path, timeout_sec: int | None) -> dict[str, object]:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    stdout_path = output_json.with_suffix(output_json.suffix + ".stdout.txt")
    stderr_path = output_json.with_suffix(output_json.suffix + ".stderr.txt")
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as error:
        elapsed = time.perf_counter() - start
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        return {
            "command": command,
            "exit_code": None,
            "elapsed_sec": elapsed,
            "output_json": str(output_json),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "completed": False,
            "timed_out": True,
            "timeout_sec": timeout_sec,
        }
    elapsed = time.perf_counter() - start
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    return {
        "command": command,
        "exit_code": completed.returncode,
        "elapsed_sec": elapsed,
        "output_json": str(output_json),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "completed": completed.returncode == 0 and output_json.exists(),
        "timed_out": False,
    }


def _command_with_output_json(command: list[str], output_json: Path) -> list[str]:
    updated = list(command)
    try:
        index = updated.index("--output-json")
    except ValueError as error:
        raise ValueError("command does not contain --output-json") from error
    if index + 1 >= len(updated):
        raise ValueError("command has --output-json without a following path")
    updated[index + 1] = str(output_json)
    for flag in ("--overlay-output", "-output"):
        if flag not in updated:
            continue
        overlay_index = updated.index(flag)
        if overlay_index + 1 >= len(updated):
            raise ValueError(f"command has {flag} without a following path")
        updated[overlay_index + 1] = str(output_json.with_suffix(".overlay.txt"))
    return updated


def _run_author_repeated(
    command: list[str],
    *,
    output_json: Path,
    timeout_sec: int | None,
    warmup: int,
    repeat: int,
) -> dict[str, object]:
    runs = []
    for iteration in range(int(warmup) + int(repeat)):
        is_warmup = iteration < int(warmup)
        iteration_json = output_json.with_name(f"{output_json.stem}_iter{iteration}{output_json.suffix}")
        iteration_command = _command_with_output_json(command, iteration_json)
        run_result = _run_one(
            iteration_command,
            output_json=iteration_json,
            timeout_sec=timeout_sec,
        )
        payload = _read_json(iteration_json)
        elapsed = None if payload is None else payload.get("elapsed_sec")
        runs.append(
            {
                "iteration": iteration,
                "is_warmup": is_warmup,
                "run_result": run_result,
                "elapsed_sec": None if elapsed is None else float(elapsed),
                "overlay_output_digest": _overlay_output_digest(_overlay_output_path_from_command(iteration_command)),
            }
        )
    hot_elapsed = [
        float(run["elapsed_sec"])
        for run in runs
        if not run["is_warmup"] and run["elapsed_sec"] is not None and run["run_result"]["completed"]
    ]
    hot_overlay_digests = [
        run["overlay_output_digest"]
        for run in runs
        if not run["is_warmup"] and run["run_result"]["completed"] and run.get("overlay_output_digest") is not None
    ]
    hot_overlay_shas = [str(digest["sha256"]) for digest in hot_overlay_digests if isinstance(digest, dict)]
    payload = {
        "schema": "rtdl.rayjoin.section57_overlay_matrix.author_repeated.v1",
        "command_template": command,
        "warmup": int(warmup),
        "repeat": int(repeat),
        "elapsed_sec": statistics.median(hot_elapsed) if hot_elapsed else None,
        "hot_median_sec": statistics.median(hot_elapsed) if hot_elapsed else None,
        "hot_min_sec": min(hot_elapsed) if hot_elapsed else None,
        "hot_max_sec": max(hot_elapsed) if hot_elapsed else None,
        "overlay_output_digest": hot_overlay_digests[0] if hot_overlay_digests else None,
        "overlay_output_digest_stable": len(set(hot_overlay_shas)) <= 1 if hot_overlay_shas else None,
        "runs": runs,
    }
    _write_json(output_json, payload)
    return {
        "command": command,
        "exit_code": 0 if len(hot_elapsed) == int(repeat) else None,
        "elapsed_sec": sum(
            float(run["run_result"]["elapsed_sec"])
            for run in runs
            if run["run_result"].get("elapsed_sec") is not None
        ),
        "output_json": str(output_json),
        "stdout_path": None,
        "stderr_path": None,
        "completed": len(hot_elapsed) == int(repeat),
        "timed_out": any(bool(run["run_result"].get("timed_out")) for run in runs),
    }


def _extract_author_total(payload: dict[str, object] | None) -> float | None:
    if payload is None:
        return None
    value = payload.get("elapsed_sec")
    return None if value is None else float(value)


def _extract_author_overlay_digest(payload: dict[str, object] | None) -> dict[str, object] | None:
    if payload is None:
        return None
    digest = payload.get("overlay_output_digest")
    return digest if isinstance(digest, dict) else None


def _extract_rtdl_total(payload: dict[str, object] | None, backend: str) -> tuple[float | None, int | None]:
    if payload is None:
        return None, None
    result: dict[str, object]
    if "results" in payload:
        result = (payload.get("results") or {}).get(backend) or {}
    else:
        result = payload
    total = result.get("total_median_sec")
    if total is None:
        total = (result.get("phase_seconds") or {}).get("total_sec")
    lsi = result.get("lsi") or {}
    count = lsi.get("intersection_count")
    return (None if total is None else float(total), None if count is None else int(count))


def _extract_rtdl_overlay_digest(payload: dict[str, object] | None, backend: str) -> dict[str, object] | None:
    if payload is None:
        return None
    if "results" in payload:
        result = (payload.get("results") or {}).get(backend) or {}
    else:
        result = payload
    output = result.get("output") or {}
    if not isinstance(output, dict):
        return None
    path = output.get("path")
    if not path:
        return None
    return _overlay_output_digest(Path(str(path)))


def _digest_match(left: dict[str, object] | None, right: dict[str, object] | None) -> bool | None:
    left_sha = None if left is None else left.get("sha256")
    right_sha = None if right is None else right.get("sha256")
    if left_sha is None or right_sha is None:
        return None
    return str(left_sha) == str(right_sha)


def _extract_v4_numba(payload: dict[str, object] | None) -> dict[str, object]:
    if payload is None:
        return {
            "present": False,
            "claim_classification": None,
            "selected_plan_id": None,
            "total_sec": None,
            "correctness_status": None,
        }
    selected = payload.get("selected_plan") or {}
    if not isinstance(selected, dict):
        selected = {}
    total = selected.get("measured_total_sec")
    return {
        "present": True,
        "claim_classification": payload.get("claim_classification"),
        "selected_plan_id": selected.get("plan_id"),
        "total_sec": None if total is None else float(total),
        "correctness_status": selected.get("correctness_status"),
    }


def summarize_results(args: argparse.Namespace) -> dict[str, object]:
    pair_ids = _split_csv(args.pairs, default=[pair.pair_id for pair in paper_pairs()])
    rows = []
    for case in _overlay_cases(pair_ids):
        paths = _artifact_paths(args.output_dir, case.pair.pair_id)
        author = _read_json(paths["author_rt"])
        optix = _read_json(paths["rtdl_optix"])
        embree = _read_json(paths["rtdl_embree"])
        v4_numba = _read_json(paths["v4_numba"])
        optix_total, optix_count = _extract_rtdl_total(optix, "optix")
        embree_total, embree_count = _extract_rtdl_total(embree, "embree")
        v4_numba_summary = _extract_v4_numba(v4_numba)
        author_overlay_digest = _extract_author_overlay_digest(author)
        optix_overlay_digest = _extract_rtdl_overlay_digest(optix, "optix")
        embree_overlay_digest = _extract_rtdl_overlay_digest(embree, "embree")
        rows.append(
            {
                "pair_id": case.pair.pair_id,
                "paper_label": case.pair.paper_label,
                "paper_rayjoin_processing_sec": RAYJOIN_SECTION57_TABLE4_SECONDS["RayJoin*"][case.pair.pair_id][0],
                "paper_rayjoin_preprocessing_sec": RAYJOIN_SECTION57_TABLE4_SECONDS["RayJoin*"][case.pair.pair_id][1],
                "author_rt_process_sec": _extract_author_total(author),
                "rtdl_optix_total_sec": optix_total,
                "rtdl_optix_lsi_count": optix_count,
                "rtdl_embree_total_sec": embree_total,
                "rtdl_embree_lsi_count": embree_count,
                "v4_numba_total_sec": v4_numba_summary["total_sec"],
                "v4_numba_claim_classification": v4_numba_summary["claim_classification"],
                "v4_numba_selected_plan_id": v4_numba_summary["selected_plan_id"],
                "v4_numba_correctness_status": v4_numba_summary["correctness_status"],
                "author_overlay_output_digest": author_overlay_digest,
                "rtdl_optix_overlay_output_digest": optix_overlay_digest,
                "rtdl_embree_overlay_output_digest": embree_overlay_digest,
                "rtdl_optix_author_raw_output_digest_match": _digest_match(author_overlay_digest, optix_overlay_digest),
                "rtdl_embree_author_raw_output_digest_match": _digest_match(author_overlay_digest, embree_overlay_digest),
                "rtdl_optix_embree_raw_output_digest_match": _digest_match(optix_overlay_digest, embree_overlay_digest),
                "complete": (
                    author is not None
                    and optix is not None
                    and embree is not None
                    and v4_numba_summary["present"]
                    and v4_numba_summary["selected_plan_id"] is not None
                ),
                "paths": {key: str(value) for key, value in paths.items()},
            }
        )
    complete = sum(1 for row in rows if row["complete"])
    return {
        "schema": "rtdl.rayjoin.section57_overlay_matrix.summary.v1",
        "dataset_root": str(args.dataset_root),
        "output_dir": str(args.output_dir),
        "coverage": {
            "overlay_pairs_total": len(rows),
            "overlay_pairs_complete": complete,
            "overlay_pairs_incomplete": len(rows) - complete,
        },
        "timing_caveat": (
            "Paper Table 4 values are historical reference numbers. Local author_rt rows are "
            "measured process wall times. RTDL rows are warm-cache medians under the selected protocol."
        ),
        "correctness_caveat": (
            "Raw overlay-output digest matches are byte-level checks for runs that requested "
            "--assemble-overlay-output. They are stronger than count-only checks, but they are "
            "not a substitute for a geometry/topology equivalence proof when output order or "
            "format intentionally differs."
        ),
        "rows": rows,
    }


def render_plan_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# RayJoin Section 5.7 Overlay 8/8 Execution Plan",
        "",
        f"Dataset root: `{payload['dataset_root']}`",
        f"Input provenance: `{payload['input_provenance']}`",
        f"Preprocessed source: {payload['preprocessed_share_url']}",
        "",
        "## Coverage",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in payload["coverage"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Overlay Pairs",
            "",
            "| Pair | Exact Inputs Ready | Blocker | Paper RayJoin Processing (Preprocess) Sec |",
            "|---|---:|---|---:|",
        ]
    )
    for row in payload["rows"]:
        rayjoin = row["paper_table4_seconds"]["RayJoin*"]
        paper = f"{rayjoin['processing_sec']} ({rayjoin['preprocessing_sec']})"
        lines.append(f"| {row['paper_label']} | {row['exact_input_ready']} | {row['blocker'] or ''} | {paper} |")
    return "\n".join(lines).rstrip() + "\n"


def render_summary_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# RayJoin Section 5.7 Overlay 8/8 Summary",
        "",
        f"Dataset root: `{payload['dataset_root']}`",
        "",
        "Timing caveat: " + str(payload["timing_caveat"]),
        "",
        "Correctness caveat: " + str(payload["correctness_caveat"]),
        "",
        "## Coverage",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in payload["coverage"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Matrix",
            "",
            "| Pair | Paper RayJoin Processing (Preprocess) | Local Author RT Process | RTDL OptiX Total | RTDL Embree Total | V4+Numba Total | V4+Numba Status | RTDL LSI Count Match | OptiX Raw Output = Author | Embree Raw Output = Author | OptiX Raw Output = Embree | Complete |",
            "|---|---:|---:|---:|---:|---:|---|---|---|---|---|---:|",
        ]
    )
    for row in payload["rows"]:
        paper = f"{row['paper_rayjoin_processing_sec']} ({row['paper_rayjoin_preprocessing_sec']})"
        author = "" if row["author_rt_process_sec"] is None else f"{row['author_rt_process_sec']:.6f}"
        optix = "" if row["rtdl_optix_total_sec"] is None else f"{row['rtdl_optix_total_sec']:.6f}"
        embree = "" if row["rtdl_embree_total_sec"] is None else f"{row['rtdl_embree_total_sec']:.6f}"
        v4_numba = "" if row["v4_numba_total_sec"] is None else f"{row['v4_numba_total_sec']:.6f}"
        v4_numba_status = row["v4_numba_claim_classification"] or ""
        count_match = (
            ""
            if row["rtdl_optix_lsi_count"] is None or row["rtdl_embree_lsi_count"] is None
            else str(row["rtdl_optix_lsi_count"] == row["rtdl_embree_lsi_count"])
        )
        optix_author_digest = "" if row["rtdl_optix_author_raw_output_digest_match"] is None else str(row["rtdl_optix_author_raw_output_digest_match"])
        embree_author_digest = "" if row["rtdl_embree_author_raw_output_digest_match"] is None else str(row["rtdl_embree_author_raw_output_digest_match"])
        optix_embree_digest = "" if row["rtdl_optix_embree_raw_output_digest_match"] is None else str(row["rtdl_optix_embree_raw_output_digest_match"])
        lines.append(
            f"| {row['paper_label']} | {paper} | {author} | {optix} | {embree} | "
            f"{v4_numba} | `{v4_numba_status}` | {count_match} | {optix_author_digest} | "
            f"{embree_author_digest} | {optix_embree_digest} | {row['complete']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def cmd_plan(args: argparse.Namespace) -> None:
    payload = build_plan(args)
    _write_json(args.output_json, payload)
    if args.output_md is not None:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_plan_markdown(payload), encoding="utf-8")


def cmd_run(args: argparse.Namespace) -> None:
    plan = build_plan(args)
    attempts = []
    selected_implementations = set(_split_csv(args.implementations, default=IMPLEMENTATIONS))
    for row in plan["rows"]:
        if not row["exact_input_ready"] and not args.allow_missing_inputs:
            attempts.append(
                {
                    "pair_id": row["pair_id"],
                    "status": "skipped_missing_inputs",
                    "blocker": row["blocker"],
                }
            )
            continue
        case = _overlay_cases((row["pair_id"],))[0]
        paths = {key: Path(value) for key, value in row["result_paths"].items()}
        commands = row["commands"]
        for implementation in IMPLEMENTATIONS:
            if implementation not in selected_implementations:
                continue
            command = commands.get(implementation)
            if command is None:
                attempts.append(
                    {
                        "pair_id": row["pair_id"],
                        "implementation": implementation,
                        "status": "skipped_missing_command",
                    }
                )
                continue
            if args.dry_run:
                attempts.append(
                    {
                        "pair_id": row["pair_id"],
                        "implementation": implementation,
                        "status": "dry_run",
                        "command": command,
                    }
                )
                continue
            if implementation == "author_rt":
                run_result = _run_author_repeated(
                    command,
                    output_json=paths[implementation],
                    timeout_sec=args.timeout_sec,
                    warmup=args.author_warmup,
                    repeat=args.author_repeat,
                )
            else:
                run_result = _run_one(command, output_json=paths[implementation], timeout_sec=args.timeout_sec)
            attempts.append(
                {
                    "pair_id": row["pair_id"],
                    "implementation": implementation,
                    "status": "completed" if run_result["completed"] else "failed",
                    **run_result,
                }
            )
    run_payload = {
        "schema": "rtdl.rayjoin.section57_overlay_matrix.run.v1",
        "plan": plan,
        "attempts": attempts,
    }
    _write_json(args.run_json, run_payload)
    summary = summarize_results(args)
    _write_json(args.summary_json, summary)
    if args.summary_md is not None:
        args.summary_md.parent.mkdir(parents=True, exist_ok=True)
        args.summary_md.write_text(render_summary_markdown(summary), encoding="utf-8")


def cmd_summarize(args: argparse.Namespace) -> None:
    payload = summarize_results(args)
    _write_json(args.output_json, payload)
    if args.output_md is not None:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_summary_markdown(payload), encoding="utf-8")


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--pairs")
    parser.add_argument(
        "--implementations",
        default=",".join(IMPLEMENTATIONS),
        help="Comma-separated subset of author_rt,rtdl_optix,rtdl_embree,v4_numba.",
    )
    parser.add_argument(
        "--input-provenance",
        choices=("paper_preprocessed_cdb", "same_source_regenerated_cdb", "fixture_or_synthetic"),
        default="paper_preprocessed_cdb",
    )
    parser.add_argument("--query-exec", type=Path)
    parser.add_argument("--polyover-exec", type=Path)
    parser.add_argument("--mode", choices=("grid", "lbvh", "rt"), default="rt")
    parser.add_argument("--serialize-prefix", default="/dev/shm")
    parser.add_argument("--grid-size", type=int, default=15000)
    parser.add_argument("--xsect-factor", default="0.1")
    parser.add_argument("--enlarge", default="3.5")
    parser.add_argument("--author-warmup", type=int, default=5)
    parser.add_argument("--author-repeat", type=int, default=5)
    parser.add_argument("--rtdl-warmup", type=int, default=1)
    parser.add_argument("--rtdl-repeat", type=int, default=3)
    parser.add_argument("--packed-cache-dir", type=Path)
    parser.add_argument("--disable-packed-cache", action="store_true")
    parser.add_argument("--assemble-overlay-output", action="store_true")
    parser.add_argument("--v4-numba-select", default="fastest_valid")
    parser.add_argument("--v4-numba-skip-runtime-probe", action="store_true")
    parser.add_argument("--v4-numba-section57-device-columns-ready", action="store_true")
    parser.add_argument("--v4-numba-measurements", type=Path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or plan the full RayJoin Section 5.7 8/8 overlay matrix.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan")
    _add_common(plan)
    plan.add_argument("--output-json", required=True, type=Path)
    plan.add_argument("--output-md", type=Path)
    plan.set_defaults(func=cmd_plan)

    run = subparsers.add_parser("run")
    _add_common(run)
    run.add_argument("--allow-missing-inputs", action="store_true")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--timeout-sec", type=int)
    run.add_argument("--run-json", required=True, type=Path)
    run.add_argument("--summary-json", required=True, type=Path)
    run.add_argument("--summary-md", type=Path)
    run.set_defaults(func=cmd_run)

    summarize = subparsers.add_parser("summarize")
    _add_common(summarize)
    summarize.add_argument("--output-json", required=True, type=Path)
    summarize.add_argument("--output-md", type=Path)
    summarize.set_defaults(func=cmd_summarize)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
