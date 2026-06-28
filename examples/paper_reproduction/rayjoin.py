from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.benchmark_apps._support._repo_bootstrap import ensure_repo_src_on_path

ensure_repo_src_on_path()

from rtdsl._example_support.benchmark_harness_compat import run_archived_harness
from rtdsl.rayjoin_numba_auto_planner import section57_polygon_overlay
from rtdsl.rayjoin_numba_auto_planner import write_section57_numba_auto_evidence


DEFAULT_SECTION57_DATASET_ROOT = "data/rayjoin_section57_cdb"
DEFAULT_SECTION57_OUTPUT_DIR = "artifacts/rayjoin_section57"


def _payload() -> dict[str, object]:
    return {
        "status": "ok",
        "paper_entry": "RayJoin",
        "benchmark_app": "examples/benchmark_apps/spatial_rayjoin/v4_app.py",
        "paper_suite": "src/rtdsl/rayjoin_paper_suite.py",
        "learn_first": "examples/tutorial_programs/rayjoin_topology_intro.py",
        "scope_note": "examples/paper_reproduction/paper_reproduction_scope.md",
        "contract": "docs/research/rayjoin/rayjoin_exact_paper_reproduction_contract.md",
        "default_behavior": "explain_paper_route",
        "section57_overlay_plan": (
            "python examples/paper_reproduction/rayjoin.py --section57-plan "
            "--dataset-root data/rayjoin_section57_cdb"
        ),
        "section57_overlay_run": (
            "python examples/paper_reproduction/rayjoin.py --section57-run "
            "--dataset-root data/rayjoin_section57_cdb "
            "--query-exec /workspace/RayJoin_fresh/release/bin/query_exec "
            "--polyover-exec /workspace/RayJoin_fresh/release/bin/polyover_exec"
        ),
        "v2_14_comparison": (
            "python examples/paper_reproduction/rayjoin.py --section57-compare-v214 --json"
        ),
        "v4_numba_auto_planner": (
            "python examples/paper_reproduction/rayjoin.py --section57-auto-numba "
            "--dataset-root data/rayjoin_section57_cdb --partner numba --select fastest_valid"
        ),
        "run_harness": "python examples/paper_reproduction/rayjoin.py --run-harness -- --help",
    }


def _section57_script() -> Path:
    return ROOT / "scripts" / "rayjoin_section57_overlay_matrix.py"


def _section57_common_args(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        str(_section57_script()),
        args._section57_command,
        "--dataset-root",
        str(args.dataset_root),
        "--output-dir",
        str(args.output_dir),
        "--implementations",
        args.implementations,
        "--input-provenance",
        args.input_provenance,
        "--author-warmup",
        str(args.author_warmup),
        "--author-repeat",
        str(args.author_repeat),
        "--rtdl-warmup",
        str(args.rtdl_warmup),
        "--rtdl-repeat",
        str(args.rtdl_repeat),
    ]
    if args.pairs:
        command.extend(["--pairs", args.pairs])
    if args.query_exec:
        command.extend(["--query-exec", str(args.query_exec)])
    if args.polyover_exec:
        command.extend(["--polyover-exec", str(args.polyover_exec)])
    if args.packed_cache_dir:
        command.extend(["--packed-cache-dir", str(args.packed_cache_dir)])
    if args.disable_packed_cache:
        command.append("--disable-packed-cache")
    if args.assemble_overlay_output:
        command.append("--assemble-overlay-output")
    return command


def _run_section57_plan(args: argparse.Namespace) -> int:
    args._section57_command = "plan"
    output_json = args.output_json or (Path(args.output_dir) / "section57_overlay_plan.json")
    output_md = args.output_md or (Path(args.output_dir) / "section57_overlay_plan.md")
    command = _section57_common_args(args)
    command.extend(["--output-json", str(output_json), "--output-md", str(output_md)])
    return subprocess.call(command, cwd=ROOT)


