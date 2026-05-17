from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2212_optix_pip_compact_positive_hits_2026-05-17.md"


class Goal2212OptixPipCompactPositiveHitsTest(unittest.TestCase):
    def test_device_anyhit_writes_compact_positive_candidate_records(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        self.assertIn("point_index_offset", text)
        self.assertIn("const uint32_t slot = atomicAdd(params.output_count, 1u);", text)
        self.assertIn("params.output[slot] = r;", text)
        self.assertNotIn("atomicOr(&params.hit_words[word], bit)", text)

    def test_host_positive_path_avoids_full_bitmap_scan(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        pip_block = text.split("static void run_pip_optix", 1)[1].split(
            "static void validate_polygon_ref_span_for_collection", 1
        )[0]
        self.assertIn("launch_positive_candidate_pass", pip_block)
        self.assertIn("gpu_rows.resize(old_size + gpu_count)", pip_block)
        self.assertIn("PIP positive-hit candidate count changed between count and write passes", pip_block)
        self.assertNotIn("hit_words[word] & bit", pip_block)

    def test_report_records_boundary_and_required_pod_validation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2212", text)
        self.assertIn("compact positive-hit candidate output", text)
        self.assertIn("app-agnostic", text)
        self.assertIn("does not authorize a speedup claim yet", text)
        self.assertIn("pod rerun", text)


if __name__ == "__main__":
    unittest.main()
