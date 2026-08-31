from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5807_provider_ready_formal_controller as controller
from scripts import goal5807_provider_ready_formal_evaluate as evaluator
from scripts import goal5807_provider_ready_formal_protocol as protocol
from scripts import goal5807_provider_ready_formal_recount as recount
from scripts import goal5807_provider_ready_formal_worker as worker


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "scripts" / "goal5807_provider_ready_pilot.py"
TARGET = (
    ROOT / "history" / "internal_docs"
    / "goal5806_same_source_postimport_target_20260826.json")
SUPERSEDED_CONTRACT = (
    ROOT / "history" / "internal_docs"
    / "goal5807_provider_ready_confirmatory_formal_contract_20260827.json")
CONTRACT_V2 = (
    ROOT / "history" / "internal_docs"
    / "goal5807_provider_ready_confirmatory_formal_contract_v2_20260827.json")


def _phase_ledger(prepare_ns: int, execute_ns: int) -> dict[str, object]:
    durations = {name: 1 for name in protocol.PHASES}
    durations["app_prepare"] = prepare_ns
    durations["first_exact_execute"] = execute_ns
    phases: dict[str, object] = {}
    start = 0
    for name in protocol.PHASES:
        phases[name] = {
            "status": "OBSERVED",
            "start_offset_ns": start,
            "duration_ns": durations[name],
        }
        start += durations[name]
    observed = sum(durations.values())
    between = 1_000
    total = observed + between
    return {
        "clock": "time.perf_counter_ns",
        "phases_are_sequential_and_nonoverlapping": True,
        "nonobserved_phase_zero_imputed": False,
        "phases": phases,
        "observed_phase_sum_ns_additive": observed,
        "between_phase_unclassified_ns_additive": between,
        "total_profiled_full_process_ns": total,
        "additive_closure_ns": total,
        "total_boundary": "synthetic",
    }


