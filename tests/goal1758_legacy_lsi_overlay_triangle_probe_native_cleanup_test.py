import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
NATIVE_ROOT = ROOT / "src" / "native"
PY_RUNTIME_ROOT = ROOT / "src" / "rtdsl"
REPORT = ROOT / "docs" / "reports" / "goal1758_legacy_lsi_overlay_triangle_probe_native_cleanup_2026-05-12.md"

OLD_NATIVE_SYMBOLS = (
    "rtdl_apple_rt_run_lsi",
    "rtdl_hiprt_run_lsi",
    "rtdl_hiprt_run_overlay",
    "rtdl_hiprt_run_triangle_probe",
    "rtdl_hiprt_run_prepared_triangle_probe",
    "rtdl_hiprt_lsi_2d",
    "rtdl_hiprt_overlay_2d",
    "rtdl_hiprt_triangle_probe",
    "rtdl_oracle_run_lsi",
    "rtdl_oracle_run_overlay",
    "rtdl_oracle_run_triangle_probe",
    "rtdl_vulkan_run_lsi",
    "rtdl_vulkan_run_overlay",
    "rtdl_vulkan_run_triangle_probe",
)

NEW_NATIVE_SYMBOLS = (
    "rtdl_apple_rt_run_segment_pair_intersection",
    "rtdl_hiprt_run_segment_pair_intersection",
    "rtdl_hiprt_run_shape_pair_relation_flags",
    "rtdl_hiprt_run_triangle_cycle_candidates",
    "rtdl_hiprt_run_prepared_triangle_cycle_candidates",
    "rtdl_hiprt_segment_pair_intersection_2d",
    "rtdl_hiprt_shape_pair_relation_flags_2d",
    "rtdl_hiprt_triangle_cycle_candidates",
    "rtdl_oracle_run_segment_pair_intersection",
    "rtdl_oracle_run_shape_pair_relation_flags",
    "rtdl_oracle_run_triangle_cycle_candidates",
    "rtdl_vulkan_run_segment_pair_intersection",
    "rtdl_vulkan_run_shape_pair_relation_flags",
    "rtdl_vulkan_run_triangle_cycle_candidates",
)


def _read_tree(root: pathlib.Path, suffixes: tuple[str, ...]) -> str:
    parts: list[str] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in suffixes:
            parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


class Goal1758LegacyNativeCleanupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.native_text = _read_tree(NATIVE_ROOT, (".cpp", ".h", ".hpp", ".cu", ".cuh", ".mm"))
        cls.runtime_text = _read_tree(PY_RUNTIME_ROOT, (".py",))

    def test_old_native_abi_names_are_absent_from_native_and_runtime_sources(self) -> None:
        combined = self.native_text + "\n" + self.runtime_text
        for symbol in OLD_NATIVE_SYMBOLS:
            self.assertNotIn(symbol, combined, symbol)

    def test_generic_replacement_symbols_are_present(self) -> None:
        combined = self.native_text + "\n" + self.runtime_text
        for symbol in NEW_NATIVE_SYMBOLS:
            self.assertIn(symbol, combined, symbol)

    def test_old_internal_native_vocabulary_is_absent(self) -> None:
        self.assertIsNone(
            re.search(r"(?:\blsi\b|\boverlay\b|triangle_probe|\bLsi\b|\bOverlay\b|\bLSI\b)", self.native_text),
            "native source still contains old LSI/overlay/triangle_probe vocabulary",
        )

    def test_report_records_boundary_and_linux_build_evidence(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("legacy_app_shaped_native_support_migrated_to_generic_terms", text)
        self.assertIn("make build-embree", text)
        self.assertIn("pod/hardware evidence for every backend", text)


if __name__ == "__main__":
    unittest.main()
