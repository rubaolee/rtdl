from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "barnes_hut"
    / "rtdl_barnes_hut_benchmark_app.py"
)
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2638_aggregate_frontier_collect_2026-05-27.md"
CATALOG = REPO_ROOT / "docs" / "rtdl_primitive_catalog.md"
ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
AGGREGATE_ENGINE = REPO_ROOT / "src" / "rtdsl" / "aggregate_tree_reference.py"
APP_REFERENCE = REPO_ROOT / "src" / "rtdsl" / "app_reference" / "aggregate_force_math.py"

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

import rtdsl as rt
from examples.v2_0.apps.simulation import rtdl_barnes_hut_force_app as app


class Goal2638AggregateFrontierCollectTest(unittest.TestCase):
    def test_collect_matches_existing_opening_frontier_ids(self) -> None:
        bodies = app.make_generated_bodies(128)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=8)
        opening = rt.evaluate_aggregate_tree_opening_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
        )
        collected = rt.collect_aggregate_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
        )

        self.assertEqual(
            collected["metadata"]["contract"],
            rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT,
        )
        self.assertEqual(
            collected["summary"]["accepted_aggregate_row_count"],
            opening["summary"]["accepted_aggregate_row_count"],
        )
        self.assertEqual(
            collected["summary"]["fallback_exact_row_count"],
            opening["summary"]["fallback_exact_row_count"],
        )
        self.assertEqual(
            collected["summary"]["visited_node_total"],
            opening["summary"]["visited_node_total"],
        )

        accepted_from_opening = {
            (int(row["source_id"]), int(row["aggregate_id"]))
            for row in opening["accepted_aggregate_rows"]
        }
        accepted_from_collect = {
            (int(row["source_id"]), int(row["item_id"]))
            for row in collected["frontier_rows"]
            if row["frontier_kind_code"] == 1
        }
        exact_from_opening = {
            (int(row["source_id"]), int(row["target_id"]), int(row["aggregate_id"]))
            for row in opening["fallback_exact_rows"]
        }
        exact_from_collect = {
            (int(row["source_id"]), int(row["item_id"]), int(row["owner_aggregate_id"]))
            for row in collected["frontier_rows"]
            if row["frontier_kind_code"] == 2
        }

        self.assertEqual(accepted_from_collect, accepted_from_opening)
        self.assertEqual(exact_from_collect, exact_from_opening)
        self.assertEqual(collected["row_offsets"][-1], collected["summary"]["frontier_row_count"])
        self.assertEqual(len(collected["row_offsets"]), len(collected["source_ids"]) + 1)
        for source_id, start, end in zip(
            collected["source_ids"],
            collected["row_offsets"][:-1],
            collected["row_offsets"][1:],
            strict=True,
        ):
            self.assertEqual(
                {row["source_id"] for row in collected["frontier_rows"][start:end]},
                ({source_id} if end > start else set()),
            )
        self.assertEqual(collected["row_schema"], rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA)
        self.assertEqual(len(collected["frontier_i64_rows"]), collected["summary"]["frontier_row_count"])
        schema = rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA
        kind_index = schema.index("frontier_kind_code")
        resume_index = schema.index("resume_index")
        flags_index = schema.index("metadata_flags")
        kind_codes = {row[kind_index] for row in collected["frontier_i64_rows"]}
        self.assertTrue(kind_codes.issubset({1, 2}))
        self.assertIn(2, kind_codes)
        self.assertTrue(any(row[resume_index] == -1 for row in collected["frontier_i64_rows"]))
        for row in collected["frontier_i64_rows"]:
            self.assertEqual(len(row), len(rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA))
            self.assertEqual(row[flags_index], rt.AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE)

    def test_collect_is_ids_only_and_keeps_force_math_out(self) -> None:
        bodies = app.make_generated_bodies(32)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=4)
        collected = rt.collect_aggregate_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
        )

        forbidden_fields = {
            "force_x",
            "force_y",
            "vector_x",
            "vector_y",
            "aggregate_mass",
            "mass",
            "distance",
            "opening_ratio",
        }
        for row in collected["frontier_rows"]:
            with self.subTest(row=row):
                self.assertFalse(forbidden_fields.intersection(row))
                self.assertIn("metadata_flags", row)
        self.assertNotIn("debug_diagnostics", collected)
        self.assertFalse(collected["metadata"]["debug_diagnostics_included"])
        self.assertFalse(collected["metadata"]["app_math_embedded"])
        self.assertFalse(collected["metadata"]["force_law_embedded"])
        self.assertFalse(collected["metadata"]["native_engine_app_specific"])
        self.assertIn(
            rt.AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE,
            collected["metadata"]["metadata_flags_semantics"],
        )
        self.assertEqual(
            collected["metadata"]["frontier_row_extra_fields_reference_only"],
            ("frontier_kind", "aggregate_id", "target_id"),
        )
        self.assertEqual(
            collected["metadata"]["partner_lowering_status"],
            "row_major_i64_frontier_ids_partner_ready",
        )

    def test_collect_debug_diagnostics_are_opt_in_side_channel(self) -> None:
        bodies = app.make_generated_bodies(16)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=4)
        collected = rt.collect_aggregate_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
            include_debug_diagnostics=True,
        )

        self.assertTrue(collected["metadata"]["debug_diagnostics_included"])
        self.assertEqual(len(collected["debug_diagnostics"]), collected["summary"]["frontier_row_count"])
        self.assertNotIn("distance", collected["frontier_rows"][0])
        self.assertIn("distance", collected["debug_diagnostics"][0])
        self.assertIn("opening_ratio", collected["debug_diagnostics"][0])

    def test_columnar_adapter_and_lowering_plan_are_explicit(self) -> None:
        bodies = app.make_generated_bodies(32)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=4)
        collected = rt.collect_aggregate_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
        )
        record_set = rt.aggregate_frontier_collect_to_columnar_record_set(collected)
        self.assertEqual(record_set["metadata"]["contract"], rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT)
        self.assertEqual(tuple(record_set["columns"]), rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA)
        self.assertIn("metadata_flags", record_set["columns"])
        self.assertTrue(record_set["metadata"]["partner_i64_row_layout_ready"])
        self.assertNotIn("partner_resident_ready", record_set["metadata"])
        self.assertIn(
            rt.AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE,
            record_set["metadata"]["metadata_flags_semantics"],
        )
        self.assertEqual(len(record_set["row_ids"]), collected["summary"]["frontier_row_count"])
        self.assertEqual(record_set["row_offsets"], collected["row_offsets"])

        cpu_plan = rt.plan_aggregate_frontier_collect_lowering("cpu")
        partner_plan = rt.plan_aggregate_frontier_collect_lowering("partner")
        optix_plan = rt.plan_aggregate_frontier_collect_lowering("optix")
        self.assertTrue(cpu_plan["executable"])
        self.assertEqual(partner_plan["status"], "implemented_partner_column_adapter")
        self.assertTrue(optix_plan["executable"])
        self.assertIn("pod_parity_validated", optix_plan["status"])
        self.assertIn("timing_baseline_recorded", optix_plan["status"])
        self.assertIn("rtdl_optix_collect_aggregate_frontier_2d", optix_plan["required_native_symbol"])

        adapters = ADAPTERS.read_text(encoding="utf-8")
        self.assertIn("def aggregate_frontier_collect_to_partner_columns", adapters)
        self.assertIn("force_law_embedded", adapters)
        self.assertIn("native_rt_execution", adapters)
        self.assertIn("metadata_flags_semantics", adapters)

    def test_collect_fails_closed_on_capacity_overflow(self) -> None:
        bodies = app.make_generated_bodies(64)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=4)
        collected = rt.collect_aggregate_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
        )

        rt.collect_aggregate_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
            max_total_rows=collected["summary"]["frontier_row_count"],
        )
        max_source_rows = max(
            item["frontier_count"] for item in collected["per_source_summary"].values()
        )
        rt.collect_aggregate_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
            max_rows_per_source=max_source_rows,
        )
        with self.assertRaisesRegex(rt.AggregateFrontierOverflowError, "partial_result_returned=False"):
            rt.collect_aggregate_frontier_2d(
                bodies,
                tree["nodes"],
                theta=app.THETA,
                max_total_rows=0,
            )
        with self.assertRaisesRegex(rt.AggregateFrontierOverflowError, "attempted"):
            rt.collect_aggregate_frontier_2d(
                bodies,
                tree["nodes"],
                theta=app.THETA,
                max_rows_per_source=0,
            )

    def test_single_body_tree_has_empty_frontier(self) -> None:
        bodies = app.make_generated_bodies(1)
        tree = rt.build_bucketized_aggregate_tree_2d(bodies, bucket_size=4)
        collected = rt.collect_aggregate_frontier_2d(
            bodies,
            tree["nodes"],
            theta=app.THETA,
        )

        self.assertEqual(collected["frontier_rows"], ())
        self.assertEqual(collected["frontier_i64_rows"], ())
        self.assertEqual(collected["row_offsets"], (0, 0))
        self.assertEqual(collected["summary"]["frontier_row_count"], 0)

    def test_deduplicate_fallback_targets_toggle_is_exact(self) -> None:
        points = (
            {"id": 0, "x": 0.0, "y": 0.0, "mass": 1.0},
            {"id": 1, "x": 1.0, "y": 0.0, "mass": 1.0},
        )
        overlapping_leaf_roots = (
            {
                "id": 10,
                "cx": 0.0,
                "cy": 0.0,
                "half_size": 1.0,
                "mass": 2.0,
                "member_ids": (0, 1),
                "child_ids": (),
                "depth": 0,
                "dfs_index": 0,
                "resume_index": None,
                "cell_cx": 0.0,
                "cell_cy": 0.0,
                "is_leaf": True,
            },
            {
                "id": 11,
                "cx": 1.0,
                "cy": 0.0,
                "half_size": 1.0,
                "mass": 1.0,
                "member_ids": (1,),
                "child_ids": (),
                "depth": 0,
                "dfs_index": 1,
                "resume_index": None,
                "cell_cx": 1.0,
                "cell_cy": 0.0,
                "is_leaf": True,
            },
        )

        deduped = rt.collect_aggregate_frontier_2d(
            points,
            overlapping_leaf_roots,
            theta=0.01,
            deduplicate_fallback_targets=True,
        )
        duplicated = rt.collect_aggregate_frontier_2d(
            points,
            overlapping_leaf_roots,
            theta=0.01,
            deduplicate_fallback_targets=False,
        )

        self.assertEqual(deduped["summary"]["fallback_exact_row_count"], 2)
        self.assertEqual(duplicated["summary"]["fallback_exact_row_count"], 3)
        self.assertFalse(duplicated["metadata"]["deduplicate_fallback_targets"])

    def test_barnes_hut_cli_exposes_collect_mode(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                "aggregate_frontier_collect_bucketized_cpu",
                "--body-count",
                "64",
                "--bucket-size",
                "8",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src:."},
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["benchmark_metadata"]["mode"], "aggregate_frontier_collect_bucketized_cpu")
        self.assertEqual(payload["benchmark_metadata"]["contract"], rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT)
        self.assertFalse(payload["benchmark_metadata"]["native_engine_app_specific"])
        self.assertIn("force math remains app or partner code", payload["boundary"])
        self.assertEqual(
            payload["frontier_collection"]["metadata"]["native_lowering_status"],
            "cpu_reference_contract_native_backend_separate_lowering",
        )

    def test_docs_record_contract_boundary(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        catalog = CATALOG.read_text(encoding="utf-8")
        for text in (readme, report, catalog):
            with self.subTest(doc=text[:64]):
                self.assertIn("AGGREGATE_FRONTIER_COLLECT_2D", text)
                self.assertIn("force", text.lower())
        self.assertIn("aggregate-frontier collect rows", catalog)
        self.assertIn("local Embree native", report)
        self.assertIn("OptiX lowering remains future work", report)
        self.assertIn("partner-ready row-layout", report)
        self.assertIn("metadata_flags", report)
        self.assertIn("debug_diagnostics", report)

    def test_force_math_is_in_app_reference_not_aggregate_engine(self) -> None:
        engine_text = AGGREGATE_ENGINE.read_text(encoding="utf-8")
        app_reference_text = APP_REFERENCE.read_text(encoding="utf-8")

        self.assertNotIn("def _contribution_vector", engine_text)
        self.assertNotIn("def sum_weighted_inverse_square_contributions_2d", engine_text)
        self.assertIn("def _contribution_vector", app_reference_text)
        self.assertIn("app_reference_math", app_reference_text)


if __name__ == "__main__":
    unittest.main()
