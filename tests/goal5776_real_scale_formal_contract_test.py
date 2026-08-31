from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/goal5776_real_scale_formal_contract.py"


def _load():
    spec = importlib.util.spec_from_file_location("goal5776_contract", PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5776RealScaleFormalContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = _load()

    def test_exact_matrix_shape(self):
        c = self.contract
        self.assertEqual(len(c.UNITS), 32)
        self.assertEqual(len(c.FORMAL_UNITS), 15)
        self.assertEqual(len(c.statistical_rows(lifecycle=c.COLD)), 15)
        self.assertEqual(len(c.statistical_rows(lifecycle=c.PREPARED)), 19)
        self.assertEqual(len(c.statistical_rows()), 34)
        self.assertEqual(len(c.schedule()), 464)
        self.assertEqual(len(c.RTDBSCAN_CASES), 18)
        self.assertIn("goal5776_clustered3d_4096", c.RTDBSCAN_CASES)
        triangle = [unit for unit in c.UNITS if unit.app == "triangle_counting"]
        self.assertEqual(len(triangle), 6)
        self.assertEqual(
            {unit.workload for unit in triangle},
            {"com-dblp", "cit-Patents", "soc-LiveJournal1"},
        )
        rayjoin = next(unit for unit in c.UNITS if unit.app == "rayjoin")
        self.assertEqual(len(rayjoin.statistical_row_ids_for(c.COLD)), 1)
        self.assertEqual(len(rayjoin.statistical_row_ids_for(c.PREPARED)), 6)
        raydb = next(unit for unit in c.UNITS if unit.app == "raydb")
        self.assertEqual(raydb.unit_id, "raydb__ssb_sf10_q11")
        self.assertIn("Q1.1", raydb.workload)
        self.assertEqual(raydb.supported_lifecycles, (c.COLD,))
        self.assertEqual(raydb.statistical_row_ids_for(c.PREPARED), ())
        self.assertTrue(all(unit.input_identity_level for unit in c.UNITS))
        self.assertEqual(
            [unit.unit_id for unit in c.FORMAL_UNITS if unit.app == "rt_dbscan"],
            ["rtdbscan__goal5776_clustered3d_4096"],
        )
        document = c.contract_document()
        self.assertEqual(
            document["formal_unit_lifecycle_count_by_lifecycle"],
            {c.COLD: 15, c.PREPARED: 14},
        )
        self.assertEqual(document["formal_unit_lifecycle_count_total"], 29)
        self.assertEqual(len(document["formal_unit_ids"]), 15)
        self.assertEqual(len(document["functional_only_unit_ids"]), 17)
        self.assertEqual(
            document["correctness_contract"]
            ["fully_discrete_or_digest_exact_functional_paths"], 114)
        self.assertEqual(
            document["correctness_contract"]
            ["mixed_identity_exact_numeric_tolerance_functional_paths"], 12)

    def test_schedule_is_round_major_abba_and_pair_complete(self):
        c = self.contract
        grouped = {}
        for row in c.schedule():
            key = (row["lifecycle"], row["unit_id"], row["pair_index"])
            grouped.setdefault(key, []).append(row)
        self.assertEqual(len(grouped), len(c.schedule()) // 2)
        for (_, _, pair_index), rows in grouped.items():
            expected = list(c.METHODS if pair_index % 2 == 0 else reversed(c.METHODS))
            self.assertEqual([row["method"] for row in rows], expected)
            self.assertEqual([row["order_ordinal"] for row in rows], [0, 1])

    def test_timing_and_claim_boundaries_are_explicit(self):
        document = self.contract.contract_document()
        timer = document["timing_contract"]
        self.assertTrue(timer["v2_and_v4_same_endpoint_boundary"])
        self.assertTrue(
            timer["cold_immutable_input_loading_inside_timer_for_both_methods"])
        self.assertFalse(
            timer["prepared_immutable_input_loading_inside_execute_timer"])
        self.assertFalse(timer["correctness_comparator_inside_timer"])
        self.assertFalse(timer["prepared_work_is_free"])
        self.assertTrue(timer["first_build_callback_compilation_reported_separately"])
        self.assertFalse(timer["installed_leaf_cache_may_hide_first_build_cost"])
        stats = document["statistics_contract"]
        self.assertFalse(stats["cross_app_compensation_allowed"])
        self.assertFalse(stats["cross_lifecycle_compensation_allowed"])
        self.assertFalse(stats["rayjoin_derived_sum_is_independent"])
        self.assertFalse(document["claim_boundary"]["performance_result_exists"])
        self.assertFalse(document["claim_boundary"]["pod_authorized"])
        self.assertEqual(
            document["worker_contract"]["per_worker_timeout_seconds"], 1_800)
        self.assertTrue(
            document["worker_contract"]["worker_timeout_is_terminal_and_not_retried"])

    def test_application_algorithm_identity_is_never_default_selected(self):
        document = self.contract.contract_document()
        self.assertFalse(
            document["worker_contract"]
            ["default_may_select_between_application_algorithms"]
        )
        triangle = [unit for unit in self.contract.UNITS
                    if unit.app == "triangle_counting"]
        self.assertEqual({unit.paper_algorithm for unit in triangle},
                         {"RT-1A2", "RT-2A1"})

    def test_leaf_cache_applicability_is_semantic_and_exact(self):
        not_applicable = {
            unit.unit_id for unit in self.contract.UNITS
            if not unit.v4_numba_leaf_cache_required
        }
        self.assertEqual(not_applicable, {
            "rtbh__author_32768",
            "librts__parks_point_contains",
            "librts__parks_range_contains",
        })


if __name__ == "__main__":
    unittest.main()
