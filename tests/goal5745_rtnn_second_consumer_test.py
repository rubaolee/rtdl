from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.metric_knn import cpu_aabb_candidate_provider_3d  # noqa: E402


FIXTURE = (
    ROOT
    / "Paper-reproduction-apps/rtnn-paper/data/fixtures/goal5531_exact_knn"
)


def _load(path: Path) -> np.ndarray:
    return np.loadtxt(path, delimiter=",", dtype=np.float32)


def _load_rtnn_app():
    path = ROOT / "Paper-reproduction-apps/rtnn-paper/rtdl3_action_migration.py"
    spec = importlib.util.spec_from_file_location("goal5745_real_rtnn_consumer", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5745RtnnSecondConsumerTest(unittest.TestCase):
    def test_preexisting_rtnn_fixture_uses_same_generic_metric_completion(self) -> None:
        data = _load(FIXTURE / "search.xyz")
        queries = _load(FIXTURE / "queries.xyz")
        # The third frozen RTNN query has no zero-distance self match, so the
        # metric-kNN family and RTNN's strict (0,max) window are identical on
        # this real paper-app slice.  The other fixture queries intentionally
        # exercise zero-distance exclusion and are not claimed equivalent.
        queries = queries[2:3]
        result = _load_rtnn_app().run_generic_metric_knn_second_consumer_points(
            data,
            queries,
            k=4,
            min_distance=0.0,
            max_distance=200.0,
            candidate_provider=cpu_aabb_candidate_provider_3d,
        )
        self.assertTrue(result["matched"])
        self.assertTrue(result["consumer_is_real_rtnn_paper_app"])
        self.assertFalse(result["historical_production_route_changed"])
        metadata = result["runtime_metadata"]
        self.assertTrue(metadata["compiler_or_canonical_resolution_used"])
        self.assertTrue(
            metadata["canonical_provider_stable_id"].endswith(
                "/prepared_metric_knn_3d_optix"
            )
        )
        self.assertEqual(
            metadata["statement_stable_id"],
            "metric_knn.filter_refine_euclidean_3d.v1",
        )

    def test_second_consumer_is_not_an_arkade_fixture(self) -> None:
        self.assertIn("rtnn-paper", FIXTURE.as_posix())
        self.assertNotIn("arkade", FIXTURE.as_posix().lower())
        self.assertTrue((FIXTURE / "search.xyz").is_file())
        self.assertTrue((FIXTURE / "queries.xyz").is_file())


if __name__ == "__main__":
    unittest.main()
