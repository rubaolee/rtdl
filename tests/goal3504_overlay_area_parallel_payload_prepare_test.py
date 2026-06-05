from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"


class Goal3504OverlayAreaParallelPayloadPrepareTest(unittest.TestCase):
    def test_runner_exposes_parallel_payload_prepare_evidence_mode(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--payload-workers",
            "--parallel-payload-prepare-evidence",
            "_prepare_geometry_payload_bundle_parallel",
            "_geometry_payload_parts_worker",
            "parallel_geometry_payload_prepare",
            "geometry_plus_payload_prepare",
            "rtdl.goal3504.overlay_area_parallel_payload_prepare.v1",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_parallel_path_is_opt_in(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("parser.add_argument(", text)
        self.assertIn('"--payload-workers"', text)
        self.assertIn("default=1", text)
        self.assertIn("parallel_payload_prepare_used = payload_workers > 1", text)


if __name__ == "__main__":
    unittest.main()
