from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5792_build_local_completion.py"


def _module():
    spec = importlib.util.spec_from_file_location("goal5792_local_completion", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5792LocalCompletionTest(unittest.TestCase):
    def test_exact_components_build_local_completion_without_authorization(self) -> None:
        result = _module().build_result(ROOT)
        self.assertEqual(
            "LOCAL_EVIDENCE_COMPLETE__OWNER_REVIEW_REQUIRED__NO_EXECUTION_AUTHORITY",
            result["status"],
        )
        self.assertTrue(result["completion"]["goal5792_local_required_work_complete"])
        self.assertFalse(result["completion"]["owner_returned_external_review_complete"])
        self.assertEqual(6, result["semantic_decision_evidence"]["semantic_compatible_count"])
        self.assertEqual(9, result["semantic_decision_evidence"]["semantic_unknown_fail_closed_count"])
        self.assertEqual(6, result["negative_decision_evidence"]["product_admission_fail_closed_count"])
        self.assertEqual(8, result["responsibility_evidence"][
            "native_runtime_loading_behind_registered_interface_count"])
        self.assertEqual(["raydb"], result["responsibility_evidence"][
            "native_runtime_loading_exception_applications"])
        self.assertTrue(all(value is False for value in result["authorization"].values()))

    def test_all_pin_hashes_are_full_length_and_distinct_roles_are_visible(self) -> None:
        module = _module()
        self.assertGreaterEqual(len(module.PINS), 20)
        self.assertTrue(all(len(value[1]) == 64 for value in module.PINS.values()))
        self.assertIn("clean_linux_raw", module.PINS)
        self.assertIn("negative_result", module.PINS)
        self.assertIn("responsibility_result_v3", module.PINS)
        self.assertIn("hygiene_result_v2", module.PINS)


if __name__ == "__main__":
    unittest.main()
