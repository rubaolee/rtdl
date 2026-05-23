from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_IMPLEMENTATION_FILES = (
    ROOT / "src/native/embree/rtdl_embree_api.cpp",
    ROOT / "src/native/embree/rtdl_embree_scene.cpp",
    ROOT / "src/native/optix/rtdl_optix_api.cpp",
    ROOT / "src/native/optix/rtdl_optix_core.cpp",
    ROOT / "src/native/optix/rtdl_optix_workloads.cpp",
)
PRELUDE_FILES = (
    ROOT / "src/native/embree/rtdl_embree_prelude.h",
    ROOT / "src/native/optix/rtdl_optix_prelude.h",
)
RUNTIME_FILES = (
    ROOT / "src/rtdsl/embree_runtime.py",
    ROOT / "src/rtdsl/optix_runtime.py",
)

OLD_NATIVE_TYPE_TOKENS = (
    "RtdlDbField",
    "RtdlDbScalar",
    "RtdlDbClause",
    "RtdlDbRowIdRow",
    "RtdlDbGroupedCountRow",
    "RtdlDbGroupedSumRow",
    "RtdlDbGroupedSumCountRow",
    "RtdlDbGroupedStatsRow",
    "RtdlDbCompactSummaryRequest",
    "RtdlDbCompactSummaryResult",
    "RtdlEmbreeDbDataset",
    "RtdlOptixDbDataset",
    "kRtdlDbKind",
    "kRtdlDbCompactSummary",
)

GENERIC_NATIVE_TYPE_TOKENS = (
    "RtdlColumnField",
    "RtdlColumnScalar",
    "RtdlColumnClause",
    "RtdlColumnRowIdRow",
    "RtdlGroupedCountRow",
    "RtdlGroupedSumRow",
    "RtdlGroupedSumCountRow",
    "RtdlGroupedStatsRow",
    "RtdlColumnCompactSummaryRequest",
    "RtdlColumnCompactSummaryResult",
    "RtdlEmbreeColumnarPayload",
    "RtdlOptixColumnarPayload",
    "kRtdlColumnKind",
    "kRtdlColumnCompactSummary",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


class Goal2554NativeColumnarTypeBoundaryTest(unittest.TestCase):
    def test_active_native_implementation_uses_generic_columnar_type_names(self) -> None:
        text = "\n".join(_text(path) for path in ACTIVE_IMPLEMENTATION_FILES)
        for token in OLD_NATIVE_TYPE_TOKENS:
            with self.subTest(token=token):
                self.assertNotIn(token, text)
        for token in GENERIC_NATIVE_TYPE_TOKENS:
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_preludes_keep_old_type_names_as_compatibility_aliases_only(self) -> None:
        text = "\n".join(_text(path) for path in PRELUDE_FILES)
        for token in GENERIC_NATIVE_TYPE_TOKENS:
            with self.subTest(token=token):
                self.assertIn(token, text)
        for token in OLD_NATIVE_TYPE_TOKENS:
            with self.subTest(token=token):
                self.assertIn(token, text)

        for alias in (
            "using RtdlDbField = RtdlColumnField;",
            "using RtdlDbScalar = RtdlColumnScalar;",
            "using RtdlDbClause = RtdlColumnClause;",
            "using RtdlDbRowIdRow = RtdlColumnRowIdRow;",
            "using RtdlDbGroupedCountRow = RtdlGroupedCountRow;",
            "using RtdlDbGroupedSumRow = RtdlGroupedSumRow;",
            "using RtdlEmbreeDbDataset = RtdlEmbreeColumnarPayload;",
            "using RtdlOptixDbDataset = RtdlOptixColumnarPayload;",
        ):
            with self.subTest(alias=alias):
                self.assertIn(alias, text)

    def test_python_ctypes_compatibility_names_remain_python_side(self) -> None:
        text = "\n".join(_text(path) for path in RUNTIME_FILES)
        for token in (
            "_RtdlDbField",
            "_RtdlDbRowIdRow",
            "_RtdlDbGroupedCountRow",
            "_RtdlDbGroupedSumRow",
            "_RtdlDbGroupedSumCountRow",
            "_RtdlDbGroupedStatsRow",
            "_RtdlDbCompactSummaryRequest",
            "_RtdlDbCompactSummaryResult",
        ):
            with self.subTest(token=token):
                self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
