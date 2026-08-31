#!/usr/bin/env python3
"""Run the frozen Goal5791 workspace or portable-clean CPU test gate.

This helper is deliberately stdlib-only.  It discovers the same eleven
``unittest`` modules for both gates, flattens them to unique concrete test IDs,
and applies the exact six-test external/history exclusion only for the clean
gate.  The helper observes no scientific clock and reports no elapsed or
performance value.  Its caller's operational timeout watchdog may use a host
clock, but that observation is neither persisted nor registered.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import unittest


SCHEMA = "rtdl.goal5791.cpu_test_gate_result.v2"
WORKSPACE_CPU_TEST_MODULES = (
    "tests.goal5791_data_oracle_authority_test",
    "tests.goal5791_formal_contract_test",
    "tests.goal5791_formal_evaluator_recount_test",
    "tests.goal5791_formal_worker_controller_test",
    "tests.goal5791_portable_home_harness_test",
    "tests.goal5791_pre_pod_base_budget_audit_test",
    "tests.goal5791_pre_worker_zero_claim_freeze_test",
    "tests.goal5791_pretimer_execution_token_amendment_test",
    "tests.goal5791_segment_descriptors_test",
    "tests.goal5791_successor_source_authority_test",
    "tests.goal5791_verified_fusion_execution_token_test",
)
CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS = (
    "tests.goal5791_data_oracle_authority_test."
    "Goal5791DataOracleAuthorityTest."
    "test_bundle_manifest_datasets_oracles_and_non_authorization",
    "tests.goal5791_pre_pod_base_budget_audit_test."
    "Goal5791PrePodBaseBudgetAuditTest."
    "test_budget_rebuilds_from_frozen_goal5784_and_goal5785_raw",
    "tests.goal5791_pre_pod_base_budget_audit_test."
    "Goal5791PrePodBaseBudgetAuditTest."
    "test_selected_a1_v4_base_rehashes_and_manifest_recounts",
    "tests.goal5791_pre_pod_base_budget_audit_test."
    "Goal5791PrePodBaseBudgetAuditTest."
    "test_v8_nested_elf_rejection_reproduces",
    "tests.goal5791_pre_worker_zero_claim_freeze_test."
    "Goal5791PreWorkerZeroClaimFreezeTest."
    "test_a1_raw_rejects_prove_five_facade_plus_one_tps",
    "tests.goal5791_pretimer_execution_token_amendment_test."
    "Goal5791PretimerExecutionTokenAmendmentTest."
    "test_selected_base_and_append_only_product_lineage_are_exact",
)
EXPECTED_WORKSPACE_CPU_TEST_COUNT = 115
EXPECTED_CLEAN_CPU_TEST_COUNT = 109
WORKSPACE_CPU_TEST_MODULES_SHA256 = (
    "b22d66d23ed29e80c8184880f09e257246ea21288eb3eca0567adf16506fe766"
)
EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256 = (
    "84b6fd3a5e2f2437784972d15bb5f5f19ddc7999615bd1151eed8e1634fbb171"
)
CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256 = (
    "a7319f38d0eb5ec0ca21db7588a950eb07bc0c86b4c619d68db95d39b3e30245"
)
EXPECTED_CLEAN_CPU_TEST_IDS_SHA256 = (
    "d472d8023717e1e025c5c4dbd66d39158bda156b2cec89084854bb15b28a36f9"
)
ENVIRONMENT_CONTRACT = {
    "pythonpath_role": "source_root_src_then_source_root",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONNOUSERSITE": "1",
    "CUDA_VISIBLE_DEVICES": "-1",
    "NUMBA_DISABLE_CUDA": "1",
    "ambient_environment_outside_overrides_is_not_claimed": True,
}


class Goal5791CPUTestGateError(RuntimeError):
    """Raised when discovery, scope, environment, or result drifts."""


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest_ids(values: tuple[str, ...] | list[str]) -> str:
    return hashlib.sha256(_canonical(list(values))).hexdigest()


def _stable_exception_summary(
    *, root: Path, test_id: str, outcome: str,
    error: tuple[type[BaseException], BaseException, object],
) -> dict[str, str]:
    exception_type = (
        f"{error[0].__module__}.{error[0].__qualname__}")
    message = str(error[1]).replace("\r\n", "\n").replace("\r", "\n")
    message = message.replace("\\", "/")
    source_root = str(root.resolve(strict=True)).replace("\\", "/")
    message = re.sub(
        re.escape(source_root), "<SOURCE_ROOT>", message,
        flags=re.IGNORECASE if os.name == "nt" else 0,
    )
    message = " | ".join(
        line.strip() for line in message.split("\n") if line.strip())
    if len(message) > 2_048:
        digest = hashlib.sha256(message.encode("utf-8")).hexdigest()
        message = message[:1_960] + f"...<MESSAGE_SHA256={digest}>"
    lowered = message.casefold()
    if re.search(
        r"(?:[a-z]:/|/(?:tmp|private/tmp|var/tmp)/|"
        r"/users/[^/]+/appdata/local/temp/)", message,
        flags=re.IGNORECASE,
    ) or any(part in lowered for part in ("/.codex/", "/.git/")):
        raise Goal5791CPUTestGateError(
            "Goal5791 stable exception summary retained a private/temp path")
    return {
        "test_id": test_id,
        "outcome": outcome,
        "exception_type": exception_type,
        "summary": message,
    }


class _StableTestResult(unittest.TestResult):
    def __init__(self, *, root: Path) -> None:
        super().__init__()
        self._source_root = root
        self.failure_exception_summaries: list[dict[str, str]] = []
        self.error_exception_summaries: list[dict[str, str]] = []

    def addFailure(self, test: unittest.TestCase, err: object) -> None:
        super().addFailure(test, err)
        self.failure_exception_summaries.append(_stable_exception_summary(
            root=self._source_root, test_id=test.id(), outcome="failure",
            error=err,
        ))

    def addError(self, test: unittest.TestCase, err: object) -> None:
        super().addError(test, err)
        self.error_exception_summaries.append(_stable_exception_summary(
            root=self._source_root, test_id=test.id(), outcome="error",
            error=err,
        ))


def _flatten(suite: unittest.TestSuite) -> tuple[unittest.TestCase, ...]:
    flattened: list[unittest.TestCase] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            flattened.extend(_flatten(item))
        elif isinstance(item, unittest.TestCase):
            flattened.append(item)
        else:
            raise Goal5791CPUTestGateError(
                f"unexpected unittest node type: {type(item).__name__}")
    ids = [item.id() for item in flattened]
    if not all(isinstance(item, str) and item for item in ids) \
            or len(set(ids)) != len(ids):
        raise Goal5791CPUTestGateError(
            "Goal5791 discovered test IDs are empty or non-unique")
    return tuple(flattened)


def _validate_environment(root: Path) -> None:
    expected_pythonpath = os.pathsep.join((str(root / "src"), str(root)))
    expected = {
        "PYTHONPATH": expected_pythonpath,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "CUDA_VISIBLE_DEVICES": "-1",
        "NUMBA_DISABLE_CUDA": "1",
    }
    observed = {key: os.environ.get(key) for key in expected}
    if observed != expected:
        raise Goal5791CPUTestGateError(
            "Goal5791 CPU gate environment overrides drifted")


def _validate_frozen_identity(
    discovered_ids: tuple[str, ...], clean_ids: tuple[str, ...],
) -> None:
    if len(WORKSPACE_CPU_TEST_MODULES) != 11 \
            or _digest_ids(WORKSPACE_CPU_TEST_MODULES) \
                != WORKSPACE_CPU_TEST_MODULES_SHA256 \
            or len(discovered_ids) != EXPECTED_WORKSPACE_CPU_TEST_COUNT \
            or _digest_ids(discovered_ids) \
                != EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256 \
            or len(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS) != 6 \
            or len(set(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS)) != 6 \
            or _digest_ids(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS) \
                != CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256 \
            or not set(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS).issubset(
                discovered_ids) \
            or len(clean_ids) != EXPECTED_CLEAN_CPU_TEST_COUNT \
            or _digest_ids(clean_ids) != EXPECTED_CLEAN_CPU_TEST_IDS_SHA256:
        raise Goal5791CPUTestGateError(
            "Goal5791 frozen CPU test identity/count drifted")


def run_gate(*, root: Path, scope: str) -> dict[str, object]:
    root = root.resolve(strict=True)
    if scope not in {"workspace", "clean"}:
        raise Goal5791CPUTestGateError("Goal5791 CPU gate scope drifted")
    _validate_environment(root)
    discovered = _flatten(
        unittest.defaultTestLoader.loadTestsFromNames(
            WORKSPACE_CPU_TEST_MODULES))
    discovered_ids = tuple(item.id() for item in discovered)
    excluded_set = set(CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS)
    clean = tuple(
        item for item in discovered if item.id() not in excluded_set)
    clean_ids = tuple(item.id() for item in clean)
    _validate_frozen_identity(discovered_ids, clean_ids)
    selected = discovered if scope == "workspace" else clean
    selected_ids = discovered_ids if scope == "workspace" else clean_ids

    result = _StableTestResult(root=root)
    unittest.TestSuite(selected).run(result)
    outcome_test_ids = {
        "failures": sorted(case.id() for case, _ in result.failures),
        "errors": sorted(case.id() for case, _ in result.errors),
        "skipped": sorted(case.id() for case, _ in result.skipped),
        "expectedFailures": sorted(
            case.id() for case, _ in result.expectedFailures),
        "unexpectedSuccesses": sorted(
            case.id() for case in result.unexpectedSuccesses),
    }
    failure_summaries = sorted(
        result.failure_exception_summaries,
        key=lambda item: (item["test_id"], item["summary"]),
    )
    error_summaries = sorted(
        result.error_exception_summaries,
        key=lambda item: (item["test_id"], item["summary"]),
    )
    test_result = {
        "testsRun": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "expectedFailures": len(result.expectedFailures),
        "unexpectedSuccesses": len(result.unexpectedSuccesses),
    }
    success = result.wasSuccessful() and test_result == {
        "testsRun": len(selected_ids),
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "expectedFailures": 0,
        "unexpectedSuccesses": 0,
    } and not any(outcome_test_ids.values()) \
        and not failure_summaries and not error_summaries
    return {
        "schema": SCHEMA,
        "scope": scope,
        "python_role": "current_interpreter",
        "entrypoint": "scripts/goal5791_cpu_test_gate.py",
        "workspace_test_modules": list(WORKSPACE_CPU_TEST_MODULES),
        "workspace_test_module_count": len(WORKSPACE_CPU_TEST_MODULES),
        "workspace_test_modules_sha256": WORKSPACE_CPU_TEST_MODULES_SHA256,
        "discovered_workspace_test_ids": list(discovered_ids),
        "discovered_workspace_test_count": len(discovered_ids),
        "discovered_workspace_test_ids_sha256": (
            EXPECTED_WORKSPACE_CPU_TEST_IDS_SHA256),
        "excluded_external_only_test_ids": list(
            CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS),
        "excluded_external_only_test_count": len(
            CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS),
        "excluded_external_only_test_ids_sha256": (
            CLEAN_EXTERNAL_ONLY_EXCLUDED_TEST_IDS_SHA256),
        "selected_test_ids": list(selected_ids),
        "selected_test_count": len(selected_ids),
        "selected_test_ids_sha256": _digest_ids(selected_ids),
        "environment_contract": ENVIRONMENT_CONTRACT,
        "test_result": test_result,
        "outcome_test_ids": outcome_test_ids,
        "outcome_test_ids_sha256": hashlib.sha256(
            _canonical(outcome_test_ids)).hexdigest(),
        "failure_test_ids": outcome_test_ids["failures"],
        "error_test_ids": outcome_test_ids["errors"],
        "failure_exception_summaries": failure_summaries,
        "error_exception_summaries": error_summaries,
        "success": success,
        "reported_elapsed_value_count": 0,
        "test_or_scientific_clock_sample_count": 0,
        "registered_performance_timing_count": 0,
        "operational_timeout_watchdog_uses_host_clock": True,
        "operational_watchdog_clock_not_persisted_or_registered": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--scope", choices=("workspace", "clean"), required=True)
    args = parser.parse_args()
    value = run_gate(root=args.root, scope=args.scope)
    sys.stdout.buffer.write(_canonical(value) + b"\n")
    if value["success"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
