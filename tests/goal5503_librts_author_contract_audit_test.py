from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "audit_goal5503_author_range_intersects_contract.py"
SPEC = importlib.util.spec_from_file_location("goal5503_audit", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5503AuthorContractAuditTest(unittest.TestCase):
    def test_required_source_contract_checks_are_explicit(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for needle in (
            "using coord_t = float;",
            "Predicate::kIntersects",
            "other.min_.get_coordinate(dim) <= max_.get_coordinate(dim)",
            "other.max_.get_coordinate(dim) >= min_.get_coordinate(dim)",
            "EnvelopeToOptixAabb<double, 2>",
            "double_path_used_by_benchmark",
            "struct RayParams<float, 2>",
            "nextafterf(1.0, FLT_MAX)",
            "FLT_GAMMA(3)",
            "ray_params.Compute(query, true)",
            "bool query_hit = ray_params.IsHit(envelope)",
            "bool box_hit = ray_params.IsHit(query)",
            "cpu_reference_and_gpu_predicate_equivalence_proven",
        ):
            self.assertIn(needle, text)

    def test_audit_does_not_authorize_core_change(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"rtdl_core_change_authorized": False', text)
        self.assertIn('"author_validity_proven_for_full_inputs": False', text)


if __name__ == "__main__":
    unittest.main()
