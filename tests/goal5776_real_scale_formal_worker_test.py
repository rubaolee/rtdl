from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys
import tempfile
import unittest

import numba
import numpy as np

from goal5776_real_scale_formal_contract import COLD, contract_sha256
from goal5776_real_scale_formal_worker import (
    _validate_receipt_row_binding,
    installed_partner_versions,
    run_worker,
)
from goal5776_real_scale_frontdoors import _bind_receipt_to_registered_rows


ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "scripts/goal5776_real_scale_formal_worker.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _receipt():
    return {
        "physical_executor_classification": "optix_traversal_observed",
        "native_snapshot": {
            "successful_launch_count": 1,
            "complete_context_launch_count": 1,
            "failed_launch_count": 0,
            "incomplete_context_launch_count": 0,
            "unbound_launch_count": 0,
            "pending_context_at_finish": 0,
            "session_error": 0,
            "first_traversable": "gas:first",
            "last_traversable": "gas:last",
        },
    }


def _bound_receipt(receipt=None):
    return _bind_receipt_to_registered_rows(receipt or _receipt(), [{
        "row_id": "particle__microfluidics_5000::complete",
        "input_sha256": "a" * 64,
        "output_sha256": "b" * 64,
    }])


class Goal5776RealScaleFormalWorkerTest(unittest.TestCase):
    def test_registered_row_binding_rejects_output_digest_drift(self):
        receipt = _bound_receipt()
        with self.assertRaisesRegex(RuntimeError, "row receipt binding mismatch"):
            _validate_receipt_row_binding(receipt, [{
                "row_id": "particle__microfluidics_5000::complete",
                "input_sha256": "a" * 64,
                "output_sha256": "c" * 64,
            }])

    def test_worker_binds_all_partner_runtime_versions(self):
        source = WORKER.read_text(encoding="utf-8")
        for required in (
            '"numba_version"', '"numpy_version"', '"cupy_version"',
            '"scipy_version"', 'installed_partner_versions()',
        ):
            self.assertIn(required, source)

    def runtime(self, root: Path) -> Path:
        native = root / "native.so"
        native.write_bytes(b"native")
        manifest = root / "MANIFEST.json"
        manifest.write_text("{}\n", encoding="utf-8")
        expected_value = root / "EXPECTED_VALUE_STATEMENT.md"
        expected_value.write_text("frozen negative prior\n", encoding="utf-8")
        python = Path(sys.executable).resolve()
        payload = {
            "schema": "rtdl.goal5776.real_scale_runtime.v1",
            "source_root": str(root),
            "bundle_sha256": "0" * 64,
            "data_archive_sha256": "9" * 64,
            "execution_source_sha256": "1" * 64,
            "source_tree_sha256": "2" * 64,
            "rtdbscan_evidence_sha256": "3" * 64,
            "native_library_path": str(native),
            "native_library_sha256": _sha(native),
            "target_identity_sha256": "4" * 64,
            "prepared_identity_sha256": "8" * 64,
            "plan_sha256": "5" * 64,
            "formal_identity_sha256": "6" * 64,
            "leaf_cache_root": str(root),
            "leaf_cache_manifest_path": str(manifest),
            "leaf_cache_manifest_sha256": _sha(manifest),
            "expected_value_statement_path": str(expected_value),
            "expected_value_statement_sha256": _sha(expected_value),
            "formal_contract_sha256": contract_sha256(),
            "python_executable": str(python),
            "python_executable_sha256": _sha(python),
            "python_version": platform.python_version(),
            "numba_version": numba.__version__,
            "numpy_version": np.__version__,
            "cupy_version": installed_partner_versions()["cupy"],
            "scipy_version": installed_partner_versions()["scipy"],
            "inputs": {},
        }
        path = root / "RUNTIME.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_v2_worker_emits_one_frozen_raw_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = self.runtime(root)

            def runner(**kwargs):
                self.assertEqual(kwargs["lifecycle"], COLD)
                self.assertEqual(kwargs["unit_id"], "particle__microfluidics_5000")
                return {
                    "matched": True,
                    "default_selected_between_application_algorithms": False,
                    "comparator_inside_registered_timer": False,
                    "close_inside_registered_timer": True,
                    "loading_seconds_reported_separately": None,
                    "preparation_seconds_reported_separately": None,
                    "traversal_receipt": _bound_receipt(),
                    "phase_accounting": {
                        "loading_seconds": 0.1,
                        "preparation_seconds": 0.1,
                        "close_seconds": 0.05,
                        "row_execute_seconds": {
                            "particle__microfluidics_5000::complete": 1.0
                        },
                        "same_worker_mutually_exclusive_phases": True,
                        "nested_phase_medians_summed": False,
                    },
                    "rows": [{
                        "row_id": "particle__microfluidics_5000::complete",
                        "input_sha256": "a" * 64,
                        "output_sha256": "b" * 64,
                        "registered_complete_endpoint_seconds": 1.25,
                    }],
                }

            output = root / "worker.json"
            run_worker(
                runtime_path=runtime, worker_index=0, output=output,
                runner=runner,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["parent_pid"], __import__("os").getpid())
            self.assertEqual(payload["leaf_cache"], {
                "mode": "not_applicable_to_v2_direct"
            })
            self.assertEqual(len(payload["rows"]), 1)

    def test_bad_receipt_fails_before_raw_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = self.runtime(root)
            bad = _receipt()
            bad["native_snapshot"]["unbound_launch_count"] = 1

            def runner(**kwargs):
                return {
                    "matched": True,
                    "default_selected_between_application_algorithms": False,
                    "comparator_inside_registered_timer": False,
                    "close_inside_registered_timer": True,
                    "loading_seconds_reported_separately": None,
                    "preparation_seconds_reported_separately": None,
                    "traversal_receipt": _bound_receipt(bad),
                    "phase_accounting": {
                        "loading_seconds": 0.1,
                        "preparation_seconds": 0.1,
                        "close_seconds": 0.05,
                        "row_execute_seconds": {
                            "particle__microfluidics_5000::complete": 1.0
                        },
                        "same_worker_mutually_exclusive_phases": True,
                        "nested_phase_medians_summed": False,
                    },
                    "rows": [{
                        "row_id": "particle__microfluidics_5000::complete",
                        "input_sha256": "a" * 64,
                        "output_sha256": "b" * 64,
                        "registered_complete_endpoint_seconds": 1.25,
                    }],
                }

            output = root / "worker.json"
            with self.assertRaises(RuntimeError):
                run_worker(
                    runtime_path=runtime, worker_index=0, output=output,
                    runner=runner,
                )
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
