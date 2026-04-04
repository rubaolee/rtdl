from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "goal65_vulkan_optix_linux_comparison.py"
SPEC = importlib.util.spec_from_file_location("goal65_vulkan_optix_linux_comparison", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Goal65VulkanOptixLinuxComparisonTest(unittest.TestCase):
    def test_canonical_rows_lsi(self) -> None:
        rows = (
            {"left_id": 2, "right_id": 10},
            {"left_id": 1, "right_id": 11},
        )
        self.assertEqual(MODULE.canonical_rows("lsi", rows), [(1, 11), (2, 10)])

    def test_canonical_rows_pip(self) -> None:
        rows = (
            {"point_id": 2, "polygon_id": 10, "contains": 0},
            {"point_id": 1, "polygon_id": 11, "contains": 1},
        )
        self.assertEqual(MODULE.canonical_rows("pip", rows), [(1, 11, 1), (2, 10, 0)])

    def test_canonical_rows_overlay(self) -> None:
        rows = (
            {"left_polygon_id": 2, "right_polygon_id": 10, "requires_lsi": 1, "requires_pip": 0},
            {"left_polygon_id": 1, "right_polygon_id": 11, "requires_lsi": 0, "requires_pip": 1},
        )
        self.assertEqual(MODULE.canonical_rows("overlay", rows), [(1, 11, 0, 1), (2, 10, 1, 0)])

    def test_backend_payload_parity_true_when_hash_matches(self) -> None:
        rows = (
            {"left_id": 1, "right_id": 2},
            {"left_id": 3, "right_id": 4},
        )
        canonical = MODULE.canonical_rows("lsi", rows)
        hashed = MODULE.hash_rows(canonical)
        payload = MODULE.backend_payload(
            workload="lsi",
            rows=rows,
            reference_hash=hashed["sha256"],
            reference_row_count=hashed["row_count"],
            run_sec=0.5,
            prepare_sec=0.25,
        )
        self.assertTrue(payload["parity_vs_cpu"])
        self.assertEqual(payload["total_sec"], 0.75)

    def test_render_markdown_mentions_warm_comparison_and_boundary(self) -> None:
        summary = {
            "host_label": "192.168.1.20",
            "bbox": "-26.72,152.95,-26.55,153.10",
            "optix_version": (9, 0, 0),
            "vulkan_version": (0, 1, 0),
            "county_zipcode": {
                "metadata": {"county_feature_count": 1},
                "slices": [
                    {
                        "slice_label": "1x4",
                        "selection": {"estimated_total_segments": 123, "zipcode_face_ids": [1, 2, 3, 4]},
                        "workloads": {
                            "lsi": {
                                "cpu": {"row_count": 1, "run_sec": 1.0},
                                "embree": {"row_count": 1, "run_sec": 0.9, "parity_vs_cpu": True},
                                "optix": {"row_count": 1, "run_sec": 0.5, "prepare_sec": 0.2, "cold_run_sec": 0.9, "total_sec": 0.7, "parity_vs_cpu": True},
                                "vulkan": {"row_count": 1, "run_sec": 0.75, "prepare_sec": 0.3, "cold_run_sec": 1.1, "total_sec": 1.05, "parity_vs_cpu": True},
                            }
                        },
                    }
                ],
            },
            "blockgroup_waterbodies": {
                "metadata": {"comparison_surface": ["county2300_s04", "county2300_s05"]},
                "slices": [
                    {
                        "slice_label": "county2300_s04",
                        "metadata": {"blockgroup_feature_count": 1},
                        "workloads": {
                            "pip": {
                                "cpu": {"row_count": 1, "run_sec": 1.0},
                                "embree": {"row_count": 1, "run_sec": 0.9, "parity_vs_cpu": True},
                                "optix": {"row_count": 1, "run_sec": 0.5, "prepare_sec": 0.2, "cold_run_sec": 0.9, "total_sec": 0.7, "parity_vs_cpu": True},
                                "vulkan": {"row_count": 1, "run_sec": 0.75, "prepare_sec": 0.3, "cold_run_sec": 1.1, "total_sec": 1.05, "parity_vs_cpu": True},
                            }
                        },
                    }
                ],
            },
            "lkau_pkau_overlay": {
                "bbox_label": "sunshine_tiny",
                "metadata": {"lakes_feature_count": 1},
                "workloads": {
                    "overlay": {
                        "cpu": {"row_count": 1, "run_sec": 1.0},
                        "embree": {"row_count": 1, "run_sec": 0.9, "parity_vs_cpu": True},
                        "optix": {"row_count": 1, "run_sec": 0.5, "prepare_sec": 0.2, "cold_run_sec": 0.9, "total_sec": 0.7, "parity_vs_cpu": True},
                        "vulkan": {"row_count": 1, "run_sec": 0.75, "prepare_sec": 0.3, "cold_run_sec": 1.1, "total_sec": 1.05, "parity_vs_cpu": True},
                    }
                },
            },
        }
        text = MODULE.render_markdown(summary)
        self.assertIn("warm Vulkan vs warm OptiX", text)
        self.assertIn("not a new PostGIS closure round", text)
        self.assertIn("LKAU/PKAU overlay-seed", text)
        self.assertIn("whole `top4` package", text)
        self.assertIn("county2300_s06", text)
        self.assertIn("cold", text)


if __name__ == "__main__":
    unittest.main()