def _pilot_receipt(
    arm: str, task: str, prepare_ns: int, execute_ns: int,
) -> dict[str, object]:
    ledger = _phase_ledger(prepare_ns, execute_ns)
    primary = prepare_ns + execute_ns
    body: dict[str, object] = {
        "schema": protocol.PILOT_SCHEMA,
        "status": "synthetic-exact",
        "arm": arm,
        "task": task,
        "steady_repetitions": 1,
        "target_manifest": {
            "path": str(TARGET), "bytes": TARGET.stat().st_size,
            "sha256": protocol.file_sha256(TARGET),
        },
        "pilot_source": {
            "path": str(PILOT), "bytes": PILOT.stat().st_size,
            "sha256": protocol.file_sha256(PILOT),
        },
        "provider_program_ready_assertions": {
            "runtime_provider_loaded": True,
            "cuda_primary_ready": True,
            "exact_program_bytes_loaded": True,
            "optix_device_context_absent": True,
            "pipeline_absent": True,
            "cuda_current_context_is_device0_primary_at_app_timer_entry": True,
            "cuda_current_context_matches_retained_primary_handle": True,
            "device_ordinal_is_zero": True,
            "target_compute_capability_is_8_6": True,
            "temporary_primary_retain_balanced": True,
        },
        "provider_program_ready_assertion_source": {},
        "ready_program_identity": {},
        "comparison_contract": {
            "comparison_authorized": True,
            "app_boundary_ratio_computation_authorized": True,
            "timer_entry_state_mechanically_matched": True,
            "app_timer_entry_cuda_context": "DEVICE0_PRIMARY_CURRENT",
            "pilot_is_formal_or_paper_evidence": False,
            "provider_bind_phase_comparison_authorized": False,
            "full_profiled_process_comparison_authorized": False,
        },
        "phase_ledger": ledger,
        "comparable_app_boundary": {
            "definition": "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE",
            "duration_ns_additive": primary,
        },
        "contiguous_prefix_boundaries": {
            protocol.PREFIX_REGIMES[0]: {
                "duration_ns": primary + 200,
                "start_event": "HARNESS_RUN_ENTRY",
                "stop_event": "FIRST_EXACT_OUTPUT_VALIDATED",
                "single_contiguous_timer": True,
            },
            protocol.PREFIX_REGIMES[1]: {
                "duration_ns": primary + 100,
                "start_event": "POST_RUNTIME_PRELOAD",
                "stop_event": "FIRST_EXACT_OUTPUT_VALIDATED",
                "single_contiguous_timer": True,
            },
        },
        "identities": {
            "construction": {}, "runtime": {}, "inputs": {},
        },
        "validation": {
            "oracle_validated_execution_count": 2,
            "first_evidence_sha256": "e" * 64,
            "relation_cubin_loader_fd_closed_after_adapter_close": (
                True if arm == protocol.ARMS[1] and task == "relation"
                else None),
            "pyoptix_prepared_close_semantics": (
                "PARTIAL_OWNER_CLOSE__PROCESS_TEARDOWN_RETAINS_CONTEXT_"
                "PIPELINE_SBT" if arm == protocol.ARMS[1] else
                "COMPLETE_PROVIDER_OWNER_CLOSE"),
        },
        "measurement_contract": {
            "diagnostic_pilot_only": True,
            "exact_program_bytes_loaded_before_comparable_boundary": True,
            "current_cuda_context_restored_before_comparable_boundary": True,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "may_replace_goal5806": False,
            "paper_claim_authorized": False,
            "inferential_claim_authorized": False,
            "threshold_claim_authorized": False,
            "formal_design_input_only": True,
            "pyoptix_prepared_close_semantics": (
                "PARTIAL_OWNER_CLOSE__PROCESS_TEARDOWN_RETAINS_CONTEXT_"
                "PIPELINE_SBT" if arm == protocol.ARMS[1] else
                "COMPLETE_PROVIDER_OWNER_CLOSE"),
        },
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    return {**body, "pilot_sha256": protocol.value_sha256(body)}


def _formal_rows(*, rtdl_ns: int, pyoptix_ns: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    contract_sha = "c" * 64
    for ordinal, coordinate in enumerate(protocol.expected_worker_coordinates()):
        task, block, position, arm = coordinate
        identity = protocol.worker_id(task, block, position, arm)
        primary = rtdl_ns if arm == protocol.ARMS[0] else pyoptix_ns
        pilot = _pilot_receipt(arm, task, primary - 10, 10)
        worker_body: dict[str, object] = {
            "schema": worker.WORKER_SCHEMA,
            "status": "PASS__EXACT_ORACLE_AND_PHASE_LEDGER",
            "worker_id": identity,
            "pid": 10_000 + ordinal,
            "task": task,
            "arm": arm,
            "contract_sha256": contract_sha,
            "primary_app_prepare_plus_first_exact_execute_ns": primary,
            "registered_timing_ns": {
                "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE": primary,
                protocol.PREFIX_REGIMES[0]: primary + 200,
                protocol.PREFIX_REGIMES[1]: primary + 100,
            },
            "registered_performance_timing_count": (
                protocol.REGISTERED_TIMINGS_PER_WORKER),
            "pilot_receipt": pilot,
            "pilot_receipt_sha256": protocol.value_sha256(pilot),
            "full_process_total_ns_nonprimary": pilot[
                "phase_ledger"]["total_profiled_full_process_ns"],
            "all_phases_preserved_nonprimary": True,
            "formal_worker_count": 1,
        }
        result = {
            **worker_body,
            "worker_receipt_sha256": protocol.value_sha256(worker_body),
        }
        rows.append({
            "schema": controller.ROW_SCHEMA,
            "status": "PASS",
            "contract_sha256": contract_sha,
            "worker_id": identity,
            "task": task,
            "block": block,
            "position": position,
            "arm": arm,
            "pid": 10_000 + ordinal,
            "returncode": 0,
            "registered_performance_timing_count": (
                protocol.REGISTERED_TIMINGS_PER_WORKER),
            "worker_result": result,
        })
    return rows


def _evaluation_contract() -> dict[str, object]:
    threshold = {
        "median_block_ratio_rtdl_over_pyoptix_max": 1.05,
        "bootstrap_ci_upper_max": 1.10,
        "positive_rtdl_minus_pyoptix_arm_median_gap_ns_max": 25_000_000,
        "rtdl_faster_passes_absolute_gap_gate": True,
        "each_task_must_pass_all_three": True,
    }
    return {
        "hypotheses": {
            "thresholded_regimes": list(protocol.THRESHOLDED_REGIMES),
            "app_boundary": threshold,
            "harness_run_entry_prefix": threshold,
            "post_runtime_preload_prefix_has_threshold": False,
            "all_structurally_valid_results_accepted": True,
        },
        "claim_boundary": {"old_goal5806_rows_replaced": False},
        "predecessor_results": {"preserved": True},
    }


def _controller_receipt() -> dict[str, object]:
    return {
        "schema": controller.CONTROLLER_SCHEMA,
        "status": "COMPLETE__NO_RETRY_RESUME_REPLACEMENT_OR_DROP",
        "contract_sha256": "c" * 64,
        "worker_count": protocol.TOTAL_WORKERS,
        "unique_worker_pid_count": protocol.TOTAL_WORKERS,
        "registered_performance_timing_count": (
            protocol.TOTAL_REGISTERED_TIMINGS),
        "retry_count": 0,
        "resume_count": 0,
        "replacement_count": 0,
        "row_drop_count": 0,
    }


class Goal5807ProviderReadyFormalTest(unittest.TestCase):
    def test_v2_frozen_contract_rehashes_at_worker_zero(self) -> None:
        if not CONTRACT_V2.is_file():
            self.skipTest(
                "v2 freeze awaits the required unregistered four-cell pilot")
        frozen = protocol.read_object(CONTRACT_V2)
        resolved = protocol.validate_contract(frozen, ROOT, rehash=True)
        self.assertEqual(set(resolved), protocol.FILE_KEYS)
        self.assertEqual(frozen["formal_worker_count"], 0)
        self.assertEqual(frozen[
            "registered_performance_timing_count"], 0)
        self.assertEqual(frozen["claim_boundary"][
            "registered_boundary"], (
                "DEVICE0_PRIMARY_CURRENT_PROVIDER_PRIMARY_AND_"
                "PROGRAM_READY__APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE"))
        self.assertTrue(frozen["claim_boundary"][
            "pilot_is_unregistered_diagnostic"])
        self.assertFalse(frozen["claim_boundary"][
            "pilot_is_formal_or_paper_evidence"])

    def test_old_zero_worker_contract_is_preserved_as_superseded(self) -> None:
        self.assertEqual(protocol.file_sha256(SUPERSEDED_CONTRACT), (
            "f992669efca937d7c3aed61dc66efa45e610927cffde47cfb3e9a3cba8153ebb"))

    def test_exact_abba_schedule_has_128_fresh_process_observations(self) -> None:
        coordinates = protocol.expected_worker_coordinates()
        self.assertEqual(len(coordinates), 128)
        for task in protocol.TASKS:
            for block in range(protocol.BLOCK_COUNT):
                observed = tuple(
                    arm for row_task, row_block, _position, arm in coordinates
                    if row_task == task and row_block == block)
                self.assertEqual(observed, (
                    protocol.ARMS[0], protocol.ARMS[1],
                    protocol.ARMS[1], protocol.ARMS[0]))

    def test_worker_accepts_exact_pilot_and_rejects_primary_drift(self) -> None:
        receipt = _pilot_receipt(
            protocol.ARMS[1], "relation", 700, 300)
        timings = worker._validate_pilot_receipt(
            receipt, arm=protocol.ARMS[1], task="relation",
            pilot_path=PILOT, target_path=TARGET)
        self.assertEqual(timings[
            "APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE"], 1_000)
        receipt["comparable_app_boundary"]["duration_ns_additive"] = 999
        body = dict(receipt)
        body.pop("pilot_sha256")
        receipt["pilot_sha256"] = protocol.value_sha256(body)
        with self.assertRaisesRegex(RuntimeError, "primary boundary differs"):
            worker._validate_pilot_receipt(
                receipt, arm=protocol.ARMS[1], task="relation",
                pilot_path=PILOT, target_path=TARGET)

    def test_phase_ledger_survives_canonical_json_key_sorting(self) -> None:
        ledger = _phase_ledger(700, 300)
        round_tripped = json.loads(protocol.canonical(ledger))
        self.assertNotEqual(tuple(round_tripped["phases"]), protocol.PHASES)
        self.assertEqual(protocol.validate_phase_ledger(
            round_tripped), ledger["total_profiled_full_process_ns"])

    def test_valid_negative_result_is_accepted_unconditionally(self) -> None:
        rows = json.loads(protocol.canonical(
            _formal_rows(rtdl_ns=200_000_000, pyoptix_ns=100_000_000)))
        result = evaluator.evaluate_rows(
            _evaluation_contract(), rows, contract_sha256="c" * 64,
            controller_sha256="d" * 64)
        self.assertFalse(result[
            "all_thresholded_regimes_and_tasks_hypothesis_pass"])
        self.assertEqual(result["status"], (
            "VALID_RESULT__HYPOTHESES_FAIL__ACCEPTED_UNCONDITIONALLY"))
        self.assertTrue(result["valid_result_accepted_unconditionally"])
        self.assertEqual(result["worker_count"], 128)
        self.assertEqual(
            len(result["nonprimary_full_process_evidence_by_worker"]), 128)

    def test_valid_positive_result_passes_all_three_gates(self) -> None:
        rows = json.loads(protocol.canonical(
            _formal_rows(rtdl_ns=101_000_000, pyoptix_ns=100_000_000)))
        result = evaluator.evaluate_rows(
            _evaluation_contract(), rows, contract_sha256="c" * 64,
            controller_sha256="d" * 64)
        self.assertTrue(result[
            "all_thresholded_regimes_and_tasks_hypothesis_pass"])
        for task in protocol.TASKS:
            for regime in protocol.THRESHOLDED_REGIMES:
                self.assertTrue(all(result[
                    "thresholded_results"][regime][task]["gates"].values()))

    def test_controller_worker_failure_is_terminal_and_not_reusable(self) -> None:
        calls: list[str] = []

        def fail_launcher(**kwargs: object) -> dict[str, object]:
            calls.append(str(kwargs["arm"]))
            return {
                "command": ["synthetic"], "pid": 1234, "returncode": 9,
                "stdout": json.dumps({
                    "registered_performance_timing_count": 1,
                }).encode("utf-8"),
                "stderr": b"synthetic failure",
                "cache_files_after": [],
            }

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            contract = root / "contract.json"
            contract.write_text("{}\n", encoding="utf-8")
            output = root / "formal"
            with self.assertRaisesRegex(RuntimeError, "formal worker failed"):
                controller.execute_schedule(
                    root=root, contract_path=contract, output=output,
                    launcher=fail_launcher)
            self.assertEqual(len(calls), 1)
            failure = json.loads((output / "TERMINAL_FAILURE.json").read_text(
                encoding="utf-8"))
            self.assertEqual(failure[
                "failed_worker_registered_timing_count"], 1)
            self.assertFalse(failure["partial_result_reuse_authorized"])
            with self.assertRaisesRegex(RuntimeError, "already exists"):
                controller.execute_schedule(
                    root=root, contract_path=contract, output=output,
                    launcher=fail_launcher)
            self.assertEqual(len(calls), 1)

    def test_independent_recount_accepts_exact_negative_result(self) -> None:
        rows = json.loads(protocol.canonical(
            _formal_rows(rtdl_ns=200_000_000, pyoptix_ns=100_000_000)))
        evaluation = evaluator.evaluate_rows(
            _evaluation_contract(), rows, contract_sha256="c" * 64,
            controller_sha256="d" * 64)
        result = recount.recount(
            contract=_evaluation_contract(), contract_sha256="c" * 64,
            controller=_controller_receipt(), controller_sha256="d" * 64,
            rows=rows, evaluation=evaluation,
            evaluation_sha256="e" * 64)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["finding_count"], 0)
        self.assertTrue(result["threshold_failure_is_valid_scientific_result"])


if __name__ == "__main__":
    unittest.main()
