import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal3952_grouped_and_segment_pair_direct_cuda_cubin_loader_hardening_2026-06-08"
)


class Goal3952GroupedAndSegmentPairDirectCudaCubinLoaderHardeningTest(unittest.TestCase):
    def test_grouped_and_segment_pair_direct_cuda_loaders_use_cubin(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        for source_name, file_name in (
            ("kDeviceColumnGroupedI64KernelSrc", "device_column_grouped_i64_kernel.cu"),
            ("kSegmentPairAmbiguityCountKernelSrc", "segment_pair_ambiguity_count_kernel.cu"),
            ("kSegmentPairDeviceRefinedCountKernelSrc", "segment_pair_device_refined_count_kernel.cu"),
        ):
            pattern = (
                rf"compile_to_cubin\(\s*{source_name},\s*\"{re.escape(file_name)}\"\s*\)"
                r"[\s\S]{0,260}?cuModuleLoadData\(&[^,]+,\s*cubin\.data\(\)\)"
            )
            self.assertRegex(text, pattern)
            self.assertNotIn(
                f'compile_to_ptx({source_name}, "{file_name}")',
                text,
            )

    def test_raydb_and_rayjoin_smoke_rows_pass(self) -> None:
        summary = json.loads(
            (ARTIFACT_DIR / "goal3952_raydb_rayjoin_smoke.json").read_text(encoding="utf-8")
        )
        self.assertTrue(summary["all_pass"])
        self.assertEqual(2, summary["json_pass_count"])
        rows = {row["row_id"]: row for row in summary["rows"]}
        self.assertEqual(
            {
                "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default",
                "raydb_style_optix_count_scale_default_262k",
            },
            set(rows),
        )
        for row in rows.values():
            self.assertEqual("pass", row["status"])
            self.assertEqual([], row["semantic_stdout_check"]["claim_flag_violations"])
            self.assertTrue(row["semantic_stdout_check"]["stdout_json_parseable"])


if __name__ == "__main__":
    unittest.main()
