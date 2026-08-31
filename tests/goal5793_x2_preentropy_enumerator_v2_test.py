from __future__ import annotations

import copy
import unittest

from scripts import goal5793_x2_offline_core as core
from scripts import goal5793_x2_preentropy_enumerator as v1
from scripts import goal5793_x2_preentropy_enumerator_v2 as v2
from tests.goal5793_x2_harvester_enumerator_test import _science


def _fixture(rows):
    return {
        "schema": "rtdl.goal5793.x2.preentropy_science_fixture.v1",
        "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
        "synthetic_fixture": True,
        "network_call_count": 0,
        "examiner_invocation_count": 0,
        "candidate_implementation_count": 0,
        "rows": rows,
    }


class Goal5793X2PreentropyEnumeratorV2Test(unittest.TestCase):
    def test_01_unmapped_row_is_preserved_and_counted_without_batch_abort(self) -> None:
        positives, _ = v1.load_positive_vectors()
        rows = [
            _science("A", dict(positives[0], ray_construction="FINITE_SEGMENT"), "COMPATIBLE", "problem_a"),
            _science("B", dict(positives[1], geometry_family="INSTANCED_CURVE_OR_SPHERE_PRIMITIVE"), "UNKNOWN", "problem_b"),
            _science("C", dict(positives[2], composition="COMMUTATIVE_CHECKED_REDUCTION"), "UNKNOWN", "problem_c", risk="continuation"),
        ]
        result = v2.build_fixture_result(_fixture(rows))
        self.assertEqual(result["counts"]["input_rows"], 3)
        self.assertEqual(result["counts"]["mapped_rows"], 2)
        self.assertEqual(result["counts"]["unmapped_rows"], 1)
        self.assertEqual(result["counts"]["unmapped_by_axis"]["geometry_family"], 1)
        self.assertEqual(len(result["validated_rows"]), 3)
        row = next(item for item in result["validated_rows"] if item["candidate_id"] == "B")
        self.assertEqual(row["structural_mapping_status"], v2.UNMAPPED_STATUS)
        self.assertEqual(row["unmapped_structural_values"], [{"axis": "geometry_family", "value": "INSTANCED_CURVE_OR_SPHERE_PRIMITIVE"}])
        self.assertFalse(row["selection_eligible"])
        self.assertFalse(row["role_A"] or row["role_B"] or row["role_C"])

    def test_02_all_unmapped_axes_and_values_are_sealed_in_denominator(self) -> None:
        positives, _ = v1.load_positive_vectors()
        vector = dict(positives[0], geometry_family="CURVE", primitive_type="SPHERE", continuation="RECURSIVE")
        result = v2.build_fixture_result(_fixture([_science("U", vector, "UNKNOWN", "problem_u")]))
        self.assertEqual(result["counts"]["unmapped_rows"], 1)
        self.assertEqual(result["counts"]["unmapped_by_axis"]["geometry_family"], 1)
        self.assertEqual(result["counts"]["unmapped_by_axis"]["primitive_type"], 1)
        self.assertEqual(result["counts"]["unmapped_by_axis"]["continuation"], 1)
        self.assertEqual(result["counts"]["unmapped_values_by_axis"]["geometry_family"], ["CURVE"])

    def test_03_non_taxonomy_defect_still_fails_closed(self) -> None:
        positives, _ = v1.load_positive_vectors()
        row = _science("U", dict(positives[0], geometry_family="CURVE"), "UNKNOWN", "problem_u")
        row["source_basis_exact"] = "yes"
        with self.assertRaisesRegex(core.X2Error, "SCIENCE_ROW_BOOL_ALIAS_INVALID"):
            v2.build_fixture_result(_fixture([row]))

    def test_04_order_independent_and_claim_ceiling_exact(self) -> None:
        positives, _ = v1.load_positive_vectors()
        rows = [
            _science("M", dict(positives[0]), "UNKNOWN", "problem_m"),
            _science("U", dict(positives[1], geometry_family="CURVE"), "UNKNOWN", "problem_u"),
        ]
        forward = v2.build_fixture_result(_fixture(rows))
        reverse = v2.build_fixture_result(_fixture(list(reversed(copy.deepcopy(rows)))))
        self.assertEqual(forward, reverse)
        self.assertFalse(forward["claim_language"]["role_diversity_supports_structural_novelty_or_coverage_claim"])
        self.assertFalse(forward["claim_language"]["role_A_supports_arbitrary_literature_capability_claim"])
        self.assertFalse(forward["claim_language"]["randomly_selected_from_the_literature_without_qualification_allowed"])
        self.assertFalse(any(forward["authorization"].values()))


if __name__ == "__main__":
    unittest.main()
