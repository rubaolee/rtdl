import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_polygon_pair_overlap_area_rows import make_authored_polygon_pair_overlap_case
from examples.rtdl_polygon_pair_overlap_area_rows import polygon_pair_overlap_area_rows_reference
from examples.rtdl_polygon_set_jaccard import make_authored_polygon_set_jaccard_case
from examples.rtdl_polygon_set_jaccard import polygon_set_jaccard_reference


ROOT = Path(__file__).resolve().parents[1]


class Goal146JaccardBackendSurfaceTest(unittest.TestCase):
    def test_raw_mode_is_rejected_for_wrapper_fallback_backends(self) -> None:
        with self.assertRaisesRegex(ValueError, "Jaccard workloads"):
            rt.run_embree(polygon_set_jaccard_reference, result_mode="raw", **make_authored_polygon_set_jaccard_case())
        with self.assertRaisesRegex(ValueError, "Jaccard workloads"):
            rt.run_optix(polygon_set_jaccard_reference, result_mode="raw", **make_authored_polygon_set_jaccard_case())
        with self.assertRaisesRegex(ValueError, "Jaccard workloads"):
            rt.run_vulkan(polygon_set_jaccard_reference, result_mode="raw", **make_authored_polygon_set_jaccard_case())
        with self.assertRaisesRegex(ValueError, "Jaccard workloads"):
            rt.run_embree(
                polygon_pair_overlap_area_rows_reference,
                result_mode="raw",
                **make_authored_polygon_pair_overlap_case(),
            )
        with self.assertRaisesRegex(ValueError, "Jaccard workloads"):
            rt.run_optix(
                polygon_pair_overlap_area_rows_reference,
                result_mode="raw",
                **make_authored_polygon_pair_overlap_case(),
            )
        with self.assertRaisesRegex(ValueError, "Jaccard workloads"):
            rt.run_vulkan(
                polygon_pair_overlap_area_rows_reference,
                result_mode="raw",
                **make_authored_polygon_pair_overlap_case(),
            )

    def test_polygon_set_jaccard_matches_cpu_when_oracle_available(self) -> None:
        try:
            rt.oracle_version()
        except Exception as exc:  # pragma: no cover - platform-specific oracle availability
            self.skipTest(f"native oracle unavailable: {exc}")
        expected = rt.run_cpu(polygon_set_jaccard_reference, **make_authored_polygon_set_jaccard_case())
        self.assertEqual(rt.run_embree(polygon_set_jaccard_reference, **make_authored_polygon_set_jaccard_case()), expected)
        self.assertEqual(rt.run_optix(polygon_set_jaccard_reference, **make_authored_polygon_set_jaccard_case()), expected)
        self.assertEqual(rt.run_vulkan(polygon_set_jaccard_reference, **make_authored_polygon_set_jaccard_case()), expected)

    def test_polygon_pair_overlap_rows_match_cpu_when_oracle_available(self) -> None:
        try:
            rt.oracle_version()
        except Exception as exc:  # pragma: no cover - platform-specific oracle availability
            self.skipTest(f"native oracle unavailable: {exc}")
        expected = rt.run_cpu(
            polygon_pair_overlap_area_rows_reference,
            **make_authored_polygon_pair_overlap_case(),
        )
        self.assertEqual(
            rt.run_embree(polygon_pair_overlap_area_rows_reference, **make_authored_polygon_pair_overlap_case()),
            expected,
        )
        self.assertEqual(
            rt.run_optix(polygon_pair_overlap_area_rows_reference, **make_authored_polygon_pair_overlap_case()),
            expected,
        )
        self.assertEqual(
            rt.run_vulkan(polygon_pair_overlap_area_rows_reference, **make_authored_polygon_pair_overlap_case()),
            expected,
        )

    def test_artifact_writer(self) -> None:
        payload = {
            "suite": "goal146_jaccard_linux_stress",
            "generated_at": "2026-04-07T12:00:00",
            "host": {"platform": "linux-test"},
            "boundary": {
                "accepted_claim": "wrapper fallback",
                "timing_interpretation": "measurement noise note",
                "not_claimed": "native backend maturity",
            },
            "dataset": {
                "source": "MoNuSeg 2018 Training Data",
                "xml_name": "sample.xml",
                "selected_polygon_count": 16,
                "base_left_polygon_count": 8556,
                "base_right_polygon_count": 8556,
            },
            "rows": [
                {
                    "copies": 64,
                    "left_polygon_count": 547584,
                    "right_polygon_count": 547584,
                    "backend_seconds": {
                        "cpu_python_reference": 7.5,
                        "cpu": 3.0,
                        "embree": 3.1,
                        "optix": 3.2,
                        "vulkan": 3.1,
                    },
                    "consistency_vs_python": {
                        "cpu": True,
                        "embree": True,
                        "optix": True,
                        "vulkan": True,
                    },
                    "result_rows": (
                        {
                            "intersection_area": 8190,
                            "left_area": 8556,
                            "right_area": 8556,
                            "union_area": 8922,
                            "jaccard_similarity": 0.917956,
                        },
                    ),
                }
            ],
        }
        (ROOT / "build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            artifacts = rt.write_goal146_artifacts(payload, tmpdir)
            self.assertTrue(artifacts["json"].exists())
            self.assertTrue(artifacts["markdown"].exists())
            self.assertAlmostEqual(
                json.loads(artifacts["json"].read_text(encoding="utf-8"))["rows"][0]["result_rows"][0]["jaccard_similarity"],
                0.917956,
            )
            self.assertIn("Goal 146 Jaccard Linux Stress", artifacts["markdown"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
