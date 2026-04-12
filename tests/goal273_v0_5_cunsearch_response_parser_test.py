import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal273V05CuNSearchResponseParserTest(unittest.TestCase):
    def test_response_parser_loads_and_sorts_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            response = Path(tmpdir) / "response.json"
            response.write_text(
                json.dumps(
                    {
                        "adapter": "cunsearch",
                        "response_format": "json_rows_v1",
                        "workload": "fixed_radius_neighbors",
                        "rows": [
                            {"query_id": 2, "neighbor_id": 8, "distance": 0.5},
                            {"query_id": 1, "neighbor_id": 4, "distance": 0.6},
                            {"query_id": 1, "neighbor_id": 3, "distance": 0.4},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = rt.load_cunsearch_fixed_radius_response(response)
            self.assertEqual(result.row_count, 3)
            self.assertEqual(
                result.rows,
                (
                    {"query_id": 1, "neighbor_id": 3, "distance": 0.4},
                    {"query_id": 1, "neighbor_id": 4, "distance": 0.6},
                    {"query_id": 2, "neighbor_id": 8, "distance": 0.5},
                ),
            )

    def test_parser_rejects_wrong_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            response = Path(tmpdir) / "response.json"
            response.write_text(
                json.dumps(
                    {
                        "adapter": "other",
                        "response_format": "json_rows_v1",
                        "workload": "fixed_radius_neighbors",
                        "rows": [],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unsupported cuNSearch response adapter"):
                rt.load_cunsearch_fixed_radius_response(response)

    def test_parser_rejects_wrong_format_or_workload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            response = Path(tmpdir) / "response.json"
            response.write_text(
                json.dumps(
                    {
                        "adapter": "cunsearch",
                        "response_format": "bad_format",
                        "workload": "fixed_radius_neighbors",
                        "rows": [],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unsupported cuNSearch response format"):
                rt.load_cunsearch_fixed_radius_response(response)

            response.write_text(
                json.dumps(
                    {
                        "adapter": "cunsearch",
                        "response_format": "json_rows_v1",
                        "workload": "bounded_knn_rows",
                        "rows": [],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unsupported cuNSearch response workload"):
                rt.load_cunsearch_fixed_radius_response(response)


if __name__ == "__main__":
    unittest.main()
