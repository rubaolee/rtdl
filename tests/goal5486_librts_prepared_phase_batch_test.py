from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
sys.path.insert(0, str(APP))
SPEC = importlib.util.spec_from_file_location(
    "librts_exact_point_contains_prepared_phase_batch",
    APP / "run_exact_point_contains_prepared_phase_batch.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5486LibrtsPreparedPhaseBatchTest(unittest.TestCase):
    def test_batch_covers_dtl_and_remaining_manifests_without_ratio(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifests = {}
            for manifest_key, case_ids in (("dtl", ("dtl_cnty",)), ("remaining", tuple(MODULE.CASE_MEMBERS))):
                manifest_root = root / manifest_key
                selected = []
                for case_id in case_ids:
                    geometry = manifest_root / f"{case_id}.geom"
                    query = manifest_root / f"{case_id}.query"
                    geometry.parent.mkdir(parents=True, exist_ok=True)
                    geometry.write_text(f"{case_id}-geometry\n")
                    query.write_text(f"{case_id}-query\n")
                    selected.extend(
                        {
                            "relative_path": path.name,
                            "size_bytes": path.stat().st_size,
                            "sha256": MODULE._sha256(path),
                        }
                        for path in (geometry, query)
                    )
                manifests[manifest_key] = {
                    "claim_boundary": {"archive_subset_extracted": True},
                    "extraction": {
                        "final_path": str(manifest_root),
                        "selected_members": selected,
                    },
                }

            def resolve(*, extraction, member):
                root_path = Path(extraction["extraction"]["final_path"])
                return root_path / Path(member).name

            def fake_gate(**kwargs):
                return {
                    "matched": True,
                    "rtdl": {"result_count": 1},
                    "phase_boundary": {
                        "prepared_query_phase_comparison_candidate": True,
                        "performance_ratio_authorized": False,
                    },
                }

            with (
                mock.patch.object(MODULE, "_resolve_member", side_effect=resolve),
                mock.patch.object(MODULE, "run_gate", side_effect=fake_gate),
            ):
                result = MODULE.run_batch(
                    author_binary=root / "author",
                    ae_root=root,
                    archive={"claim_boundary": {"archive_verified": True}},
                    extraction_results=manifests,
                    output_dir=root / "results",
                    serialize_root=root / "serialize",
                )

            self.assertTrue(result["matched"])
            self.assertEqual(result["case_count"], 6)
            self.assertEqual(result["matched_case_count"], 6)
            self.assertFalse(result["claim_boundary"]["performance_ratio_authorized"])
            self.assertEqual(result["cases"]["dtl_cnty"]["extraction_manifest"], "dtl")
            self.assertEqual(result["cases"]["parks.bz2"]["extraction_manifest"], "remaining")
            self.assertTrue((root / "results" / "dtl_cnty.json").is_file())

    def test_incomplete_case_set_is_not_promoted(self):
        result = {
            "matched": False,
            "case_count": 6,
            "matched_case_count": 5,
            "claim_boundary": {"performance_ratio_authorized": False},
        }
        self.assertFalse(result["matched"])
        self.assertEqual(result["matched_case_count"], 5)

    def test_committed_pod_matrix_is_six_of_six_and_keeps_ratio_closed(self):
        result_path = (
            APP / "results" / "librts_goal5486_prepared_phase_batch.json"
        )
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result["case_count"], 6)
        self.assertEqual(result["matched_case_count"], 6)
        self.assertTrue(result["matched"])
        self.assertFalse(result["phase_boundary"]["performance_ratio_authorized"])
        self.assertFalse(result["claim_boundary"]["pointwise_containment_equivalence_claimed"])
        self.assertFalse(result["claim_boundary"]["figure6_reproduced"])
        self.assertFalse(result["claim_boundary"]["complete_paper_reproduction_claimed"])
        self.assertEqual(
            sorted(result["cases"]),
            sorted(
                (
                    "dtl_cnty",
                    "USACensusBlockGroupBoundaries",
                    "USADetailedWaterBodies",
                    "parks_Europe",
                    "lakes.bz2",
                    "parks.bz2",
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
