from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.prepared_execution import PreparedExecutionPhaseTiming
from rtdsl.prepared_execution import PreparedExecutionReport
from rtdsl.prepared_execution import PreparedExecutionSessionTask
from rtdsl.prepared_execution import run_repeated_prepared_execution_session
from rtdsl.prepared_session_residency import ExplicitPreparedSessionCache
from rtdsl.prepared_session_residency import make_prepared_session_cache_key


SCHEMA = "rtdl.phoenix_v3.runner_overhead_microbench.v1"


class _NoopPrepared:
    def __init__(self) -> None:
        self.calls = 0

    def run(self) -> dict[str, int]:
        self.calls += 1
        return {"calls": self.calls}

    def run_heavy(self) -> dict[str, object]:
        self.calls += 1
        return _heavy_output(self.calls)

    def run_light(self) -> dict[str, int]:
        self.calls += 1
        return {"calls": self.calls}

    def finalize_heavy(self, output: dict[str, int]) -> dict[str, object]:
        return _heavy_output(int(output["calls"]))


def _heavy_output(calls: int) -> dict[str, object]:
    return {
        "calls": int(calls),
        "metadata": {f"field_{index}": index for index in range(96)},
        "phase_seconds": {f"phase_{index}": index / 1_000_000.0 for index in range(32)},
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }


def _seconds(fn: Callable[[], Any], iterations: int) -> float:
    start = time.perf_counter()
    for _ in range(int(iterations)):
        fn()
    return time.perf_counter() - start


def build_report_template() -> PreparedExecutionReport:
    phases = (
        PreparedExecutionPhaseTiming(
            phase="prepare",
            seconds=0.1,
            role="prepare_explicit_session_on_cache_miss",
            setup_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="cache_load",
            seconds=0.0,
            role="load_explicit_prepared_session_from_cache_on_hit",
        ),
        PreparedExecutionPhaseTiming(
            phase="warmup",
            seconds=0.01,
            role="caller_requested_prepared_session_warmup",
            repeat_seconds=(0.01,),
            best_repeat_seconds=0.01,
        ),
        PreparedExecutionPhaseTiming(
            phase="steady_state_stream",
            seconds=0.0,
            role="no_separate_stream_phase_recorded_by_minimal_runner",
            steady_state_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="planner",
            seconds=0.0,
            role="caller_preplanned_single_prepared_operation",
            steady_state_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="executor",
            seconds=0.01,
            role="median_of_repeated_explicit_prepared_operations",
            repeat_seconds=(0.01, 0.011, 0.012, 0.011, 0.01),
            best_repeat_seconds=0.01,
            steady_state_candidate=True,
        ),
        PreparedExecutionPhaseTiming(
            phase="validation",
            seconds=0.0,
            role="caller_supplied_validation_after_execution",
            validation_candidate=True,
        ),
    )
    return PreparedExecutionReport(
        workflow_name="phoenix_runner_overhead_microbench",
        explicit_backend="optix",
        explicit_partner="none",
        phases=phases,
        warmup_count=1,
        claim_boundary={},
        notes=("local microbench only; not release evidence",),
    )


