from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "Paper-reproduction-apps"
    / "librts-paper"
    / "results"
    / "goal5503_author_contract_audit.json"
)


class Goal5503AuthorContractAuditResultTest(unittest.TestCase):
    def test_gpu_contract_is_audited_separately_from_cpu_reference(self) -> None:
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.librts.goal5503_author_range_intersects_contract.v2",
        )
        self.assertEqual(payload["status"], "author_contract_audit_completed")
        self.assertEqual(
            payload["exit_label"],
            "author_float32_gpu_rayparams_contract_audited_cpu_reference_distinguished",
        )
        contract = payload["contract"]
        self.assertEqual(contract["benchmark_coordinate_type"], "float32")
        self.assertEqual(
            contract["benchmark_cpu_reference_predicate"],
            "inclusive_aabb_intersects",
        )
        self.assertEqual(
            contract["benchmark_gpu_predicate"],
            "float32_rayparams_slab_hit_with_nextafter_t1_and_tfar_gamma",
        )
        self.assertFalse(contract["cpu_reference_and_gpu_predicate_equivalence_proven"])
        self.assertEqual(contract["benchmark_gpu_t0"], 0.0)
        self.assertEqual(contract["benchmark_gpu_t1"], "nextafterf(1.0, FLT_MAX)")
        self.assertEqual(contract["benchmark_gpu_tfar_multiplier"], "1 + 2 * FLT_GAMMA(3)")
        self.assertTrue(payload["claim_boundary"]["author_contract_source_audited"])
        self.assertFalse(payload["claim_boundary"]["author_validity_proven_for_full_inputs"])
        self.assertFalse(payload["claim_boundary"]["rtdl_core_change_authorized"])

        labels = {check["label"] for check in payload["checks"] if check["present"]}
        self.assertIn("gpu_float_ray_params_specialization_exists", labels)
        self.assertIn("gpu_float_hit_interval_uses_nextafter_one", labels)
        self.assertIn("gpu_float_hit_interval_expands_tfar", labels)
        self.assertIn("gpu_forward_intersects_tests_envelope_with_ray", labels)
        self.assertIn("gpu_forward_intersects_tests_query_with_reverse_ray", labels)


if __name__ == "__main__":
    unittest.main()
