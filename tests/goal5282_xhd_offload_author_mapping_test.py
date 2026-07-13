from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "xhd_memory_accounting.py"
)
SCRIPT_PATH = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_offload_mapping.py"
)
GOAL5281_ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json"
)
GOAL5282_ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5282_author_offload_mapping_2026-07-09.json"
)


def _load_memory_module():
    spec = importlib.util.spec_from_file_location("xhd_memory_accounting", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5282XhdOffloadAuthorMappingTest(unittest.TestCase):
    def test_helper_maps_v2_telemetry_to_author_shaped_fields(self) -> None:
        module = _load_memory_module()
        native = json.loads(GOAL5281_ARTIFACT.read_text(encoding="utf-8"))
        mapping = module.author_offload_mapping_from_native_telemetry(
            native["native_memory_telemetry"]
        )

        self.assertEqual(
            mapping["status"],
            "bounded_author_offload_shape_mapped__figure11_byte_denominator_not_aligned",
        )
        self.assertEqual(mapping["author_shaped_fields"]["OffloadingSize"]["value"], 6)
        self.assertEqual(mapping["author_shaped_fields"]["WL Heavy Peak"]["bytes"], 48)
        self.assertEqual(
            mapping["rtdl_measured_fields"]["generic_heavy_offload_queue_peak"]["bytes"],
            96,
        )
        self.assertTrue(
            mapping["denominator_alignment"]["offloading_size_row_count_shape_available"]
        )
        self.assertFalse(
            mapping["denominator_alignment"]["same_byte_denominator_author_figure11"]
        )
        self.assertFalse(
            mapping["denominator_alignment"]["same_denominator_author_figure11"]
        )

    def test_artifact_keeps_shape_mapping_separate_from_figure11_reproduction(self) -> None:
        artifact = json.loads(GOAL5282_ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(artifact["matched"])
        self.assertEqual(
            artifact["status"],
            "xhd_bounded_offload_mapping_ready__figure11_same_denominator_not_met",
        )
        self.assertTrue(artifact["decision"]["xhd_offloading_size_shape_mapped"])
        self.assertTrue(artifact["decision"]["wl_heavy_peak_author_width_candidate_available"])
        self.assertFalse(artifact["decision"]["same_denominator_author_figure11"])
        self.assertFalse(artifact["decision"]["figure11_reproduced"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)

    def test_builder_and_mapping_are_app_owned_not_core_primitives(self) -> None:
        text = SCRIPT_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("xhd_memory_accounting", text)
        self.assertNotIn("src/rtdsl", text)
        self.assertNotIn("src/native", text)


if __name__ == "__main__":
    unittest.main()