def run_microbench(*, iterations: int, runner_iterations: int) -> dict[str, Any]:
    iterations = int(iterations)
    runner_iterations = int(runner_iterations)
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    if runner_iterations <= 0:
        raise ValueError("runner_iterations must be positive")

    input_fingerprints = {
        f"input_{index}": {
            "kind": "synthetic",
            "count": 1000 + index,
            "digest": "x" * 64,
        }
        for index in range(4)
    }
    parameters = {f"param_{index}": index for index in range(8)}
    key = make_prepared_session_cache_key(
        primitive="fixed_radius_threshold_reached_count_2d",
        backend="optix",
        partner="none",
        device="cuda:0",
        input_fingerprints=input_fingerprints,
        parameters=parameters,
    )
    phase = PreparedExecutionPhaseTiming(
        phase="executor",
        seconds=0.01,
        role="median_of_repeated_explicit_prepared_operations",
        source_keys=("synthetic.executor",),
        repeat_seconds=(0.01, 0.011, 0.01, 0.012, 0.01),
        best_repeat_seconds=0.01,
        steady_state_candidate=True,
    )
    report = build_report_template()

    stable_id_sec = _seconds(lambda: key.stable_id, iterations)
    phase_to_dict_sec = _seconds(phase.to_dict, iterations)
    report_to_dict_sec = _seconds(report.to_dict, iterations)

    cache = ExplicitPreparedSessionCache(max_entries=1)

    def prepare_session() -> _NoopPrepared:
        return _NoopPrepared()

    task = PreparedExecutionSessionTask(
        workflow_name="phoenix_runner_overhead_microbench_noop",
        primitive="fixed_radius_threshold_reached_count_2d",
        backend="optix",
        partner="none",
        input_fingerprints=input_fingerprints,
        parameters=parameters,
        device="cuda:0",
        cache=cache,
        prepare_session=prepare_session,
        warmup_count=0,
        run_prepared=lambda prepared: prepared.run(),
        validate_output=lambda output: {"matches_oracle": int(output["calls"]) >= 1},
        notes=("local microbench only; not release evidence",),
    )

    def run_noop_runner() -> None:
        run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=1,
            validate_each_repeat=False,
            retain_repeat_outputs=False,
        )

    noop_runner_sec = _seconds(run_noop_runner, runner_iterations)
    last_result = run_repeated_prepared_execution_session(task, measured_repeat_count=3)
    last_metadata = last_result.to_metadata()

    heavy_cache = ExplicitPreparedSessionCache(max_entries=1)
    heavy_task = PreparedExecutionSessionTask(
        workflow_name="phoenix_runner_overhead_microbench_heavy_full",
        primitive="segment_intersection_topology_stream",
        backend="optix",
        partner="none",
        input_fingerprints=input_fingerprints,
        parameters=parameters,
        device="cuda:0",
        cache=heavy_cache,
        prepare_session=prepare_session,
        warmup_count=0,
        run_prepared=lambda prepared: prepared.run_heavy(),
        validate_output=lambda output: {"matches_oracle": int(output["calls"]) >= 1},
        notes=("local microbench only; not release evidence",),
    )
    finalized_cache = ExplicitPreparedSessionCache(max_entries=1)
    finalized_task = PreparedExecutionSessionTask(
        workflow_name="phoenix_runner_overhead_microbench_heavy_finalize_once",
        primitive="segment_intersection_topology_stream",
        backend="optix",
        partner="none",
        input_fingerprints=input_fingerprints,
        parameters=parameters,
        device="cuda:0",
        cache=finalized_cache,
        prepare_session=prepare_session,
        warmup_count=0,
        run_prepared=lambda prepared: prepared.run_heavy(),
        measured_run_prepared=lambda prepared: prepared.run_light(),
        finalize_output=lambda prepared, output: prepared.finalize_heavy(output),
        validate_output=lambda output: {"matches_oracle": int(output["calls"]) >= 1},
        notes=("local microbench only; not release evidence",),
    )

    def run_heavy_full_runner() -> None:
        run_repeated_prepared_execution_session(
            heavy_task,
            measured_repeat_count=5,
            validate_each_repeat=False,
            retain_repeat_outputs=False,
        )

    def run_heavy_finalize_once_runner() -> None:
        run_repeated_prepared_execution_session(
            finalized_task,
            measured_repeat_count=5,
            validate_each_repeat=False,
            retain_repeat_outputs=False,
        )

    heavy_full_runner_sec = _seconds(run_heavy_full_runner, runner_iterations)
    heavy_finalize_once_runner_sec = _seconds(run_heavy_finalize_once_runner, runner_iterations)
    finalized_result = run_repeated_prepared_execution_session(
        finalized_task,
        measured_repeat_count=5,
    )
    finalized_metadata = finalized_result.to_metadata()

    return {
        "schema": SCHEMA,
        "status": "local_microbench_not_release_evidence",
        "iterations": iterations,
        "runner_iterations": runner_iterations,
        "timing_sec": {
            "stable_id_reads": stable_id_sec,
            "phase_to_dict": phase_to_dict_sec,
            "report_to_dict": report_to_dict_sec,
            "noop_runner_calls": noop_runner_sec,
            "heavy_full_runner_calls": heavy_full_runner_sec,
            "heavy_finalize_once_runner_calls": heavy_finalize_once_runner_sec,
        },
        "timing_per_call_sec": {
            "stable_id_read": stable_id_sec / iterations,
            "phase_to_dict": phase_to_dict_sec / iterations,
            "report_to_dict": report_to_dict_sec / iterations,
            "noop_runner_call": noop_runner_sec / runner_iterations,
            "heavy_full_runner_call": heavy_full_runner_sec / runner_iterations,
            "heavy_finalize_once_runner_call": heavy_finalize_once_runner_sec / runner_iterations,
        },
        "comparison": {
            "heavy_finalize_once_speedup_vs_full": (
                heavy_full_runner_sec / heavy_finalize_once_runner_sec
                if heavy_finalize_once_runner_sec > 0.0
                else None
            ),
            "heavy_finalize_once_saved_fraction": (
                1.0 - (heavy_finalize_once_runner_sec / heavy_full_runner_sec)
                if heavy_full_runner_sec > 0.0
                else None
            ),
        },
        "last_runner_metadata": {
            "schema": last_metadata.get("schema"),
            "runtime_executed": last_metadata.get("runtime_executed"),
            "productized_execution_path": "prepared_execution_session_runner",
            "prepared_execution_report_validation": last_metadata.get(
                "prepared_execution_report_validation"
            ),
            "release_authorized": last_metadata.get("release_authorized"),
            "public_speedup_claim_authorized": last_metadata.get(
                "public_speedup_claim_authorized"
            ),
            "broad_v3_faster_than_v2_claim_authorized": last_metadata.get(
                "broad_v3_faster_than_v2_claim_authorized"
            ),
            "true_zero_copy_claim_authorized": last_metadata.get(
                "true_zero_copy_claim_authorized"
            ),
            "app_specific_native_engine_logic_allowed": last_metadata.get(
                "app_specific_native_engine_logic_allowed"
            ),
        },
        "finalized_runner_metadata": {
            "schema": finalized_metadata.get("schema"),
            "runtime_executed": finalized_metadata.get("runtime_executed"),
            "measured_run_prepared_override_used": finalized_metadata.get(
                "measured_run_prepared_override_used"
            ),
            "measured_output_finalized_once": finalized_metadata.get(
                "measured_output_finalized_once"
            ),
            "per_repeat_output_finalization_avoided": finalized_metadata.get(
                "per_repeat_output_finalization_avoided"
            ),
            "output_finalize_sec": finalized_metadata.get("output_finalize_sec"),
            "release_authorized": finalized_metadata.get("release_authorized"),
            "public_speedup_claim_authorized": finalized_metadata.get(
                "public_speedup_claim_authorized"
            ),
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_or_external_zero_copy_authorized": False,
        "full_all_app_rerun_authorized_by_this_packet": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phoenix V3 runner overhead microbench.")
    parser.add_argument("--iterations", type=int, default=20_000)
    parser.add_argument("--runner-iterations", type=int, default=2_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    payload = run_microbench(
        iterations=args.iterations,
        runner_iterations=args.runner_iterations,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
