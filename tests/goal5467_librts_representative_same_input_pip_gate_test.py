from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
RUNNER_PATH = APP_DIR / "run_same_input_representative_pip_gate.py"
DATA_DIR = APP_DIR / "data" / "representative" / "goal5466_blockgroups_simple64_100k"


def _load_runner():
    sys.path.insert(0, str(APP_DIR))
    spec = importlib.util.spec_from_file_location("librts_goal5467_gate", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5467LibRtsRepresentativeSameInputPipGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = _load_runner()

    def test_committed_linux_gate_matches_relation_not_only_count(self) -> None:
        payload = json.loads(
            (APP_DIR / "results" / "librts_goal5467_representative_same_input_pip.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["author"]["result_count"], 71626)
        self.assertEqual(payload["instrumented_author_comparator"]["result_count"], 71626)
        self.assertEqual(payload["rtdl"]["result_count"], 71626)
        self.assertTrue(payload["comparison"]["pair_rows_equal"])
        self.assertTrue(payload["comparison"]["canonical_row_sha256_equal"])
        self.assertEqual(
            payload["instrumented_author_comparator"]["canonical_row_sha256"],
            payload["rtdl"]["canonical_row_sha256"],
        )
        self.assertEqual(payload["rtdl"]["partner"], "numba_cuda")
        self.assertTrue(payload["rtdl"]["rt_core_accelerated"])
        self.assertFalse(payload["claim_boundary"]["figure12_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(payload["claim_boundary"]["embree_evidence_used"])

    def test_diagnostic_preserves_standard_route_mismatch_and_compatibility_match(self) -> None:
        payload = json.loads(
            (APP_DIR / "results" / "librts_goal5467_representative_pip_semantics_diagnostic.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(payload["observed_author_row_count"], 71626)
        self.assertEqual(payload["rtdl_count"], 71624)
        self.assertFalse(payload["observed_author_matches_rtdl_rows"])
        self.assertEqual(payload["rtdl_candidate_author_numba_compatibility_count"], 71626)
        self.assertTrue(
            payload[
                "observed_author_matches_rtdl_candidate_author_numba_compatibility_rows"
            ]
        )

    def test_summary_fails_closed_on_relation_mismatch(self) -> None:
        rtdl_payload = {
            "schema": "test",
            "candidate_id_rows": [[0, 0], [1, 1]],
            "result_count": 2,
            "polygon_count": 64,
            "point_count": 100000,
            "rt_core_accelerated": True,
            "native_engine_customization": False,
        }
        with tempfile.TemporaryDirectory() as temporary:
            row_path = Path(temporary) / "author_rows.csv"
            row_path.write_text("0,0\n1,2\n", encoding="utf-8")
            with mock.patch.object(
                self.runner,
                "run_author_compatible_pip_rows",
                return_value=rtdl_payload,
            ):
                payload = self.runner.build_summary(
                    polygons_path=DATA_DIR / "blockgroups_simple64_arcgis.wkt",
                    points_path=DATA_DIR / "blockgroups_simple64_queries_seed0_100k.wkt",
                    dataset_manifest_path=DATA_DIR / "manifest.json",
                    author_stdout="Results 2\n",
                    author_command=["author"],
                    instrumented_author_stdout="Results 2\n",
                    instrumented_author_command=["instrumented-author"],
                    author_rows_path=row_path,
                    environment_label="test",
                    gpu_label="test",
                )
        self.assertFalse(payload["matched"])
        self.assertFalse(payload["comparison"]["pair_rows_equal"])

    def test_row_dump_patch_is_comparator_only_and_app_owned(self) -> None:
        patch = (
            APP_DIR / "author_patches" / "goal5467_export_author_pip_rows.patch"
        ).read_text(encoding="utf-8")
        self.assertIn("LIBRTS_PIP_ROW_DUMP", patch)
        self.assertIn("results.data()", patch)
        self.assertNotIn("pnpoly(", patch)
        self.assertNotIn("index.Query", patch)


if __name__ == "__main__":
    unittest.main()
