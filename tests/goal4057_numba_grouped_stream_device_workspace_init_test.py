from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs" / "reports" / "goal4057_numba_grouped_stream_device_workspace_init_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4057_numba_grouped_stream_device_workspace_init_pod_probe.json"


def _numba_grouped_stream_class_source() -> str:
    source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
    start = source.index("class PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D")
    end = source.index("def prepare_optix_cupy_radius_graph_components_3d", start)
    return source[start:end]


class Goal4057NumbaGroupedStreamDeviceWorkspaceInitTest(unittest.TestCase):
    def test_numba_grouped_stream_uses_device_workspace_init_kernel(self) -> None:
        source = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        class_source = _numba_grouped_stream_class_source()

        self.assertIn("_NUMBA_I32_PARENT_BORDER_INIT_KERNEL", source)
        self.assertIn("def _numba_i32_parent_border_init_kernel", source)
        self.assertIn("parent[point] = point", source)
        self.assertIn("border[point] = border_value", source)
        self.assertIn("self.parent_border_init_kernel", class_source)
        self.assertIn("numba_workspace_init_policy", class_source)
        self.assertIn("numba_workspace_host_reset_copy_used", class_source)
        self.assertNotIn("copy_to_device(self.parent_initial_host)", class_source)
        self.assertNotIn("copy_to_device(self.border_initial_host)", class_source)
        self.assertNotIn("parent_initial_host = np.arange", class_source)
        self.assertNotIn("border_initial_host = np.full", class_source)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal4057",
            "generic Numba CUDA init kernel",
            "copy_to_device(parent_initial_host)",
            "numba_workspace_host_reset_copy_used: false",
            "does not add DBSCAN-native ABI",
            "does not authorize speedup",
        ):
            self.assertIn(phrase, text)

    def test_pod_probe_records_device_init_metadata_and_boundary(self) -> None:
        import json

        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["commit"], "a60509b8")
        self.assertTrue(artifact["all_rows_avoid_host_workspace_reset_copy"])
        self.assertTrue(artifact["mixed_label_rows_observed"])
        self.assertGreaterEqual(len(artifact["rows"]), 3)
        for row in artifact["rows"]:
            self.assertFalse(row["numba_workspace_host_reset_copy_used"])
            self.assertEqual(row["numba_workspace_init_policy"], "device_parent_iota_optional_border_fill")
            self.assertGreater(row["vs_goal4056_speedup"], 1.0)
        for flag, value in artifact["claim_boundary"].items():
            self.assertFalse(value, flag)


if __name__ == "__main__":
    unittest.main()
