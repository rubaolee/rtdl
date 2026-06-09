from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4066_partition_pair_count_then_emit_preview_2026-06-09.md"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4066PartitionPairCountThenEmitRuntimeTest(unittest.TestCase):
    def test_count_then_emit_matches_bounded_offsets_with_exact_capacity(self) -> None:
        points = (
            (0.0, 0.0, 0.0),
            (0.2, 0.0, 0.0),
            (1.2, 0.0, 0.0),
            (1.5, 0.0, 0.0),
            (4.0, 0.0, 0.0),
        )
        bounded = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            pair_enumeration="device_bounded_offsets",
        )
        counted = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            pair_enumeration="device_count_then_emit",
        )
        validation = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            candidate=counted,
        )

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(counted["metadata"]["pair_enumeration"], "device_count_then_emit")
        self.assertEqual(counted["metadata"]["pair_capacity_source"], "device_exact_count")
        self.assertTrue(counted["metadata"]["device_pair_enumeration_used"])
        self.assertTrue(counted["metadata"]["device_pair_count_probe_used"])
        self.assertFalse(counted["metadata"]["host_pair_enumeration_used"])
        self.assertFalse(counted["metadata"]["overflow"])
        self.assertEqual(counted["metadata"]["pair_capacity"], max(1, counted["metadata"]["pair_count"]))
        self.assertLess(counted["metadata"]["pair_capacity"], bounded["metadata"]["pair_capacity"])
        self.assertEqual(counted["metadata"]["status_counts"], bounded["metadata"]["status_counts"])
        self.assertFalse(counted["metadata"]["release_authorized"])
        self.assertFalse(counted["metadata"]["public_speedup_claim_authorized"])


class Goal4066PartitionPairCountThenEmitSourceTest(unittest.TestCase):
    def test_source_and_report_describe_opt_in_memory_fix(self) -> None:
        text = SOURCE.read_text(encoding="utf-8") + "\n" + REPORT.read_text(encoding="utf-8")
        for fragment in (
            "device_count_then_emit",
            "_cupy_partition_pair_status_device_count_then_emit",
            "device_exact_count",
            "device_pair_count_probe_used",
            "opt-in",
            "does not promote",
            "does not add a native ABI",
            "does not authorize public speedup",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
