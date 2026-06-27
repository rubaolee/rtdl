import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))
from scripts.goal4373_rayjoin_cdb_point_location_compare import _filter_backend_parity_points, _write_markdown


class _Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class _Chain:
    points = (_Point(0.0, 0.0), _Point(1.0, 1.0))


class _Dataset:
    chains = (_Chain(),)


class _Prepared:
    def __init__(self, *, mismatch_point_id: int | None):
        self.mismatch_point_id = mismatch_point_id

    def run(self, points):
        rows = []
        for point in points:
            point_id = int(point["id"])
            segment_id = 10
            face_id = 20
            if self.mismatch_point_id == point_id:
                segment_id = 11
                face_id = 21
            rows.append({"point_id": point_id, "segment_id": segment_id, "face_id": face_id, "hit_t": 1.0})
        return rows


class V3RayJoinPipMissingAuthorTest(unittest.TestCase):
    def test_markdown_writer_handles_missing_author_query_exec(self):
        payload = {
            "input_shape": {
                "base_chains": 1,
                "base_cdb_segments": 2,
                "query_points": 100000,
            },
            "protocol": {
                "contract": "vertical-ray closest CDB boundary segment",
                "timed_output": "scalar positive-face count for RTDL",
                "row_materialization_in_timed_path": False,
                "rayjoin_repeats": 1000,
            },
            "correctness_sample": {
                "sample_count": 100000,
                "mismatch_count_first_10_materialized": 0,
            },
            "rayjoin_rt": None,
            "rtdl": {
                "optix": {
                    "hot_median_sec": 0.001,
                    "native_traversal_median_sec": 0.0001,
                    "repeats": 1000,
                    "hot_total_sec": 1.0,
                    "positive_face_count": 42,
                },
                "embree": {
                    "hot_median_sec": 0.01,
                    "native_traversal_median_sec": 0.001,
                    "repeats": 1000,
                    "hot_total_sec": 10.0,
                    "positive_face_count": 42,
                },
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.md"
            _write_markdown(path, payload)
            text = path.read_text(encoding="utf-8")
        self.assertIn("author-code comparison remains blocked", text)
        self.assertNotIn("Nonex", text)

    def test_backend_parity_filter_rejects_exact_row_mismatch(self):
        initial_points = [
            {"id": 1, "x": 0.1, "y": 0.1},
            {"id": 2, "x": 0.2, "y": 0.2},
            {"id": 3, "x": 0.3, "y": 0.3},
        ]
        report = _filter_backend_parity_points(
            _Prepared(mismatch_point_id=None),
            _Prepared(mismatch_point_id=2),
            base_dataset=_Dataset(),
            initial_points=initial_points,
            target_count=2,
            seed=4373,
            oversample=1,
            max_rounds=1,
        )
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["accepted_count"], 2)
        self.assertEqual(report["rejected_count"], 1)
        self.assertEqual([point["id"] for point in report["points"]], [1, 2])
        self.assertEqual(len(report["first_rejected"]), 1)


if __name__ == "__main__":
    unittest.main()
