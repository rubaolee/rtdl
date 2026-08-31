from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5791_audit_terminal_analysis_successor as audit


ROOT = Path(__file__).resolve().parents[1]
SUCCESSOR = (
    ROOT / "history/internal_docs/goal5791_formal_v4_analysis_successor_20260821"
)
RAW = (
    ROOT / "history/internal_docs/goal5791_formal_v4_terminal_20260821_extracted"
    / ".goal5791_formal_output_v4_20260821.goal5791_incomplete"
)
ARCHIVE = ROOT / "history/internal_docs/goal5791_formal_v4_terminal_20260821.tar.gz"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _write(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resign(value: dict[str, object], field: str) -> None:
    unsigned = dict(value)
    unsigned.pop(field, None)
    value[field] = audit._digest(unsigned)


class Goal5791TerminalAnalysisSuccessorTest(unittest.TestCase):
    def _audit(
        self, *, result: Path | None = None, evaluation: Path | None = None,
        recount: Path | None = None, archive: Path | None = None,
    ) -> dict[str, object]:
        return audit.audit(
            result_path=result or SUCCESSOR / "RESULT.json",
            evaluation_path=evaluation or SUCCESSOR / "EVALUATION.json",
            recount_path=recount or SUCCESSOR / "RECOUNT.json",
            terminal_archive=archive or ARCHIVE,
            raw_root=RAW,
        )

    def test_actual_terminal_successor_independently_rebuilds(self) -> None:
        value = self._audit()
        self.assertEqual(
            value["status"],
            "PASS__INDEPENDENT_EXACT_SCHEMA_FULL_TERMINAL_ARCHIVE_AND_RAW_STATISTICS_AUDIT",
        )
        self.assertEqual(value["worker_file_count"], 96)
        self.assertEqual(value["paper_clear_winning_row_count"], 0)

    def test_resigned_governance_and_nested_schema_attacks_are_rejected(self) -> None:
        for label, mutate in (
            (
                "authorization",
                lambda value: value["authorization"].__setitem__(
                    "authorizes_worker_rerun", True),
            ),
            (
                "controller",
                lambda value: value["controller_transaction"].__setitem__(
                    "controller_transaction_success", True),
            ),
            (
                "missing_authorization_key",
                lambda value: value["authorization"].pop(
                    "authorizes_new_pod"),
            ),
            (
                "registered_timing_count",
                lambda value: value["controller_transaction"].__setitem__(
                    "registered_worker_timing_count", 0),
            ),
            (
                "status",
                lambda value: value.__setitem__("status", "ATTACKER"),
            ),
            (
                "analysis_lineage",
                lambda value: value["analysis_source_lineage"].__setitem__(
                    "executed_evaluator_sha256", "0" * 64),
            ),
            (
                "claim_boundary",
                lambda value: value["claim_boundary"].__setitem__(
                    "compiler_fusion_performance_claim_allowed", True),
            ),
        ):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "RESULT.json"
                value = _load(SUCCESSOR / "RESULT.json")
                mutate(value)
                _resign(value, "analysis_successor_sha256")
                _write(path, value)
                with self.assertRaises(audit.Goal5791TerminalAuditError):
                    self._audit(result=path)

    def test_three_way_resigned_statistic_drift_is_rejected_from_raw(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evaluation = _load(SUCCESSOR / "EVALUATION.json")
            recount = _load(SUCCESSOR / "RECOUNT.json")
            result = _load(SUCCESSOR / "RESULT.json")
            for value in (evaluation, recount, result):
                value["rows"][0]["paired_ratio_median"] = 123.0
            _resign(evaluation, "evaluation_sha256")
            evaluation_path = root / "EVALUATION.json"
            _write(evaluation_path, evaluation)
            recount["primary_evaluation_file_sha256"] = _file_sha(evaluation_path)
            recount["primary_evaluation_sha256"] = evaluation["evaluation_sha256"]
            _resign(recount, "recount_sha256")
            recount_path = root / "RECOUNT.json"
            _write(recount_path, recount)
            result["primary_evaluation"] = {
                "file_sha256": _file_sha(evaluation_path),
                "evaluation_sha256": evaluation["evaluation_sha256"],
                "status": evaluation["status"],
            }
            result["independent_recount"] = {
                "file_sha256": _file_sha(recount_path),
                "recount_sha256": recount["recount_sha256"],
                "status": recount["status"],
                "primary_evaluation_file_sha256": _file_sha(evaluation_path),
                "primary_evaluation_sha256": evaluation["evaluation_sha256"],
            }
            _resign(result, "analysis_successor_sha256")
            result_path = root / "RESULT.json"
            _write(result_path, result)
            with self.assertRaises(audit.Goal5791TerminalAuditError):
                self._audit(
                    result=result_path,
                    evaluation=evaluation_path,
                    recount=recount_path,
                )

    def test_wrong_terminal_archive_is_rejected(self) -> None:
        wrong = ROOT / "history/internal_docs/goal5791_portable_source_v26_20260820.tar.gz"
        with self.assertRaisesRegex(
            audit.Goal5791TerminalAuditError, "terminal archive SHA drifted",
        ):
            self._audit(archive=wrong)


if __name__ == "__main__":
    unittest.main()
