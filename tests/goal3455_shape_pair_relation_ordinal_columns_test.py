from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
SCRIPT = ROOT / "scripts" / "goal3455_shape_pair_relation_ordinal_columns_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3455_shape_pair_relation_ordinal_columns_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3455_shape_pair_relation_ordinal_columns_pod_2026-06-05.json"


class Goal3455ShapePairRelationOrdinalColumnsTest(unittest.TestCase):
    def test_native_stream_writes_ordinals_alongside_ids(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        for phrase in (
            "left_ordinals_device_ptr",
            "right_ordinals_device_ptr",
        ):
            self.assertIn(phrase, prelude)
            self.assertIn(phrase, workloads)

        for phrase in (
            "uint32_t* left_ordinals_out",
            "uint32_t* right_ordinals_out",
            "left_ordinals_out[slot] = li",
            "right_ordinals_out[slot] = ri",
        ):
            self.assertIn(phrase, core)

    def test_python_runtime_exposes_ordinals_without_dense_id_assumption(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        for phrase in (
            "def as_cupy_ordinal_columns(",
            "left_ordinals_device_ptr",
            "right_ordinals_device_ptr",
            "zero_based_index_into_shape_pair_geometry_payload_arrays",
            "sparse_user_ids_are_not_dense_geometry_indices",
        ):
            self.assertIn(phrase, runtime)

    def test_probe_and_report_record_boundary(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3455.shape_pair_relation_ordinal_columns.v1",
            "as_cupy_ordinal_columns",
            "ordinal_rows_match",
            "metadata_ordinal_columns",
        ):
            self.assertIn(phrase, script)

        for phrase in (
            "Goal3455",
            "Sparse ids are correct output identity",
            "not safe indices into geometry payload arrays",
            "does not authorize",
            "bounded generic witness/area continuation",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3455 pod artifact pending")
    def test_pod_artifact_ordinals_match_sparse_fixture(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3455.shape_pair_relation_ordinal_columns.v1")
        self.assertEqual(payload["goal"], 3455)
        self.assertTrue(payload["ordinal_rows_match"])
        self.assertEqual(payload["observed_rows"], payload["expected_rows"])
        self.assertTrue(payload["metadata_ordinal_columns"]["device_resident"])
        self.assertEqual(
            payload["metadata_ordinal_columns"]["ordinal_semantics"],
            "zero_based_index_into_shape_pair_geometry_payload_arrays",
        )
        self.assertTrue(payload["metadata_ordinal_columns"]["sparse_user_ids_are_not_dense_geometry_indices"])
        self.assertTrue(payload["metadata_geometry_payload"]["device_resident"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
