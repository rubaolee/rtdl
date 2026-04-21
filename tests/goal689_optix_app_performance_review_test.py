import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal689_optix_app_performance_review_2026-04-21.md"


class Goal689OptixAppPerformanceReviewTest(unittest.TestCase):
    def test_report_records_required_optix_performance_boundaries(self):
        text = REPORT.read_text(encoding="utf-8")
        required = [
            "OptiX traversal eligible",
            "CUDA-through-OptiX",
            "Host-indexed fallback",
            "Python/interface dominated",
            "GTX 1070 has no NVIDIA RT cores",
            "graph BFS/triangle",
            "segment/polygon",
            "rt.reduce_rows",
            "tuple[dict, ...]",
            "phase-split benchmark",
            "RTX-class",
            "robot collision / visibility / ray-triangle any-hit",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_covers_all_public_optix_app_rows(self):
        text = REPORT.read_text(encoding="utf-8")
        app_matrix = (ROOT / "docs" / "app_engine_support_matrix.md").read_text(encoding="utf-8")
        optix_apps = []
        for line in app_matrix.splitlines():
            if not line.startswith("| `examples/"):
                continue
            cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            if len(cells) >= 4 and cells[3] in {"direct_cli_native", "direct_cli_native_assisted"}:
                optix_apps.append(cells[0])
        self.assertGreater(len(optix_apps), 0)
        for app in optix_apps:
            with self.subTest(app=app):
                self.assertIn(app, text)


if __name__ == "__main__":
    unittest.main()
