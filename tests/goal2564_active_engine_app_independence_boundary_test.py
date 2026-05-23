from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCANNED_PATHS = (
    ROOT / "src/native/embree",
    ROOT / "src/native/optix",
    ROOT / "src/rtdsl/partner_adapters.py",
    ROOT / "src/rtdsl/columnar_partner.py",
)
REPORT = ROOT / "docs/reports/goal2564_active_engine_app_independence_boundary_2026-05-23.md"

APP_SPECIFIC_PATTERN = re.compile(
    r"dbscan|raydb|robot_collision|robot|collision|barnes|inverse_square|"
    r"pairwise_inverse_square_force|robot_collision_pose_flags|RayDB-style",
    re.IGNORECASE,
)


class Goal2564ActiveEngineAppIndependenceBoundaryTest(unittest.TestCase):
    def test_active_engine_and_shared_partner_modules_have_no_app_vocabulary(self) -> None:
        hits: list[str] = []
        for path in self._scanned_files():
            text = path.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if APP_SPECIFIC_PATTERN.search(line):
                    hits.append(f"{path.relative_to(ROOT)}:{line_no}: {line.strip()}")

        self.assertEqual([], hits)

    def test_report_records_scope_and_deferred_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("active native Embree/OptiX engine paths", text)
        self.assertIn("Python compatibility wrappers still contain legacy DB-shaped names", text)
        self.assertIn("Vulkan/HIPRT/Apple RT are explicitly out of scope before v2.1", text)
        self.assertIn("Goal2564ActiveEngineAppIndependenceBoundaryTest", text)

    @staticmethod
    def _scanned_files() -> list[Path]:
        files: list[Path] = []
        for path in SCANNED_PATHS:
            if path.is_file():
                files.append(path)
                continue
            files.extend(
                child
                for child in path.rglob("*")
                if child.is_file()
                and child.suffix in {".c", ".cc", ".cpp", ".h", ".hpp", ".cu"}
            )
        return sorted(files)


if __name__ == "__main__":
    unittest.main()
