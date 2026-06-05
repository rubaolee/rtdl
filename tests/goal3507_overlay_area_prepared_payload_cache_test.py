from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"


class Goal3507OverlayAreaPreparedPayloadCacheTest(unittest.TestCase):
    def test_runner_exposes_prepared_payload_cache_evidence_mode(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--payload-cache-dir",
            "--payload-cache-mode",
            "--payload-cache-evidence",
            "_write_prepared_payload_cache",
            "_read_prepared_payload_cache",
            "payload_cache_load",
            "payload_cache_write",
            "rtdl.goal3507.overlay_area_prepared_payload_cache.v1",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_cache_mode_is_off_by_default_and_read_requires_dir(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('choices=("off", "read", "write", "refresh")', text)
        self.assertIn('default="off"', text)
        self.assertIn('payload_cache_mode != "off" and payload_cache_dir is None', text)
        self.assertIn('raise ValueError("--payload-cache-mode requires --payload-cache-dir")', text)


if __name__ == "__main__":
    unittest.main()
