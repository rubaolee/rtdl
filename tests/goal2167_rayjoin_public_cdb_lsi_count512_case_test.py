from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal2159_rayjoin_public_cdb_runner.py"


class Goal2167RayjoinPublicCdbLsiCount512CaseTest(unittest.TestCase):
    def test_runner_defines_count512_lsi_stress_case(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("lsi_county256_soil256_count512", text)
        self.assertIn("br_county_start256_count512.cdb", text)
        self.assertIn("br_soil_start256_count512.cdb", text)
        self.assertIn("count-first prepared OptiX checks", text)


if __name__ == "__main__":
    unittest.main()
