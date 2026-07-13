from __future__ import annotations

import importlib.util
import argparse
import tempfile
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_modelnet40_normalized_batch_gate.py"


def _load_batch_module():
    spec = importlib.util.spec_from_file_location("run_xhd_modelnet40_normalized_batch_gate_goal5223", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5223ModelNet40AlgorithmAwareComparatorTest(unittest.TestCase):
    def test_algorithm_from_author_log_payload_reads_uniform_repeat_algorithm(self) -> None:
        module = _load_batch_module()

        payload = {"Running": {"Repeats": [{"Algorithm": "Hybrid"}, {"Algorithm": "Hybrid"}]}}

        self.assertEqual(module._algorithm_from_author_log_payload(payload), "Hybrid")

    def test_algorithm_from_author_log_payload_rejects_mixed_repeat_algorithms(self) -> None:
        module = _load_batch_module()

        payload = {"Running": {"Repeats": [{"Algorithm": "Hybrid"}, {"Algorithm": "XHD"}]}}

        with self.assertRaisesRegex(ValueError, "mixed author log algorithms"):
            module._algorithm_from_author_log_payload(payload)

    def test_author_runner_selects_hybrid_binary_for_hybrid_log(self) -> None:
        module = _load_batch_module()

        binary, variant, expected = module._author_runner_for_algorithm(
            "Hybrid",
            default_author_bin=Path("/author/main/hd_exec"),
            hybrid_author_bin=Path("/author/paper/hd_exec"),
        )

        self.assertEqual(binary, Path("/author/paper/hd_exec"))
        self.assertEqual(variant, "hybrid")
        self.assertEqual(expected, "Hybrid")

    def test_author_runner_selects_rt_binary_for_xhd_log(self) -> None:
        module = _load_batch_module()

        binary, variant, expected = module._author_runner_for_algorithm(
            "XHD",
            default_author_bin=Path("/author/main/hd_exec"),
            hybrid_author_bin=Path("/author/paper/hd_exec"),
        )

        self.assertEqual(binary, Path("/author/main/hd_exec"))
        self.assertEqual(variant, "rt")
        self.assertEqual(expected, "XHD")

    def test_hybrid_log_requires_hybrid_binary(self) -> None:
        module = _load_batch_module()

        with self.assertRaisesRegex(ValueError, "author-hybrid-bin"):
            module._author_runner_for_algorithm(
                "Hybrid",
                default_author_bin=Path("/author/main/hd_exec"),
                hybrid_author_bin=None,
            )

    def test_selection_strategy_can_pick_largest_unique_pairs_for_feasibility_probes(self) -> None:
        module = _load_batch_module()

        records = [
            {
                "category": "ModelNet40",
                "input": {
                    "normalize": True,
                    "translate": 0.0,
                    "files": [
                        {"path": "/local/storage/shared/HDDatasets/ModelNet40/a/train/a_1.off", "num_points": 10},
                        {"path": "/local/storage/shared/HDDatasets/ModelNet40/a/train/a_2.off", "num_points": 20},
                    ],
                },
            },
            {
                "category": "ModelNet40",
                "input": {
                    "normalize": True,
                    "translate": 0.0,
                    "files": [
                        {"path": "/local/storage/shared/HDDatasets/ModelNet40/b/train/b_1.off", "num_points": 100},
                        {"path": "/local/storage/shared/HDDatasets/ModelNet40/b/train/b_2.off", "num_points": 200},
                    ],
                },
            },
        ]

        selected = module._select_unique_modelnet_pairs(
            records,
            max_pairs=1,
            selection_strategy="largest_unique_pairs",
        )

        self.assertEqual(selected[0]["category"], "b")
        self.assertEqual(selected[0]["total_points"], 300)

    def test_chunk_selection_preserves_global_case_indices(self) -> None:
        module = _load_batch_module()

        selected = [{"name": f"case{i}"} for i in range(5)]

        chunked, summary = module._select_chunk(
            selected,
            start_index=None,
            end_index=None,
            chunk_index=1,
            chunk_size=2,
        )

        self.assertEqual([index for index, _item in chunked], [2, 3])
        self.assertEqual(summary["mode"], "chunk-index")
        self.assertEqual(summary["total_selected_before_chunk"], 5)
        self.assertEqual(summary["start_index"], 2)
        self.assertEqual(summary["end_index_exclusive"], 4)
        self.assertEqual(summary["selected_count_after_chunk"], 2)

    def test_range_selection_is_rejected_when_combined_with_chunk_index(self) -> None:
        module = _load_batch_module()

        with self.assertRaisesRegex(ValueError, "cannot be combined"):
            module._select_chunk(
                [{"name": "case"}],
                start_index=0,
                end_index=None,
                chunk_index=0,
                chunk_size=10,
            )

    def test_case_artifacts_support_skip_completed_and_aggregation(self) -> None:
        module = _load_batch_module()

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            matched = {
                "case_index": 3,
                "case_name": "0003_a__b",
                "total_points": 30,
                "case_matched": True,
            }
            failed = {
                "case_index": 4,
                "case_name": "0004_c__d",
                "total_points": 40,
                "case_matched": False,
                "case_error": {"type": "RuntimeError", "message": "boom"},
            }
            module._write_case_artifact(output_dir, "0003_a__b", matched)
            module._write_case_artifact(output_dir, "0004_c__d", failed)

            completed = module._read_completed_case_artifact(output_dir, "0003_a__b")
            self.assertIsNotNone(completed)
            self.assertTrue(completed["skipped_completed"])
            self.assertIsNone(module._read_completed_case_artifact(output_dir, "0004_c__d"))

            summary = module._aggregate_existing_case_artifacts(
                argparse.Namespace(
                    output_dir=output_dir,
                    goal_label="Goal5226",
                    log_index=None,
                    modelnet_zip=None,
                    extract_root=None,
                    paper_log_repo=None,
                    selection_strategy="all_unique_pairs",
                    max_pairs=400,
                )
            )

            self.assertEqual(summary["goal"], "Goal5226")
            self.assertEqual(summary["matched_case_count"], 1)
            self.assertEqual(summary["failed_case_count"], 1)
            self.assertFalse(summary["all_cases_matched"])
            self.assertEqual([case["case_index"] for case in summary["cases"]], [3, 4])

    def test_script_remains_app_owned_and_does_not_promote_modelnet_to_core(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertIn("algorithm_aware_author_comparator_selection", source)
        self.assertIn("--author-hybrid-bin", source)
        self.assertIn("--skip-completed", source)
        self.assertIn("--continue-on-error", source)
        self.assertIn("--aggregate-existing-cases", source)
        self.assertIn("--author-float32-normalization", source)
        self.assertIn("--grid-cell-builder", source)
        self.assertIn("--global-bound-early-break", source)
        self.assertIn("--skip-frontier-if-exact-seed", source)
        self.assertIn("grid_cell_builder=args.grid_cell_builder", source)
        self.assertIn("global_bound_early_break=bool(args.global_bound_early_break)", source)
        self.assertIn("skip_frontier_if_exact_seed=bool(args.skip_frontier_if_exact_seed)", source)
        forbidden_core_promotions = (
            "rtdsl.modelnet",
            "rtdsl.xhd",
            "native_modelnet",
            "native_xhd",
        )
        for forbidden in forbidden_core_promotions:
            self.assertNotIn(forbidden, source.lower())


if __name__ == "__main__":
    unittest.main()
