import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal1572V154OptixCollectKCarryPointerDeviceCountsDiagnosticTest(unittest.TestCase):
    def test_device_count_pointer_diagnostic_is_env_gated(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC", source)
        self.assertIn("collect_k_use_carry_pointer_device_counts_diagnostic", source)
        self.assertIn("collect_k_use_carry_pointer_device_counts_diagnostic() && use_device_level_counts", source)

    def test_pointer_device_count_kernels_are_declared_and_loaded(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        for name in (
            "collect_k_bounded_i64_row_width2_final_materialize_level_counts_pointers",
            "collect_k_bounded_i64_row_width2_final_mark_counts_level_counts_pointers",
        ):
            self.assertIn(f"extern \"C\" __global__ void {name}", core)
            self.assertGreaterEqual(api.count(name), 2)
        self.assertIn("g_collect_k_i64_row_width2_final_materialize_level_counts_pointers", core)
        self.assertIn("g_collect_k_i64_row_width2_final_mark_counts_level_counts_pointers", core)

    def test_device_count_pointer_path_uses_device_counts_without_host_count_upload(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("use_pointer_device_counts_carry_level", source)
        self.assertIn("level_use_pointer_device_counts", source)
        self.assertIn("use_device_level_counts && !use_pointer_host_counts_carry_level", source)
        self.assertIn("const size_t descriptor_fields_uploaded = level_use_pointer_device_counts", source)
        self.assertIn("? 3", source)
        self.assertIn("if (use_pointer_host_counts_carry_level) {", source)
        self.assertIn("upload(next_counts_level_device, next_counts.data(), pair_count);", source)

    def test_launcher_routes_pointer_device_count_kernels_before_derived_path(self) -> None:
        source = API.read_text(encoding="utf-8")
        materialize_pointer = source.index("if (use_pointer_device_counts) {")
        materialize_derived = source.index("} else if (use_device_level_counts) {", materialize_pointer)
        self.assertLess(materialize_pointer, materialize_derived)
        self.assertIn("g_collect_k_i64_row_width2_final_materialize_level_counts_pointers.fn", source)
        self.assertIn("g_collect_k_i64_row_width2_final_mark_counts_level_counts_pointers.fn", source)


if __name__ == "__main__":
    unittest.main()
