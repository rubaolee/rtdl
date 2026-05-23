from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_IMPLEMENTATION_FILES = (
    ROOT / "src/native/embree/rtdl_embree_api.cpp",
    ROOT / "src/native/embree/rtdl_embree_scene.cpp",
    ROOT / "src/native/optix/rtdl_optix_api.cpp",
    ROOT / "src/native/optix/rtdl_optix_core.cpp",
    ROOT / "src/native/optix/rtdl_optix_workloads.cpp",
)
REPORT = ROOT / "docs/reports/goal2555_native_columnar_helper_boundary_2026-05-23.md"

OLD_HELPER_PATTERNS = (
    r"\bDb[A-Z][A-Za-z0-9_]*\b",
    r"\bEmbreeDb[A-Za-z0-9_]*\b",
    r"\bOptixDb[A-Za-z0-9_]*\b",
    r"\bg_db[A-Za-z0-9_]*\b",
    r"\bkDb[A-Za-z0-9_]*\b",
    r"\bdb_[a-z][A-Za-z0-9_]*\b",
    r"\bDB\b",
    r"\bRTDL_DB_[A-Z0-9_]+\b",
)

GENERIC_HELPER_TOKENS = (
    "ColumnarPrimaryAxis",
    "ColumnarRowBox",
    "ColumnarRowBoxSceneData",
    "ColumnarGroupedCountRayQueryState",
    "ColumnarGroupedSumRayQueryState",
    "columnar_validate_payload_fields",
    "columnar_copy_dataset_from_payload_fields",
    "kColumnarMaxRowsPerJob",
    "kColumnarGroupedCountRay",
    "g_columnar_limit_error",
    "RTDL_COLUMN_KIND_INT64",
    "RTDL_COLUMN_OP_BETWEEN",
)


def _active_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in ACTIVE_IMPLEMENTATION_FILES)


class Goal2555NativeColumnarHelperBoundaryTest(unittest.TestCase):
    def test_active_embree_optix_helper_names_are_columnar_not_db_shaped(self) -> None:
        text = _active_text()
        for pattern in OLD_HELPER_PATTERNS:
            with self.subTest(pattern=pattern):
                match = re.search(pattern, text)
                self.assertIsNone(match, f"unexpected legacy helper token: {match.group(0) if match else pattern}")

        for token in GENERIC_HELPER_TOKENS:
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_columnar_helper_names_avoid_double_columnar_artifacts(self) -> None:
        text = _active_text()
        for token in (
            "columnar_validate_columnar_inputs",
            "columnar_copy_dataset_columnar_payload",
            "columnar_columnar",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, text)

    def test_report_records_scope_and_no_behavior_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2555", text)
        self.assertIn("active Embree/OptiX implementation internals", text)
        self.assertIn("No exported C symbol is renamed", text)
        self.assertIn("No pod was used", text)


if __name__ == "__main__":
    unittest.main()
