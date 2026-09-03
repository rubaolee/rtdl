from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5838_build_final_authority.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "goal5838_build_final_authority", SCRIPT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Goal5838 final authority builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5838FinalAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_module()
        cls.authority = cls.module.build_authority()

    def test_stored_authority_rederives_exactly(self):
        stored = self.module._load(self.module.AUTHORITY_PATH)
        self.assertEqual(stored, self.authority)
        self.assertEqual(
            stored["authority_sha256"], self.module._authority_seal(stored)
        )

    def test_completion_is_exactly_bounded(self):
        self.assertEqual(
            self.authority["status"],
            "PASS__GOAL5838_COMPLETE_AT_PREREGISTERED_BOUNDED_SCOPE",
        )
        self.assertTrue(self.authority["completion"]["goal5838_complete"])
        self.assertEqual(
            self.authority["prospective_result"],
            {
                "frozen_core_changed_file_count": 0,
                "oracle_case_count": 12,
                "oracle_exact_match_count": 12,
                "true_optix_launch_count": 2,
            },
        )
        boundary = self.authority["claim_boundary"]
        self.assertTrue(
            boundary["one_bounded_prospective_frozen_core_topology_result"]
        )
        self.assertFalse(boundary["arbitrary_callback_ir_gpu_execution"])
        self.assertFalse(boundary["performance_or_speedup"])
        self.assertFalse(boundary["external_review_or_consensus"])

    def test_authority_seal_rejects_resealed_semantic_drift(self):
        tampered = copy.deepcopy(self.authority)
        tampered["prospective_result"]["oracle_exact_match_count"] = 11
        self.assertNotEqual(
            tampered["authority_sha256"], self.module._authority_seal(tampered)
        )


if __name__ == "__main__":
    unittest.main()