def _run_section57_run(args: argparse.Namespace) -> int:
    args._section57_command = "run"
    output_dir = Path(args.output_dir)
    command = _section57_common_args(args)
    if args.allow_missing_inputs:
        command.append("--allow-missing-inputs")
    if args.dry_run:
        command.append("--dry-run")
    if args.timeout_sec is not None:
        command.extend(["--timeout-sec", str(args.timeout_sec)])
    command.extend(
        [
            "--run-json",
            str(args.run_json or (output_dir / "section57_overlay_run.json")),
            "--summary-json",
            str(args.summary_json or (output_dir / "section57_overlay_summary.json")),
            "--summary-md",
            str(args.summary_md or (output_dir / "section57_overlay_summary.md")),
        ]
    )
    return subprocess.call(command, cwd=ROOT)


def _run_section57_summary(args: argparse.Namespace) -> int:
    args._section57_command = "summarize"
    output_dir = Path(args.output_dir)
    command = _section57_common_args(args)
    command.extend(
        [
            "--output-json",
            str(args.output_json or (output_dir / "section57_overlay_summary.json")),
            "--output-md",
            str(args.output_md or (output_dir / "section57_overlay_summary.md")),
        ]
    )
    return subprocess.call(command, cwd=ROOT)


def _comparison_payload(args: argparse.Namespace) -> dict[str, object]:
    pairs = args.pairs or "all_section57_pairs_8_of_8"
    v4_command = [
        "python",
        "examples/paper_reproduction/rayjoin.py",
        "--section57-run",
        "--dataset-root",
        str(args.dataset_root),
        "--output-dir",
        str(args.output_dir),
        "--pairs",
        pairs,
        "--query-exec",
        str(args.query_exec or "/workspace/RayJoin_fresh/release/bin/query_exec"),
        "--polyover-exec",
        str(args.polyover_exec or "/workspace/RayJoin_fresh/release/bin/polyover_exec"),
    ]
    v214_command = [
        "python",
        "scripts/rtdl_v2_14_benchmark_run_plan.py",
        "--overlay-dataset-root",
        str(args.dataset_root),
        "--rayjoin-query-exec",
        str(args.query_exec or "/workspace/RayJoin_fresh/release/bin/query_exec"),
        "--rayjoin-polyover-exec",
        str(args.polyover_exec or "/workspace/RayJoin_fresh/release/bin/polyover_exec"),
        "--overlay-pairs",
        pairs,
    ]
    return {
        "status": "ok",
        "comparison": "RayJoin Section 5.7 polygon overlay",
        "v2_14_surface": "historical RTDL exact-suite run plan for Section 5.7 overlay",
        "v4_0_surface": "current public paper-reproduction wrapper over the RTDL exact-suite runner",
        "important_boundary": (
            "V4.0 includes the V2.14 RayJoin exact-suite capability. The fair "
            "performance comparison uses the same dataset root, same author binaries, "
            "same pair selection, and separates author_rt, rtdl_optix, and rtdl_embree."
        ),
        "not_a_claim": (
            "This wrapper does not claim full 8/8 reproduction unless all exact inputs "
            "are present and the summary records complete results."
        ),
        "pairs": pairs,
        "v4_0_command": v4_command,
        "v2_14_plan_command": v214_command,
        "contract": "docs/research/rayjoin/rayjoin_exact_paper_reproduction_contract.md",
    }


