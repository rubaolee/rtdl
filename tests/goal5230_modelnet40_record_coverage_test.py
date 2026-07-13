from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "build_xhd_modelnet40_record_coverage.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_xhd_modelnet40_record_coverage_goal5230", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _record(path_a: str, path_b: str, *, hd_result: float = 0.5) -> dict[str, object]:
    return {
        "category": "ModelNet40",
        "relative_log_path": f"{Path(path_a).stem}__{Path(path_b).stem}.json",
        "hd_result": hd_result,
        "input": {
            "normalize": True,
            "translate": 0.0,
            "type": "off",
            "files": [
                {"path": path_a, "num_points": 10},
                {"path": path_b, "num_points": 20},
            ],
        },
        "running": {"num_points_per_cell": 32, "max_hit": 64},
    }


def _fake_algorithm(record: dict[str, object], *, paper_log_repo: Path | None) -> str | None:
    return str(record.get("algorithm", "Hybrid"))


class Goal5230ModelNet40RecordCoverageTest(unittest.TestCase):
    def test_record_coverage_maps_duplicate_records_to_matched_unique_pair(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = "/local/storage/shared/HDDatasets/ModelNet40/a/train/a_1.off"
            b = "/local/storage/shared/HDDatasets/ModelNet40/a/train/a_2.off"
            log_index = root / "log_index.json"
            unique_summary = root / "unique_summary.json"
            log_index.write_text(
                json.dumps({"run_all_records": [_record(a, b), _record(a, b)]}),
                encoding="utf-8",
            )
            unique_summary.write_text(
                json.dumps(
                    {
                        "cases": [
                            {
                                "case_index": 0,
                                "case_name": "0000_a_1__a_2",
                                "members": [
                                    "ModelNet40/a/train/a_1.off",
                                    "ModelNet40/a/train/a_2.off",
                                ],
                                "case_matched": True,
                                "author_log": {"hd_result": 0.5},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            summary = module.build_summary(
                argparse.Namespace(
                    log_index=log_index,
                    unique_summary=unique_summary,
                    paper_log_repo=None,
                    goal_label="Goal5230",
                    tolerance=1e-6,
                )
            )

        self.assertTrue(summary["all_records_covered"])
        self.assertEqual(summary["record_count"], 2)
        self.assertEqual(summary["unique_pair_count"], 1)
        self.assertEqual(summary["covered_record_count"], 2)
        self.assertEqual(summary["duplicate_count_distribution"], {"2": 1})

    def test_record_coverage_allows_different_algorithms_for_same_value_signature(self) -> None:
        module = _load_module()
        old_algorithm = module._record_algorithm
        module._record_algorithm = _fake_algorithm
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                a = "/local/storage/shared/HDDatasets/ModelNet40/a/train/a_1.off"
                b = "/local/storage/shared/HDDatasets/ModelNet40/a/train/a_2.off"
                first = _record(a, b)
                second = _record(a, b)
                first["algorithm"] = "Hybrid"
                second["algorithm"] = "Ray Tracing"
                log_index = root / "log_index.json"
                unique_summary = root / "unique_summary.json"
                log_index.write_text(json.dumps({"run_all_records": [first, second]}), encoding="utf-8")
                unique_summary.write_text(
                    json.dumps(
                        {
                            "cases": [
                                {
                                    "case_index": 0,
                                    "case_name": "0000_a_1__a_2",
                                    "members": [
                                        "ModelNet40/a/train/a_1.off",
                                        "ModelNet40/a/train/a_2.off",
                                    ],
                                    "case_matched": True,
                                    "author_log": {"hd_result": 0.5},
                                }
                            ]
                        }
                    ),
                    encoding="utf-8",
                )

                summary = module.build_summary(
                    argparse.Namespace(
                        log_index=log_index,
                        unique_summary=unique_summary,
                        paper_log_repo=None,
                        goal_label="Goal5230",
                        tolerance=1e-6,
                    )
                )
        finally:
            module._record_algorithm = old_algorithm

        self.assertTrue(summary["all_records_covered"])
        self.assertEqual(summary["algorithm_distribution"], {"Hybrid": 1, "Ray Tracing": 1})
        self.assertEqual(summary["pair_algorithm_set_distribution"], {"Hybrid + Ray Tracing": 1})

    def test_record_coverage_rejects_duplicate_signature_mismatch(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = "/local/storage/shared/HDDatasets/ModelNet40/a/train/a_1.off"
            b = "/local/storage/shared/HDDatasets/ModelNet40/a/train/a_2.off"
            log_index = root / "log_index.json"
            unique_summary = root / "unique_summary.json"
            log_index.write_text(
                json.dumps({"run_all_records": [_record(a, b, hd_result=0.5), _record(a, b, hd_result=0.6)]}),
                encoding="utf-8",
            )
            unique_summary.write_text(json.dumps({"cases": []}), encoding="utf-8")

            summary = module.build_summary(
                argparse.Namespace(
                    log_index=log_index,
                    unique_summary=unique_summary,
                    paper_log_repo=None,
                    goal_label="Goal5230",
                    tolerance=1e-6,
                )
            )

        self.assertFalse(summary["all_records_covered"])
        self.assertEqual(summary["duplicate_signature_mismatch_count"], 1)

    def test_record_coverage_rejects_missing_or_unmatched_unique_case(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = "/local/storage/shared/HDDatasets/ModelNet40/a/train/a_1.off"
            b = "/local/storage/shared/HDDatasets/ModelNet40/a/train/a_2.off"
            log_index = root / "log_index.json"
            unique_summary = root / "unique_summary.json"
            log_index.write_text(json.dumps({"run_all_records": [_record(a, b)]}), encoding="utf-8")
            unique_summary.write_text(
                json.dumps(
                    {
                        "cases": [
                            {
                                "case_index": 0,
                                "case_name": "0000_a_1__a_2",
                                "members": [
                                    "ModelNet40/a/train/a_1.off",
                                    "ModelNet40/a/train/a_2.off",
                                ],
                                "case_matched": False,
                                "author_log": {"hd_result": 0.5},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            summary = module.build_summary(
                argparse.Namespace(
                    log_index=log_index,
                    unique_summary=unique_summary,
                    paper_log_repo=None,
                    goal_label="Goal5230",
                    tolerance=1e-6,
                )
            )

        self.assertFalse(summary["all_records_covered"])
        self.assertEqual(summary["unmatched_unique_pair_count"], 1)

    def test_script_remains_app_owned_not_core_modelnet_primitive(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8").lower()
        self.assertIn("modelnet40_record_coverage", source)
        for forbidden in ("rtdsl.modelnet", "rtdsl.xhd", "native_modelnet", "native_xhd"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
