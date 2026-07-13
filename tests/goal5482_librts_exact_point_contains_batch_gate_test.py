from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
import sys

sys.path.insert(0, str(APP))
SPEC = importlib.util.spec_from_file_location(
    "librts_exact_point_contains_batch", APP / "run_exact_point_contains_batch_gate.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5482LibrtsExactPointContainsBatchGateTest(unittest.TestCase):
    def test_member_resolution_requires_verified_hash_and_stays_inside_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            extracted = root / "extracted"
            member = extracted / "PPoPPAE" / "datasets" / "polygons" / "x.wkt"
            member.parent.mkdir(parents=True)
            member.write_bytes(b"POLYGON ((0 0, 1 0, 0 1, 0 0))\n")
            extraction = {
                "claim_boundary": {"archive_subset_extracted": True},
                "extraction": {
                    "final_path": str(extracted),
                    "selected_members": [
                        {
                            "relative_path": "PPoPPAE/datasets/polygons/x.wkt",
                            "size_bytes": member.stat().st_size,
                            "sha256": MODULE._sha256(member),
                        }
                    ],
                },
            }
            resolved = MODULE._resolve_member(
                extraction=extraction,
                member="PPoPPAE/datasets/polygons/x.wkt",
            )
            self.assertEqual(resolved, member.resolve())
            with self.assertRaises(RuntimeError):
                MODULE._resolve_member(extraction=extraction, member="missing.wkt")
            member.write_bytes(b"tampered\n")
            with self.assertRaises(RuntimeError):
                MODULE._resolve_member(
                    extraction=extraction,
                    member="PPoPPAE/datasets/polygons/x.wkt",
                )

    def test_case_contract_uses_the_five_remaining_figure_six_members(self):
        self.assertEqual(len(MODULE.CASE_MEMBERS), 5)
        for geometry, query in MODULE.CASE_MEMBERS.values():
            self.assertTrue(geometry.startswith("PPoPPAE/datasets/polygons/"))
            self.assertTrue(
                query.startswith("PPoPPAE/datasets/queries/point-contains_queries_100000/")
            )


if __name__ == "__main__":
    unittest.main()
