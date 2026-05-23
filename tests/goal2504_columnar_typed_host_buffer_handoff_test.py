import json
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.embree_runtime import _columnar_record_set_to_column_mapping
from rtdsl.embree_runtime import _encode_all_db_text_column_mapping
from rtdsl.embree_runtime import _encode_db_column_mapping_columnar_with_metadata
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2504_columnar_typed_host_buffer_handoff_2026-05-22.md"
POD_ARTIFACT = ROOT / "docs/reports/goal2504_optix_numpy_typed_host_buffer_pod_2026-05-22.json"


def _numpy():
    try:
        import numpy as np
    except Exception as exc:
        raise unittest.SkipTest(f"NumPy unavailable: {exc}") from exc
    return np


def _numpy_fixture():
    np = _numpy()
    fixture = app.make_fixture()
    return {
        "row_ids": np.asarray(fixture["row_ids"], dtype=np.int64),
        "columns": {
            name: np.asarray(values, dtype=np.int64)
            for name, values in fixture["columns"].items()
        },
    }


def _require_optix() -> None:
    try:
        rt.optix_version()
    except Exception as exc:
        raise unittest.SkipTest(f"OptiX backend unavailable: {exc}") from exc


class Goal2504ColumnarTypedHostBufferHandoffTest(unittest.TestCase):
    def test_direct_mapping_preserves_numpy_columns_before_backend_encoding(self) -> None:
        np = _numpy()
        row_ids = np.asarray([1, 2, 3], dtype=np.int64)
        region_id = np.asarray([0, 1, 0], dtype=np.int64)
        revenue = np.asarray([10.0, 20.0, 30.0], dtype=np.float64)
        mapping = _columnar_record_set_to_column_mapping(
            {
                "row_ids": row_ids,
                "columns": {
                    "region_id": region_id,
                    "revenue": revenue,
                },
            }
        )
        self.assertIs(mapping["row_id"], row_ids)
        self.assertIs(mapping["region_id"], region_id)
        self.assertIs(mapping["revenue"], revenue)

    def test_encoder_uses_numpy_typed_host_buffers_when_layout_matches(self) -> None:
        np = _numpy()
        columns, field_maps, reverse_maps = _encode_all_db_text_column_mapping(
            {
                "row_id": np.asarray([1, 2, 3], dtype=np.int64),
                "region_id": np.asarray([0, 1, 0], dtype=np.int64),
                "revenue": np.asarray([10.0, 20.0, 30.0], dtype=np.float64),
            }
        )
        _columns_array, row_count, _keepalive, metadata = _encode_db_column_mapping_columnar_with_metadata(
            columns,
            error_prefix="test direct columnar path",
        )
        self.assertEqual(row_count, 3)
        self.assertEqual(field_maps, {})
        self.assertEqual(reverse_maps, {})
        self.assertEqual(
            metadata["typed_host_buffer_columns"],
            ["row_id", "region_id", "revenue"],
        )
        self.assertEqual(metadata["copied_columns"], [])
        self.assertTrue(metadata["all_numeric_columns_use_typed_host_buffers"])
        self.assertFalse(metadata["true_zero_copy_authorized"])

    def test_non_matching_numpy_dtype_falls_back_to_copy(self) -> None:
        np = _numpy()
        columns, _field_maps, _reverse_maps = _encode_all_db_text_column_mapping(
            {
                "row_id": np.asarray([1, 2, 3], dtype=np.uint32),
                "region_id": np.asarray([0, 1, 0], dtype=np.int64),
            }
        )
        _columns_array, _row_count, _keepalive, metadata = _encode_db_column_mapping_columnar_with_metadata(
            columns,
            error_prefix="test direct columnar path",
        )
        self.assertIn("region_id", metadata["typed_host_buffer_columns"])
        self.assertIn("row_id", metadata["copied_columns"])
        self.assertFalse(metadata["all_numeric_columns_use_typed_host_buffers"])

    def test_optix_numpy_typed_buffers_match_cpu_when_available(self) -> None:
        _require_optix()
        query = rt.columnar_plan_to_grouped_query(app.make_plan("sum"))
        dataset = rt.prepare_optix_columnar_record_set(
            _numpy_fixture(),
            primary_fields=("ship_year", "discount", "quantity"),
        )
        try:
            self.assertEqual(dataset.grouped_sum(query), tuple(app.run_result_mode("sum")["rows"]))
            metadata = dataset.columnar_preparation_metadata()
            self.assertTrue(metadata["all_numeric_columns_use_typed_host_buffers"])
            self.assertIn("revenue", metadata["typed_host_buffer_columns"])
        finally:
            dataset.close()

    def test_report_records_handoff_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("typed host-buffer handoff", text)
        self.assertIn("numpy.int64", text)
        self.assertIn("numpy.float64", text)
        self.assertIn("does not authorize true zero-copy", text)
        self.assertIn("6 tests OK", text)

    def test_pod_artifact_records_optix_numpy_typed_host_buffer_handoff(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        metadata = payload["columnar_preparation_metadata"]
        self.assertTrue(payload["all_match_cpu_reference"])
        self.assertTrue(metadata["all_numeric_columns_use_typed_host_buffers"])
        self.assertEqual(metadata["copied_columns"], [])
        self.assertIn("row_id", metadata["typed_host_buffer_columns"])
        self.assertIn("revenue", metadata["typed_host_buffer_columns"])
        self.assertFalse(metadata["true_zero_copy_authorized"])


if __name__ == "__main__":
    unittest.main()
