from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3424_closed_shape_instance_identity_refinement_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3424_closed_shape_instance_identity_refinement_probe_2026-06-04.json"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
TOPOLOGY = ROOT / "src" / "rtdsl" / "closed_shape_topology.py"
SCRIPT = ROOT / "scripts" / "goal3424_closed_shape_instance_identity_refinement_probe.py"


class Goal3424ClosedShapeInstanceIdentityRefinementTest(unittest.TestCase):
    def test_native_pair_column_stream_has_optional_ordinal_columns(self):
        prelude = PRELUDE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("left_ordinals_device_ptr", prelude)
        self.assertIn("right_ordinals_device_ptr", prelude)
        self.assertIn("point_ordinals_out", workloads)
        self.assertIn("shape_ordinals_out", workloads)
        self.assertIn("params.point_index_offset + pidx", workloads)
        self.assertIn(
            "(unsigned long long)params.point_index_offset + (unsigned long long)pidx",
            workloads,
        )
        self.assertIn("params.shape_ordinals_out[slot] = (unsigned long long)prim", workloads)
        self.assertIn(
            "lp.point_ids = reinterpret_cast<const uint32_t*>(chunk_point_ids);\n"
            "        lp.point_index_offset = static_cast<uint32_t>(point_offset);\n"
            "        lp.probe_count = static_cast<uint32_t>(chunk_point_count);",
            workloads,
        )

    def test_python_runtime_exposes_instance_columns_without_renaming_public_ids(self):
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn('("left_ordinals_device_ptr", ctypes.c_uint64)', runtime)
        self.assertIn("def has_instance_identity_columns", runtime)
        self.assertIn('ordinal_field_names=("point_ordinal", "shape_ordinal")', runtime)
        self.assertIn("columns[self.ordinal_field_names[0]]", runtime)
        self.assertIn("public_id_columns_preserved", runtime)

    def test_cupy_refinement_uses_ordinals_when_available(self):
        topology = TOPOLOGY.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("candidate_point_ordinals", topology)
        self.assertIn("use_instance_ordinals", topology)
        self.assertIn("instance_identity_columns_used", topology)
        self.assertIn("must provide both point and shape ordinals or neither", topology)
        self.assertIn("out-of-range input ordinal", topology)
        self.assertIn("out-of-range prepared-shape ordinal", topology)
        self.assertIn("candidate_pages_have_instance_identity_columns", script)
        self.assertIn("refined_pages_used_instance_identity_columns", script)
        self.assertIn("public_id_columns_preserved", script)

    def test_cupy_ordinal_mode_preserves_duplicate_public_id_instances(self):
        try:
            import cupy as cp  # type: ignore
            from rtdsl.closed_shape_topology import (
                refine_closed_shape_membership_candidate_columns_exact_cupy,
            )
        except Exception as exc:  # pragma: no cover
            self.skipTest(f"CuPy closed-shape refiner unavailable: {exc}")

        try:
            points = (
                {"id": 7, "x": 0.25, "y": 0.25},
                {"id": 7, "x": 2.25, "y": 2.25},
            )
            shapes = (
                {"id": 9, "vertices": ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))},
                {"id": 9, "vertices": ((2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0))},
            )
            candidates = {
                "point_id": cp.asarray([7, 7], dtype=cp.int64),
                "shape_id": cp.asarray([9, 9], dtype=cp.int64),
                "point_ordinal": cp.asarray([0, 1], dtype=cp.int64),
                "shape_ordinal": cp.asarray([0, 1], dtype=cp.int64),
            }
            result = refine_closed_shape_membership_candidate_columns_exact_cupy(
                candidates,
                points,
                shapes,
            )
        except Exception as exc:  # pragma: no cover
            self.skipTest(f"CuPy closed-shape refiner could not execute: {exc}")

        self.assertTrue(result["instance_identity_columns_used"])
        self.assertEqual(result["row_count"], 2)
        pairs = list(
            zip(
                cp.asnumpy(result["point_id"]).tolist(),
                cp.asnumpy(result["shape_id"]).tolist(),
            )
        )
        self.assertEqual(pairs, [(7, 9), (7, 9)])

    def test_report_records_duplicate_id_diagnosis_and_claim_boundary(self):
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("duplicate public point ids", report)
        self.assertIn("duplicate public closed-shape ids", report)
        self.assertIn("point_ordinal, shape_ordinal", report)
        self.assertIn("47,570", report)
        self.assertIn("47,262", report)
        self.assertIn("exact multiset match", report)
        self.assertIn("claims remain", report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3424 pod artifact pending")
    def test_pod_artifact_records_full_cdb_gap_closure(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3424.closed_shape_instance_identity_refinement_probe.v1")
        self.assertEqual(payload["goal"], 3424)
        self.assertIn("NVIDIA", payload["gpu"])
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)
        self.assertEqual(payload["point_public_id_stats"]["duplicate_public_id_count"], 65)
        self.assertEqual(payload["shape_public_id_stats"]["duplicate_public_id_count"], 60)
        self.assertEqual(payload["host_exact_pair_count"], 47262)
        self.assertEqual(payload["rt_candidate_pair_count"], 47570)
        self.assertEqual(payload["cupy_refined_pair_count"], 47262)
        self.assertEqual(payload["dropped_candidate_pair_count"], 308)
        self.assertTrue(payload["candidate_pages_have_instance_identity_columns"])
        self.assertTrue(payload["refined_pages_used_instance_identity_columns"])
        self.assertTrue(payload["pair_multiset_match_host_exact"])
        self.assertTrue(payload["group_counts_match_host"])
        self.assertEqual(payload["pair_missing_from_refined_sample"], [])
        self.assertEqual(payload["pair_extra_on_refined_sample"], [])
        self.assertEqual(payload["mismatched_group_value_count"], 0)

        boundary = payload["refinement_boundary"]
        self.assertTrue(boundary["instance_identity_columns_produced"])
        self.assertTrue(boundary["instance_identity_columns_used_by_partner"])
        self.assertTrue(boundary["refined_columns_match_host_exact_on_this_dataset"])
        self.assertFalse(boundary["native_exact_device_predicate_implemented"])
        for key, value in payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
