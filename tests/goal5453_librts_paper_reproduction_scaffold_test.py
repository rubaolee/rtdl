from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
SCRIPT = APP_DIR / "librts_reproduction.py"


def _load_app():
    spec = importlib.util.spec_from_file_location("librts_paper_reproduction", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load LibRTS paper app")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5453LibRTSPaperReproductionScaffoldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = _load_app()
        cls.manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))

    def test_provenance_and_claim_boundary_are_pinned(self):
        self.assertEqual(self.manifest["paper"]["doi"], "10.1145/3710848.3710850")
        author = self.manifest["author_artifact"]
        self.assertEqual(author["repository"], "https://github.com/RTSpatial/RTSpatial")
        self.assertEqual(author["commit"], "52509e8022abeab722f5a9a89d1917e8b481defe")
        self.assertEqual(author["archive_md5"], "89e589f086038f1cd3af9e3ed67da8c8")
        self.assertEqual(
            self.manifest["reproduction_scope"]["status"],
            "scoped_correctness_and_system_extraction_complete__full_paper_not_reproduced",
        )
        self.assertTrue(self.manifest["boundaries"]["bounded_same_input_point_contains_count_claimed"])
        self.assertTrue(self.manifest["boundaries"]["bounded_same_input_range_contains_count_claimed"])
        self.assertTrue(self.manifest["boundaries"]["bounded_same_input_range_intersects_count_claimed"])
        for key in (
            "full_paper_reproduction_claimed",
            "independent_author_pipeline_reconstruction_claimed",
            "whole_program_speedup_claimed",
            "author_performance_parity_claimed",
            "native_backend_completion_claimed",
        ):
            self.assertFalse(self.manifest["boundaries"][key])

    def test_historical_benchmark_is_not_reclassified(self):
        mapping = self.manifest["rtdl_program"]["historical_asset_mapping"]
        self.assertFalse(mapping["historical_benchmark_is_paper_reproduction"])
        backend_scope = self.manifest["rtdl_program"]["backend_scope"]
        self.assertEqual(backend_scope["local_semantic_reference"], "cpu")
        self.assertEqual(backend_scope["accelerated_pod_backend"], "optix")
        self.assertFalse(backend_scope["embree_in_scope"])
        self.assertFalse(backend_scope["hiprt_in_scope"])
        readme = (APP_DIR / "README.md").read_text(encoding="utf-8")
        self.assertIn("not retroactively treated as paper-reproduction evidence", readme)
        self.assertIn("LibRTS scoped correctness and system extraction are complete", readme)
        self.assertIn("not full all-figure/performance paper reproduction", readme)
        self.assertIn("Embree is explicitly out of scope", readme)

    def test_local_point_contains_relation_matches_exact_fixture(self):
        payload = self.app.run_local_point_contains()
        self.assertTrue(payload["matched"])
        self.assertFalse(payload["author_comparator_used"])
        self.assertEqual(payload["rtdl"]["valid_count"], 5)
        self.assertEqual(
            payload["rtdl"]["candidate_id_rows"],
            [[0, 0], [1, 0], [1, 1], [2, 1], [3, 2]],
        )
        self.assertEqual(
            payload["rtdl"]["contract"],
            "generic_expanded_aabb_point_membership_rows_2d_v1",
        )
        self.assertFalse(payload["rtdl"]["native_engine_customization"])
        self.assertTrue(payload["claim_boundary"]["local_reference_only"])

    def test_backend_selection_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported LibRTS reproduction backend"):
            self.app.run_local_point_contains(backend="embree")

    def test_cli_writes_local_reference_without_author_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "summary.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--mode",
                    "local-point-contains",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(payload["matched"])
            self.assertFalse(payload["claim_boundary"]["author_same_input_agreement_claimed"])
            self.assertFalse(payload["claim_boundary"]["performance_claimed"])

    def test_portfolio_lists_externally_reviewed_librts_closeout(self):
        snapshot = json.loads(
            (ROOT / "Paper-reproduction-apps" / "paper_app_status_snapshot.json").read_text(
                encoding="utf-8"
            )
        )
        row = snapshot["apps"]["librts-paper"]
        self.assertTrue(row["externally_reviewed_closeout"])
        self.assertEqual(
            row["scoped_status"],
            "scoped_correctness_and_system_extraction_complete__externally_reviewed_and_approved",
        )
        self.assertEqual(
            row["review_evidence"],
            "history/internal_docs/review_goals5519_5525_librts_final_closeout_verified_2026-07-13.md",
        )
        self.assertFalse(row["full_paper_reproduction_claimed"])


if __name__ == "__main__":
    unittest.main()
