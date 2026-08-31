from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3596_rayjoin_public_cdb_pip_route_audit_2026-06-06.md"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"


class Goal3596RayJoinPublicCdbPipRouteAuditTest(unittest.TestCase):
    def test_report_records_best_current_route_and_rejections(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "CuPy dense CUDA-core baseline",
            "RTDL/OptiX exact prepared count",
            "best RTDL-only route, still slower than CuPy",
            "device_filtered_validated",
            "1429 vs exact 1417",
            "crossing_only",
            "152 vs exact 1417",
            "recommend CuPy for simple bounded PIP count",
            "generic exact point-in-closed-shape count primitive",
        ):
            self.assertIn(phrase, text)

    def test_report_keeps_claim_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "does not authorize release",
            "paper reproduction",
            "broad RT-core speedup",
            "automatic dispatch",
            "zero-copy claims",
        ):
            self.assertIn(phrase, text)

    def test_readme_explains_no_partner_pip_count_route(self) -> None:
        text = README.read_text(encoding="utf-8")
        for phrase in (
            "For no-partner RTDL-only PIP scalar counts",
            "--execution-route prepared_optix --pip-count-mode exact",
            "best current RTDL-only PIP count route",
            "prepared_optix_cupy_refined_pip",
            "not as the default scalar count path",
            "goal3596_rayjoin_public_cdb_pip_route_audit",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
