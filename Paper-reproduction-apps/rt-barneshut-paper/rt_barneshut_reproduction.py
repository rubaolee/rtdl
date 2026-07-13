from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
MANIFEST = Path(__file__).resolve().parent / "data" / "manifest.json"


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def status_payload() -> dict[str, Any]:
    manifest = load_manifest()
    current = manifest["current_rtdl_status"]
    bounded_complete = bool(current.get("bounded_same_input_reproduction_complete", False))
    return {
        "project": "rt-barneshut-paper",
        "status": "bounded_same_input_complete" if bounded_complete else "in_progress",
        "paper": manifest["paper"],
        "author_artifact": manifest["author_artifact"],
        "paper_reproduction_complete": bool(current["paper_reproduction_complete"]),
        "bounded_same_input_reproduction_complete": bounded_complete,
        "same_input_comparator_closed": bounded_complete,
        "existing_rtdl_benchmark_app": current["existing_benchmark_app"],
        "known_gap": current["known_gap"],
        "completed_evidence": current.get("completed_evidence"),
        "completion_audit_evidence": current.get("completion_audit_evidence"),
        "same_input_author_rtdl_match": current.get("same_input_author_rtdl_match"),
        "narrow_force_kernel_ratio_rtdl_over_author": current.get("narrow_force_kernel_ratio_rtdl_over_author"),
        "performance_phase_context": current.get("performance_phase_context"),
        "next_required_evidence": manifest["completion_gates"],
        "claim_boundary": (
            "bounded same-input AuthorOfficial comparator is closed. The full paper "
            "Section 5 evaluation is not complete. The "
            "reported performance ratio is a narrow force-kernel phase comparison, "
            "not whole-program runtime parity; prep and reported whole-program "
            "envelopes are reported separately."
        ),
    }


