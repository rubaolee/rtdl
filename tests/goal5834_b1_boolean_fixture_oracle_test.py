"""Scientific fixture/oracle tests for Goal5834-B1."""

from __future__ import annotations

import inspect
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.curve_boolean_contact import fixtures  # noqa: E402
from examples.curve_boolean_contact import independent_oracle  # noqa: E402
from rtdsl.v4_curve import (  # noqa: E402
    BuiltinCurveStaticInput,
    CurveBooleanSegmentBatch,
)
from rtdsl.v4_public_builtin_curve import PublicCurveLifecycleError  # noqa: E402


class Goal5834B1BooleanFixtureOracleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = fixtures.build_evaluation_manifest()

    def test_exact_frozen_denominators_and_expected_bits(self):
        self.assertEqual(self.manifest["fixture_family_count"], 10)
        self.assertEqual(self.manifest["concrete_gpu_execution_count"], 11)
        self.assertEqual(self.manifest["generalization_exam_count"], 0)
        rows = {row["execution_id"]: row
                for row in self.manifest["executable"]}
        self.assertEqual(rows["single_crossing_hit"]["canonical_oracle"][
            "per_query_hit"], (1,))
        self.assertEqual(rows["clear_miss"]["canonical_oracle"][
            "per_query_hit"], (0,))
        self.assertEqual(rows["piecewise_linear_or"]["canonical_oracle"][
            "per_query_hit"], (0, 1, 0))
        self.assertEqual(rows["face_interior_only_boundary"][
            "canonical_oracle"]["collision"], 0)

    def test_old_numeric_disagreements_reduce_only_to_boolean_hit(self):
        rows = {row["family_id"]: row
                for row in self.manifest["executable"]}
        for family in (
            "ordinary_provider_t_disagreement_regression",
            "near_coincident_id_disagreement_regression",
            "float32_tie_id_disagreement_regression",
        ):
            self.assertEqual(rows[family]["canonical_oracle"]["collision"], 1)
            self.assertNotIn("t_bits", rows[family]["canonical_oracle"])
            self.assertNotIn("application_id", rows[family]["canonical_oracle"])

    def test_scene_normalization_eliminates_large_translation_bytes(self):
        rows = {row["execution_id"]: row
                for row in self.manifest["executable"]}
        base = rows["large_translation_base"]
        translated = rows["large_translation_transformed"]
        self.assertNotEqual(
            base["normalization"]["original_input_sha256"],
            translated["normalization"]["original_input_sha256"])
        self.assertEqual(
            base["normalization"]["normalized_input_sha256"],
            translated["normalization"]["normalized_input_sha256"])
        self.assertEqual(
            base["canonical_oracle"]["per_query_hit"],
            translated["canonical_oracle"]["per_query_hit"])

    def test_oracle_is_independent_and_worker_admission_is_non_geometric(self):
        oracle_source = inspect.getsource(independent_oracle)
        fixture_source = inspect.getsource(fixtures)
        self.assertNotIn("rtdsl", oracle_source.lower())
        self.assertNotIn("rtdsl", fixture_source.lower())
        from rtdsl.v4_curve_physical_schema import (
            verify_curve_boolean_motion_segments,
        )
        worker_source = inspect.getsource(verify_curve_boolean_motion_segments)
        worker_names = set(verify_curve_boolean_motion_segments.__code__.co_names)
        worker_parameters = set(inspect.signature(
            verify_curve_boolean_motion_segments).parameters)
        for forbidden in (
            "evaluate_scene", "segment_segment_distance2", "capsule_entry",
            "control_points", "widths", "segment_indices",
        ):
            self.assertNotIn(forbidden, worker_names)
            self.assertNotIn(forbidden, worker_parameters)
        self.assertIn("intentionally accepts no static geometry", worker_source)

    def test_commitments_use_public_runtime_framing(self):
        for row in self.manifest["executable"]:
            static = fixtures.runtime_static_input(row)
            public_static = BuiltinCurveStaticInput(**static)
            public_batch = CurveBooleanSegmentBatch(
                row["normalization"]["queries"])
            self.assertEqual(len(public_static.commitment_sha256), 64)
            self.assertEqual(len(public_batch.commitment_sha256), 64)
            self.assertNotEqual(
                public_static.commitment_sha256, public_batch.commitment_sha256)

    def test_boundary_rows_launch_zero_and_malformed_public_input_rejects(self):
        self.assertEqual(self.manifest["evaluator_ineligible_execution_count"], 2)
        for row in self.manifest["boundary"]:
            self.assertEqual(row["eligibility"], "INELIGIBLE")
            self.assertTrue(row["ineligibility_reasons"])
        with self.assertRaises(PublicCurveLifecycleError):
            CurveBooleanSegmentBatch((((0, 0), (1, 0, 0)),))
        with self.assertRaises(PublicCurveLifecycleError):
            CurveBooleanSegmentBatch((((0, 0, 0), (0, 0, 0)),))

    def test_all_executable_pairs_obey_frozen_margins(self):
        for fixture_row in self.manifest["executable"]:
            self.assertTrue(fixture_row["oracle_boolean_equal"])
            self.assertEqual(fixture_row["eligibility"], "ELIGIBLE")
            for pair in fixture_row["canonical_oracle"]["pair_rows"]:
                self.assertGreaterEqual(
                    pair["decision_separation"], fixtures.EVALUATION_MARGIN)
                self.assertTrue(pair["both_query_endpoints_outside"])
                if pair["hit"]:
                    self.assertGreaterEqual(
                        pair["direction_cross_ratio"],
                        fixtures.DIRECTION_CROSS_RATIO_MARGIN)
                    self.assertGreaterEqual(
                        pair["entry_parameter"], fixtures.ENTRY_ENDPOINT_MARGIN)
                    self.assertLessEqual(
                        pair["entry_parameter"],
                        1.0 - fixtures.ENTRY_ENDPOINT_MARGIN)


if __name__ == "__main__":
    unittest.main()
