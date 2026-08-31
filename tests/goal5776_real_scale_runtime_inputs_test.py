from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from goal5776_real_scale_formal_contract import UNITS
from goal5776_real_scale_runtime_inputs import build_real_scale_inputs


class Goal5776RealScaleRuntimeInputsTest(unittest.TestCase):
    def test_mapping_covers_all_units_and_keeps_raydb_cold_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = (
                "common/raydb/q11/packet.json",
                "common/rayjoin/top4_county.cdb",
                "common/rayjoin/top4_zipcode.cdb",
                "common/rt_barneshut/prepared_arrays.json",
                "common/rt_barneshut/expected_forces.txt",
                "common/librts/parks/cache/parks_bz2.npz",
                "common/librts/parks/cache/parks_bz2.json",
                "common/librts/parks/queries/point_contains_100000.wkt",
                "common/librts/parks/queries/range_contains_100000.wkt",
                "triangle/com-dblp.edge",
                "triangle/cit-Patents.edge",
                "triangle/soc-LiveJournal1.edge",
            )
            for name in files:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}\n", encoding="utf-8")
            for name in ("particle", "rtnn", "xhd", "rtdbscan"):
                (root / name).mkdir()
            evidence = root / "target_evidence.json"
            evidence.write_text("{}\n", encoding="utf-8")
            mapping = build_real_scale_inputs(
                root, refinement_evidence_path=evidence)
            self.assertEqual(set(mapping), {unit.unit_id for unit in UNITS})
            raydb = next(unit for unit in UNITS if unit.app == "raydb")
            self.assertEqual(raydb.supported_lifecycles, (
                "installed_cold_compile_prepare_execute",
            ))
            self.assertEqual(
                mapping["rayjoin__top4_six_batch"]["lsi_capacity"], 1_000_000)


if __name__ == "__main__":
    unittest.main()