def _print_comparison(args: argparse.Namespace) -> int:
    payload = _comparison_payload(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print("RayJoin Section 5.7 polygon overlay comparison")
    print(f"  V2.14 surface: {payload['v2_14_surface']}")
    print(f"  V4.0 surface:  {payload['v4_0_surface']}")
    print(f"  Boundary:      {payload['important_boundary']}")
    print("  V4.0 command:")
    print("    " + " ".join(str(part) for part in payload["v4_0_command"]))
    print("  V2.14 run-plan command:")
    print("    " + " ".join(str(part) for part in payload["v2_14_plan_command"]))
    return 0


def _run_section57_auto_numba(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    output_json = args.output_json or (output_dir / "section57_numba_auto_evidence.json")
    output_md = args.output_md or (output_dir / "section57_numba_auto_evidence.md")
    payload = section57_polygon_overlay(
        dataset_root=args.dataset_root,
        partner=args.partner,
        select=args.select,
        pairs=args.pairs,
        query_exec=args.query_exec,
        polyover_exec=args.polyover_exec,
        output_dir=args.output_dir,
        input_provenance=args.input_provenance,
        warmup=args.rtdl_warmup,
        repeat=args.rtdl_repeat,
        check_runtime=not args.skip_runtime_probe,
    )
    write_section57_numba_auto_evidence(
        payload,
        output_json=output_json,
        output_md=output_md,
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("RayJoin Section 5.7 V4+Numba auto-primitive planner")
        print(f"  claim classification: {payload['claim_classification']}")
        print(f"  evidence json: {output_json}")
        print(f"  evidence md:   {output_md}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Explain or run the RayJoin paper-oriented RTDL route.")
    parser.add_argument("--json", action="store_true", help="Print the route description as JSON.")
    parser.add_argument("--run-harness", action="store_true", help="Forward remaining arguments to the full benchmark runner.")
    parser.add_argument("--section57-plan", action="store_true", help="Generate the RayJoin Section 5.7 overlay plan.")
    parser.add_argument("--section57-run", action="store_true", help="Run the RayJoin Section 5.7 overlay matrix.")
    parser.add_argument("--section57-summary", action="store_true", help="Summarize existing Section 5.7 overlay result files.")
    parser.add_argument("--section57-compare-v214", action="store_true", help="Show the V2.14 vs V4.0 Section 5.7 comparison protocol.")
    parser.add_argument("--section57-auto-numba", action="store_true", help="Plan the V4+Numba auto-primitive route for Section 5.7.")
    parser.add_argument("--dataset-root", default=DEFAULT_SECTION57_DATASET_ROOT, help="Root containing RayJoin point_cdb inputs.")
    parser.add_argument("--output-dir", default=DEFAULT_SECTION57_OUTPUT_DIR, help="Directory for Section 5.7 artifacts.")
    parser.add_argument("--pairs", help="Comma-separated overlay pair ids; default is all eight Section 5.7 pairs.")
    parser.add_argument("--partner", default="numba", help="Partner for --section57-auto-numba; this route supports numba.")
    parser.add_argument("--select", default="fastest_valid", help="Selection policy for --section57-auto-numba.")
    parser.add_argument("--implementations", default="author_rt,rtdl_optix,rtdl_embree")
    parser.add_argument(
        "--input-provenance",
        choices=("paper_preprocessed_cdb", "same_source_regenerated_cdb", "fixture_or_synthetic"),
        default="paper_preprocessed_cdb",
    )
    parser.add_argument("--query-exec", help="Path to RayJoin author query_exec.")
    parser.add_argument("--polyover-exec", help="Path to RayJoin author polyover_exec.")
    parser.add_argument("--author-warmup", type=int, default=5)
    parser.add_argument("--author-repeat", type=int, default=5)
    parser.add_argument("--rtdl-warmup", type=int, default=1)
    parser.add_argument("--rtdl-repeat", type=int, default=3)
    parser.add_argument("--packed-cache-dir")
    parser.add_argument("--disable-packed-cache", action="store_true")
    parser.add_argument("--assemble-overlay-output", action="store_true")
    parser.add_argument("--allow-missing-inputs", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-runtime-probe", action="store_true", help="Do not probe local Numba CUDA availability.")
    parser.add_argument("--timeout-sec", type=int)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--run-json", type=Path)
    parser.add_argument("--summary-json", type=Path)
    parser.add_argument("--summary-md", type=Path)
    parser.add_argument("harness_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.run_harness:
        return run_archived_harness("spatial_rayjoin", args.harness_args)
    if args.section57_plan:
        return _run_section57_plan(args)
    if args.section57_run:
        return _run_section57_run(args)
    if args.section57_summary:
        return _run_section57_summary(args)
    if args.section57_compare_v214:
        return _print_comparison(args)
    if args.section57_auto_numba:
        return _run_section57_auto_numba(args)

    payload = _payload()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("RayJoin paper-oriented route")
        print(f"  benchmark app: {payload['benchmark_app']}")
        print(f"  paper suite: {payload['paper_suite']}")
        print(f"  learn first: {payload['learn_first']}")
        print(f"  scope note: {payload['scope_note']}")
        print(f"  full runner: {payload['run_harness']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
