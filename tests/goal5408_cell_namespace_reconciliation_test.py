from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5408_cell_namespace_reconciliation.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5408_cell_namespace_reconciliation_pod.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5408_runner", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load Goal5408 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5408CellNamespaceReconciliationTest(unittest.TestCase):
    def test_compact_to_original_lookup_requires_dense_unique_compact_ids(self) -> None:
        module = _load_module()
        lookup = module.compact_to_original_lookup(
            np.asarray([0, 1, 2], dtype=np.int64),
            np.asarray([10, 42, 99], dtype=np.int64),
        )
        self.assertEqual([10, 42, 99], lookup.tolist())
        with self.assertRaises(ValueError):
            module.compact_to_original_lookup(
                np.asarray([0, 2], dtype=np.int64),
                np.asarray([10, 99], dtype=np.int64),
            )
        with self.assertRaises(ValueError):
            module.compact_to_original_lookup(
                np.asarray([0, 0], dtype=np.int64),
                np.asarray([10, 99], dtype=np.int64),
            )

    def test_map_compact_cells_to_original(self) -> None:
        module = _load_module()
        lookup = np.asarray([10, 42, 99], dtype=np.int64)
        mapped = module.map_compact_cells_to_original(
            np.asarray([2, 0, 1, 2], dtype=np.int64),
            lookup,
        )
        self.assertEqual([99, 10, 42, 99], mapped.tolist())
        with self.assertRaises(ValueError):
            module.map_compact_cells_to_original(np.asarray([3], dtype=np.int64), lookup)

    def test_sample_namespace_reconciliation_distinguishes_compact_and_original(self) -> None:
        module = _load_module()
        rows = module.sample_namespace_reconciliation(
            source_ids=np.asarray([5, 5, 6, 6], dtype=np.int64),
            compact_cell_ids=np.asarray([0, 1, 0, 2], dtype=np.int64),
            original_cell_ids_for_rows=np.asarray([10, 42, 10, 99], dtype=np.int64),
            global_compact_cell_ids=np.asarray([0, 1, 2], dtype=np.int64),
            global_original_cell_ids=np.asarray([10, 42, 99], dtype=np.int64),
            sample_source_ids=[5, 6, 7],
            sample_cell_ids=[42, 2, 99],
        )
        self.assertTrue(rows[0]["author_cell_present_as_original_in_source"])
        self.assertFalse(rows[0]["author_cell_present_as_compact_in_source"])
        self.assertTrue(rows[1]["author_cell_present_as_compact_in_source"])
        self.assertFalse(rows[1]["author_cell_present_as_original_in_source"])
        self.assertTrue(rows[2]["author_cell_exists_as_global_original"])
        self.assertFalse(rows[2]["author_cell_present_as_original_in_source"])

    def test_classification_labels_unrecovered_namespace_gap(self) -> None:
        module = _load_module()
        classification = module.classify_namespace_reconciliation(
            [
                {
                    "author_cell_present_as_compact_in_source": False,
                    "author_cell_present_as_original_in_source": False,
                    "author_cell_exists_as_global_compact": False,
                    "author_cell_exists_as_global_original": False,
                }
            ]
        )
        self.assertEqual(
            "author_sample_cell_ids_not_recovered_in_compact_or_original_namespace",
            classification["label"],
        )
        self.assertFalse(classification["any_sample_present_as_compact_or_original"])

    def test_runner_keeps_claim_boundary_closed(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"explicit_lb_support_claimed": False', source)
        self.assertIn('"figure7_reproduction_claimed": False', source)
        self.assertIn('"full_xhd_paper_reproduction_claimed": False', source)
        self.assertIn("compact_original_namespace_remap_explains_author_samples", source)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal5408 POD artifact not present")
    def test_pod_artifact_is_namespace_reconciliation_not_lb_support(self) -> None:
        import json

        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            "rtdl.paper_reproduction.xhd.goal5408.cell_namespace_reconciliation.v1",
            payload["schema"],
        )
        self.assertTrue(payload["matched"])
        self.assertFalse(payload["decision"]["explicit_lb_support_authorized"])
        self.assertFalse(payload["claim_boundary"]["explicit_lb_support_claimed"])
        self.assertIn("classification", payload)
        self.assertIn("author_sample_namespace_reconciliation", payload)


if __name__ == "__main__":
    unittest.main()
