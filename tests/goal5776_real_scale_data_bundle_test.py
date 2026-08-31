from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from goal5776_target_prepare import _extract_data


class Goal5776RealScaleDataBundleTest(unittest.TestCase):
    def test_deterministic_bundle_stream_extracts_and_rehashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            common = root / "common"
            common_names = (
                "librts/parks/cache/parks_bz2.json",
                "librts/parks/cache/parks_bz2.npz",
                "librts/parks/queries/point_contains_100000.wkt",
                "librts/parks/queries/range_contains_100000.wkt",
                "raydb/q11/data.bin", "raydb/q11/expected_rows.json",
                "raydb/q11/packet.json", "raydb/q11/predicate.txt",
                "rayjoin/top4_county.cdb", "rayjoin/top4_zipcode.cdb",
                "rt_barneshut/expected_forces.txt",
                "rt_barneshut/prepared_arrays.json",
            )
            for index, name in enumerate(common_names):
                path = common / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"common-{index}\n".encode())
            roots = {}
            for name in ("particle", "rtnn", "xhd", "rtdbscan", "triangle"):
                path = root / name
                path.mkdir()
                (path / "payload.bin").write_bytes(name.encode())
                roots[name] = path
            output = root / "DATA.tar.gz"
            script = Path(__file__).resolve().parents[1] / \
                "scripts/goal5776_build_real_scale_data_bundle.py"
            command = [
                sys.executable, str(script), "--common-root", str(common),
                "--particle-root", str(roots["particle"]),
                "--rtnn-root", str(roots["rtnn"]),
                "--xhd-root", str(roots["xhd"]),
                "--rtdbscan-root", str(roots["rtdbscan"]),
                "--triangle-root", str(roots["triangle"]),
                "--output", str(output),
            ]
            first = subprocess.run(
                command, text=True, capture_output=True, check=True)
            summary = json.loads(first.stdout)
            self.assertEqual(summary["file_count"], len(common_names) + 5)
            extracted = root / "extracted"
            extracted.mkdir()
            manifest = _extract_data(output, extracted)
            self.assertEqual(manifest["file_count"], len(common_names) + 5)
            self.assertEqual(
                (extracted / "DATA/triangle/payload.bin").read_bytes(),
                b"triangle")


if __name__ == "__main__":
    unittest.main()
