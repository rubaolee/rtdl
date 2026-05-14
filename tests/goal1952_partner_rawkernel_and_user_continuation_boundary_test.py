from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1952_partner_rawkernel_and_user_continuation_boundary_2026-05-13.md"
BOUNDARY_DOC = ROOT / "docs" / "partner_acceleration_boundaries.md"


class Goal1952PartnerRawKernelAndUserContinuationBoundaryTest(unittest.TestCase):
    def test_report_documents_rawkernel_as_allowed_user_code(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Yes. v2.0 allows it.", text)
        self.assertIn("cupy.RawKernel", text)
        self.assertIn("RTDL v2.0 can interoperate with CuPy-owned device arrays", text)
        self.assertIn("RTDL v2.0 accelerates arbitrary CuPy RawKernel programs", text)
        self.assertIn("Blocked", text)
        self.assertIn("user-owned GPU program text", text)

    def test_report_maps_v18_cpp_and_v20_cupy_analogies(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Python + RTDL", text)
        self.assertIn("user C/C++ code", text)
        self.assertIn("Python + CuPy + RTDL", text)
        self.assertIn("CuPy operations or RawKernel", text)
        self.assertIn("proves interoperability", text)
        self.assertIn("not official RTDL v2.0 partner", text)

    def test_report_names_four_control_apps_and_reason(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for app in (
            "database_analytics",
            "graph_analytics",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            self.assertIn(app, text)
        self.assertIn("not controls because v2.0 forbids partner", text)
        self.assertIn("continuations", text)
        self.assertIn("have not yet", text)
        self.assertIn("been implemented, measured, and reviewed", text)

    def test_public_boundary_doc_contains_same_rule(self) -> None:
        text = BOUNDARY_DOC.read_text(encoding="utf-8")

        self.assertIn("User-Owned Partner Continuations", text)
        self.assertIn("including `cupy.RawKernel`", text)
        self.assertIn("That user continuation belongs to the user's application", text)
        self.assertIn("RTDL v2.0 accelerates arbitrary CuPy RawKernel programs", text)
        self.assertIn("RTDL v2.0 can interoperate with CuPy-owned device arrays", text)


if __name__ == "__main__":
    unittest.main()