def run_rtdl_diagnostic(args: argparse.Namespace) -> dict[str, Any]:
    diagnostic = ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py"
    if not diagnostic.exists():
        raise FileNotFoundError(diagnostic)
    out = Path(args.output or Path("rt_barneshut_rtdl_diagnostic.json")).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    force_out = Path(args.force_output).resolve() if args.force_output else out.with_name("rtdl_forces.txt")
    force_output_scale = float(args.force_output_scale)
    if importlib.util.find_spec("torch") is None:
        payload = {
            "project": "rt-barneshut-paper",
            "mode": "rtdl_3d_diagnostic",
            "status": "blocked_missing_runtime_dependency",
            "missing_dependency": "torch",
            "paper_reproduction_complete": False,
            "same_input_author_comparator": False,
            "force_output": str(force_out),
            "force_output_scale": force_output_scale,
            "prepared_arrays_json": None if args.prepared_arrays_json is None else str(Path(args.prepared_arrays_json).resolve()),
            "traversal_policy": args.traversal_policy,
            "next_action": "Run this mode on a CUDA Linux environment with PyTorch installed.",
        }
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"missing runtime dependency: torch; wrote {out}", file=sys.stderr)
        raise SystemExit(2)
    cmd = [
        sys.executable,
        str(diagnostic),
        "--body-count",
        str(args.body_count),
        "--theta",
        str(args.theta),
        "--softening",
        str(args.softening),
        "--traversal-policy",
        str(args.traversal_policy),
        "--repeats",
        str(args.repeats),
        "--json-out",
        str(out),
        "--force-out",
        str(force_out),
        "--force-output-scale",
        str(force_output_scale),
    ]
    if args.input_file:
        cmd.extend(["--input-file", str(Path(args.input_file).resolve())])
    if args.prepared_arrays_json:
        cmd.extend(["--prepared-arrays-json", str(Path(args.prepared_arrays_json).resolve())])
    if args.skip_reference:
        cmd.append("--skip-reference")
    subprocess.run(cmd, cwd=ROOT, check=True)
    payload = json.loads(out.read_text(encoding="utf-8"))
    wrapper = {
        "project": "rt-barneshut-paper",
        "mode": "rtdl_3d_diagnostic",
        "delegated_script": str(diagnostic.relative_to(ROOT)),
        "diagnostic_output": str(out),
        "force_output": str(force_out),
        "force_output_scale": force_output_scale,
        "force_output_exists": force_out.exists(),
        "prepared_arrays_json": None if args.prepared_arrays_json is None else str(Path(args.prepared_arrays_json).resolve()),
        "traversal_policy": args.traversal_policy,
        "paper_reproduction_complete": False,
        "same_input_author_comparator": False,
        "same_tree_contract_as_authors": bool(
            payload.get("metadata", {}).get("same_tree_contract_as_authors", False)
        ),
        "rtdl_payload": payload,
    }
    out.write_text(json.dumps(wrapper, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return wrapper


def _load_aggregate_hierarchy_adapter():
    module_path = Path(__file__).resolve().parent / "aggregate_hierarchy_adapter.py"
    spec = importlib.util.spec_from_file_location("rt_barneshut_aggregate_hierarchy_adapter_cli", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load aggregate hierarchy adapter from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_force_compare_module():
    module_path = Path(__file__).resolve().parent / "scripts" / "compare_force_outputs.py"
    spec = importlib.util.spec_from_file_location("rt_barneshut_force_compare_cli", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load force comparator from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_aggregate_numba_parity(args: argparse.Namespace) -> dict[str, Any]:
    if not args.prepared_arrays_json:
        raise SystemExit("--prepared-arrays-json is required for aggregate-numba-parity mode")
    adapter = _load_aggregate_hierarchy_adapter()
    prepared_path = Path(args.prepared_arrays_json).resolve()
    try:
        parity = adapter.read_prepared_arrays_and_run_generic_numba_parity(
            prepared_path,
            max_ratio=float(args.theta),
            softening=float(args.softening),
            rel_tol=float(args.parity_rel_tol),
            abs_tol=float(args.parity_abs_tol),
        )
    except RuntimeError as exc:
        out = Path(args.output or Path("rt_barneshut_aggregate_numba_parity.json")).resolve()
        payload = {
            "project": "rt-barneshut-paper",
            "mode": "aggregate_numba_parity",
            "status": "blocked_missing_runtime_dependency",
            "error": str(exc),
            "prepared_arrays_json": str(prepared_path),
            "paper_reproduction_complete": False,
            "claim_boundary": (
                "app_owned_public_api_parity_gate",
                "not_author_binary_comparator",
                "not_performance_claim",
            ),
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"missing runtime dependency for aggregate-numba-parity; wrote {out}", file=sys.stderr)
        raise SystemExit(2)
    return {
        "project": "rt-barneshut-paper",
        "mode": "aggregate_numba_parity",
        "prepared_arrays_json": str(prepared_path),
        "paper_reproduction_complete": False,
        "same_input_author_comparator": False,
        "generic_public_rtdl_api_used": True,
        "parity": parity,
    }


def run_aggregate_numba_force_output(args: argparse.Namespace) -> dict[str, Any]:
    if not args.prepared_arrays_json:
        raise SystemExit("--prepared-arrays-json is required for aggregate-numba-force-output mode")
    adapter = _load_aggregate_hierarchy_adapter()
    prepared_path = Path(args.prepared_arrays_json).resolve()
    out = Path(args.output or Path("rt_barneshut_aggregate_numba_force_bridge.json")).resolve()
    force_out = Path(args.force_output).resolve() if args.force_output else out.with_name("aggregate_numba_forces.txt")
    try:
        bridge = adapter.read_prepared_arrays_and_run_generic_numba_force_bridge(
            prepared_path,
            max_ratio=float(args.theta),
            softening=float(args.softening),
            force_output_scale=float(args.force_output_scale),
            force_output=force_out,
            rel_tol=float(args.parity_rel_tol),
            abs_tol=float(args.parity_abs_tol),
        )
    except RuntimeError as exc:
        payload = {
            "project": "rt-barneshut-paper",
            "mode": "aggregate_numba_force_output",
            "status": "blocked_missing_runtime_dependency",
            "error": str(exc),
            "prepared_arrays_json": str(prepared_path),
            "force_output": str(force_out),
            "paper_reproduction_complete": False,
            "same_input_author_comparator": False,
            "claim_boundary": (
                "app_owned_force_output_bridge",
                "not_author_binary_comparator",
                "not_performance_claim",
            ),
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"missing runtime dependency for aggregate-numba-force-output; wrote {out}", file=sys.stderr)
        raise SystemExit(2)
    return {
        "project": "rt-barneshut-paper",
        "mode": "aggregate_numba_force_output",
        "prepared_arrays_json": str(prepared_path),
        "force_output": str(force_out),
        "force_output_exists": force_out.exists(),
        "paper_reproduction_complete": False,
        "same_input_author_comparator": False,
        "generic_public_rtdl_api_used": True,
        "bridge": bridge,
    }


def run_aggregate_numba_force_compare(args: argparse.Namespace) -> dict[str, Any]:
    if not args.prepared_arrays_json:
        raise SystemExit("--prepared-arrays-json is required for aggregate-numba-force-compare mode")
    if not args.expected_force_output:
        raise SystemExit("--expected-force-output is required for aggregate-numba-force-compare mode")

    payload = run_aggregate_numba_force_output(args)
    comparator = _load_force_compare_module()
    expected = Path(args.expected_force_output).resolve()
    candidate = Path(payload["force_output"]).resolve()
    comparison = comparator.compare_force_outputs(
        expected,
        candidate,
        rtol=float(args.force_compare_rtol),
        atol=float(args.force_compare_atol),
    )
    payload.update(
        {
            "mode": "aggregate_numba_force_compare",
            "expected_force_output": str(expected),
            "candidate_force_output": str(candidate),
            "same_input_author_comparator": bool(comparison["matched"]),
            "paper_reproduction_complete": False,
            "force_comparison": comparison,
            "claim_boundary": (
                "app_owned_same_input_scalar_force_comparator_gate",
                "uses_public_generic_rtdl_aggregate_hierarchy_api",
                "compares_scalar_force_files_only",
                "not_full_paper_reproduction",
                "not_performance_claim",
            ),
        }
    )
    return payload


def write_payload(payload: dict[str, Any], output: str | None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description="RT-BarnesHut paper-reproduction project entry point.")
    parser.add_argument(
        "--mode",
        choices=(
            "status",
            "rtdl-3d-diagnostic",
            "aggregate-numba-parity",
            "aggregate-numba-force-output",
            "aggregate-numba-force-compare",
        ),
        default="status",
    )
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--force-output", type=str, default=None)
    parser.add_argument("--expected-force-output", type=str, default=None)
    parser.add_argument("--force-output-scale", type=float, default=0.1)
    parser.add_argument("--force-compare-rtol", type=float, default=1.0e-4)
    parser.add_argument("--force-compare-atol", type=float, default=1.0e-4)
    parser.add_argument("--body-count", type=int, default=32768)
    parser.add_argument("--input-file", type=str, default=None)
    parser.add_argument("--prepared-arrays-json", type=str, default=None)
    parser.add_argument("--theta", type=float, default=0.5)
    parser.add_argument("--softening", type=float, default=0.0)
    parser.add_argument("--parity-rel-tol", type=float, default=1.0e-12)
    parser.add_argument("--parity-abs-tol", type=float, default=1.0e-12)
    parser.add_argument(
        "--traversal-policy",
        choices=("rtdl-containment", "author-opening", "author-optix-payload"),
        default="rtdl-containment",
    )
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--skip-reference", action="store_true")
    args = parser.parse_args()

    if args.mode == "status":
        payload = status_payload()
        write_payload(payload, args.output)
        return 0
    if args.mode == "rtdl-3d-diagnostic":
        payload = run_rtdl_diagnostic(args)
        if not args.output:
            write_payload(payload, None)
        return 0
    if args.mode == "aggregate-numba-parity":
        payload = run_aggregate_numba_parity(args)
        write_payload(payload, args.output)
        return 0
    if args.mode == "aggregate-numba-force-output":
        payload = run_aggregate_numba_force_output(args)
        write_payload(payload, args.output)
        return 0
    if args.mode == "aggregate-numba-force-compare":
        payload = run_aggregate_numba_force_compare(args)
        write_payload(payload, args.output)
        return 0 if payload["force_comparison"]["matched"] else 1
    raise AssertionError(args.mode)


if __name__ == "__main__":
    raise SystemExit(main())
