import json
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2734_v2_5_same_pointer_zero_copy_boundary_audit_2026-05-30.md"

SAME_POINTER_ARTIFACTS = (
    ROOT / "docs/reports/goal2715_pod_artifacts/goal2715_raydb_native_device_hit_stream_pointer_pod_69_30_85_171_2026-05-30.json",
    ROOT / "docs/reports/goal2716_pod_artifacts/goal2716_hit_stream_carrier_execution_flag_smoke_pod_69_30_85_171_2026-05-30.json",
    ROOT / "docs/reports/goal2719_pod_artifacts/goal2719_native_output_proven_materialization_removed_smoke_pod_69_30_85_171_2026-05-30.json",
    ROOT / "docs/reports/goal2720_pod_artifacts/goal2720_raydb_prepared_device_hit_stream_smoke_pod_69_30_85_171_2026-05-30.json",
    ROOT / "docs/reports/goal2722_pod_artifacts/goal2722_raydb_prepared_device_hit_stream_large_pod_69_30_85_171_2026-05-30.json",
    ROOT / "docs/reports/goal2726_pod_artifacts/goal2726_raydb_v24_native_vs_v25_prepared_probe_pod_69_30_85_171_2026-05-30.json",
    ROOT / "docs/reports/goal2727_pod_artifacts/goal2727_raydb_prepared_grouped_vs_hit_stream_large_pod_69_30_85_171_2026-05-30.json",
    ROOT / "docs/reports/goal2731_pod_artifacts/goal2731_raydb_primitive_first_minmaxavg_gap_pod_69_30_85_171_2026-05-30.json",
)

PUBLIC_DOC_ROOTS = (
    ROOT / "docs",
    ROOT / "docs" / "tutorials",
    ROOT / "docs" / "learn",
    ROOT / "docs" / "rtdl",
    ROOT / "docs" / "features",
)

EXCLUDED_PUBLIC_DOC_PARTS = {
    "reports",
    "reviews",
    "handoff",
    "history",
    "audit",
    "release_reports",
    "research",
}

FORBIDDEN_PUBLIC_ZERO_COPY_CLAIM_FRAGMENTS = (
    '"true_zero_copy_authorized": true',
    "true_zero_copy_authorized: true",
    "true zero-copy is authorized",
    "true-zero-copy claim authorized",
    "public true-zero-copy claim authorized",
)


def _load_artifact(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _same_pointer_case(case: dict[str, Any]) -> bool:
    execution = case.get("torch_carrier_execution")
    if not isinstance(execution, dict):
        execution = {}
    return (
        case.get("torch_carrier_same_pointer_evidence_observed") is True
        or execution.get("same_pointer_evidence_observed") is True
    )


def _walk(value: Any) -> Any:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _public_markdown_files() -> list[Path]:
    files: set[Path] = set()
    for root in PUBLIC_DOC_ROOTS:
        if not root.exists():
            continue
        candidates = root.glob("*.md") if root == ROOT / "docs" else root.rglob("*.md")
        for path in candidates:
            relative_parts = set(path.relative_to(ROOT / "docs").parts)
            if relative_parts.isdisjoint(EXCLUDED_PUBLIC_DOC_PARTS):
                files.add(path)
    return sorted(files)


class Goal2734V25SamePointerZeroCopyBoundaryAuditTest(unittest.TestCase):
    def test_same_pointer_artifacts_never_authorize_true_zero_copy(self) -> None:
        same_pointer_cases = 0

        for artifact in SAME_POINTER_ARTIFACTS:
            payload = _load_artifact(artifact)
            self.assertEqual(payload.get("status"), "ok", artifact)
            if "no_public_speedup_claim" in payload:
                self.assertTrue(payload["no_public_speedup_claim"], artifact)

            for case in payload.get("cases", []):
                if not _same_pointer_case(case):
                    continue
                same_pointer_cases += 1
                execution = case.get("torch_carrier_execution")
                if not isinstance(execution, dict):
                    execution = {}
                self.assertFalse(case.get("true_zero_copy_authorized"), artifact)
                if "true_zero_copy_authorized" in execution:
                    self.assertFalse(execution["true_zero_copy_authorized"], artifact)

        self.assertEqual(same_pointer_cases, 47)

    def test_zero_copy_candidate_labels_are_not_authorization(self) -> None:
        candidate_count = 0
        candidate_case_count = 0

        for artifact in SAME_POINTER_ARTIFACTS:
            payload = _load_artifact(artifact)
            for case in payload.get("cases", []):
                adapter = case.get("torch_carrier_adapter")
                if not isinstance(adapter, dict):
                    continue
                columns = adapter.get("columns", [])
                if not isinstance(columns, list):
                    continue
                if any(isinstance(column, dict) and column.get("zero_copy_candidate") is True for column in columns):
                    candidate_case_count += 1
                    self.assertFalse(adapter.get("true_zero_copy_authorized"), artifact)
                    self.assertFalse(case.get("true_zero_copy_authorized"), artifact)
                    execution = case.get("torch_carrier_execution")
                    if isinstance(execution, dict) and "true_zero_copy_authorized" in execution:
                        self.assertFalse(execution["true_zero_copy_authorized"], artifact)
            for node in _walk(payload):
                if node.get("zero_copy_candidate") is True:
                    candidate_count += 1
                if "true_zero_copy_authorized" in node:
                    self.assertFalse(node["true_zero_copy_authorized"], artifact)

        self.assertGreater(candidate_count, 0)
        self.assertGreater(candidate_case_count, 0)

    def test_public_docs_do_not_authorize_true_zero_copy(self) -> None:
        offenders: list[str] = []
        public_docs = _public_markdown_files()
        self.assertGreater(len(public_docs), 0)

        for path in public_docs:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for fragment in FORBIDDEN_PUBLIC_ZERO_COPY_CLAIM_FRAGMENTS:
                if fragment in text:
                    offenders.append(f"{path.relative_to(ROOT)} contains {fragment}")

        self.assertEqual(offenders, [])

    def test_report_records_same_pointer_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Same-Pointer / Zero-Copy Boundary Audit", text)
        self.assertIn("47 cases", text)
        self.assertIn("not prove a complete public true-zero-copy contract", text)
        self.assertIn("Public true-zero-copy wording remains blocked", text)


if __name__ == "__main__":
    unittest.main()
