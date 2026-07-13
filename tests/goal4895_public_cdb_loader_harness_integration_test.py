import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal4895PublicCdbLoaderHarnessIntegrationTest(unittest.TestCase):
    def test_section57_public_harness_uses_public_packed_cdb_loader(self) -> None:
        harness = (
            ROOT / "history" / "internal_docs" / "goal4880_section57_public_primitives_overlay_harness.py"
        ).read_text(encoding="utf-8")

        self.assertIn("from rtdsl import load_planar_map_cdb_packed_inputs", harness)
        self.assertIn("return load_planar_map_cdb_packed_inputs(path)", harness)
        self.assertNotIn("from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs", harness)


if __name__ == "__main__":
    unittest.main()
