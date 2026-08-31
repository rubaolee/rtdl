from __future__ import annotations

import ast
import base64
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5793_x2_offline_core as core
from scripts import goal5793_x2_offline_harvester as harvester
from scripts import goal5793_x2_preentropy_enumerator as enumerator


ROOT = Path(__file__).resolve().parents[1]


def _utc(offset_seconds: float) -> str:
    value = datetime(2026, 8, 22, tzinfo=timezone.utc) + timedelta(seconds=offset_seconds)
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"


def _success(body: bytes, *, provider: str, offset_seconds: float) -> dict[str, object]:
    return {
        "attempt": 1,
        "scheduled_delay_seconds": 0,
        "request_url": core.OPENALEX_ENDPOINT if provider == "OpenAlex Works API" else core.ARXIV_ENDPOINT,
        "request_headers": [],
        "request_started_at_utc": _utc(offset_seconds),
        "status": 200,
        "response_headers": [],
        "response_received_at_utc": _utc(offset_seconds + 0.1),
        "body_base64": base64.b64encode(body).decode("ascii"),
        "error": None,
    }


def _transcript_with_one_work() -> dict[str, object]:
    queries: list[dict[str, object]] = []
    query_index = 0
    for provider in core.PROVIDER_ORDER:
        for term in core.TERMS:
            if provider == "OpenAlex Works API":
                results = []
                if term == "ray tracing core":
                    results = [
                        {
                            "id": "https://openalex.org/W999999",
                            "doi": "https://doi.org/10.9999/x2.synthetic",
                            "ids": {"openalex": "https://openalex.org/W999999"},
                            "title": "Synthetic Ray Core Work",
                            "authorships": [{"author": {"display_name": "Ada Smith"}}],
                            "publication_year": 2025,
                        }
                    ]
                body = core.canonical_bytes({"meta": {"next_cursor": None}, "results": results})
                params = core._openalex_params(term, "*")
            else:
                body = (
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<feed xmlns="http://www.w3.org/2005/Atom" '
                    'xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">'
                    '<opensearch:totalResults>0</opensearch:totalResults></feed>'
                ).encode()
                params = core._arxiv_params(term, 0)
            queries.append(
                {
                    "provider": provider,
                    "term": term,
                    "request_lineages": [{"request_sequence": 0, "params": params, "attempts": [_success(body, provider=provider, offset_seconds=query_index * 10)]}],
                }
            )
            query_index += 1
    return {
        "schema": core.SCHEMA_TRANSCRIPT,
        "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
        "synthetic_fixture": True,
        "network_call_count": 0,
        "worker_count": 1,
        "concurrent_requests": False,
        "queries": queries,
    }


def _science(candidate: str, vector: dict[str, str], expected: str, family: str, *, risk: str | None = None) -> dict[str, object]:
    risks = {key: key == risk for key in core.RISK_FLAGS}
    return {
        "schema": core.SCHEMA_SCIENCE_ROW,
        "candidate_id": candidate,
        "canonical_work_identity": f"doi:10.9999/{candidate.lower()}",
        "normalized_problem_family": family,
        "source_basis_exact": True,
        "oracle_exact": True,
        "stock_rt": True,
        "existing_registered_family": True,
        "expected_disposition": expected,
        "public_admit_compile_run_reachable": True,
        "no_core_change_predicted": True,
        "structural_vector": vector,
        "risk_flags": risks,
        "identity_stage_selection_eligible": True,
    }


class Goal5793X2HarvesterEnumeratorTest(unittest.TestCase):
    def test_01_harvester_dry_result_is_offline_and_sealed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "transcript.json"
            path.write_bytes(core.canonical_bytes(_transcript_with_one_work()) + b"\n")
            result = harvester.build_result(path)
        self.assertEqual(result["counts"]["query_count"], 22)
        self.assertEqual(result["counts"]["raw_node_count"], 1)
        self.assertEqual(result["counts"]["network_call_count"], 0)
        self.assertFalse(any(result["authorization"].values()))
        self.assertEqual(result["status"], "OFFLINE_SYNTHETIC_FIXTURE_HARVEST_VALIDATED__NOT_LIVE_SEARCH__NOT_X3_UNIVERSE")

    def test_02_harvester_rejects_live_marker(self) -> None:
        transcript = _transcript_with_one_work()
        transcript["network_call_count"] = 1
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "transcript.json"
            path.write_bytes(core.canonical_bytes(transcript) + b"\n")
            with self.assertRaisesRegex(core.X2Error, "LIVE_PROVIDER_CALL_FORBIDDEN_IN_X2"):
                harvester.build_result(path)

    def test_03_enumerator_projects_all_four_historical_vectors(self) -> None:
        vectors, authority = enumerator.load_positive_vectors()
        self.assertEqual(len(vectors), 4)
        self.assertEqual(authority["categorical_projection_count"], 4)
        self.assertEqual(len({core.sha256_bytes(core.canonical_bytes(v)) for v in vectors}), 4)

    def test_04_enumerator_fixture_builds_triplet_without_decision_calls(self) -> None:
        positives, _ = enumerator.load_positive_vectors()
        a_vector = dict(positives[0], ray_construction="FINITE_SEGMENT", tie_break="MIN_KEY_THEN_ID")
        b_vector = dict(positives[0], geometry_family="CUSTOM_AABB", primitive_type="CUSTOM_AABB_OTHER_EXACT_INTERSECTION")
        c_vector = dict(positives[0])
        fixture = {
            "schema": "rtdl.goal5793.x2.preentropy_science_fixture.v1",
            "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
            "synthetic_fixture": True,
            "network_call_count": 0,
            "examiner_invocation_count": 0,
            "candidate_implementation_count": 0,
            "rows": [
                _science("A", a_vector, "COMPATIBLE", "problem_a"),
                _science("B", b_vector, "UNKNOWN", "problem_b"),
                _science("C", c_vector, "UNKNOWN", "problem_c", risk="tie_boundary"),
            ],
        }
        result = enumerator.build_fixture_result(fixture)
        self.assertIn(["A", "B", "C"], result["ordered_triplets"])
        self.assertEqual(result["counts"]["examiner_invocations"], 0)
        self.assertEqual(result["counts"]["candidate_implementations"], 0)
        self.assertFalse(any(result["authorization"].values()))

    def test_05_expected_outcome_or_candidate_work_leakage_rejected(self) -> None:
        positives, _ = enumerator.load_positive_vectors()
        fixture = {
            "schema": "rtdl.goal5793.x2.preentropy_science_fixture.v1",
            "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
            "synthetic_fixture": True,
            "network_call_count": 0,
            "examiner_invocation_count": 1,
            "candidate_implementation_count": 0,
            "rows": [_science("A", dict(positives[0]), "COMPATIBLE", "problem_a")],
        }
        with self.assertRaisesRegex(core.X2Error, "PRESELECTION_OUTCOME_LEAKAGE"):
            enumerator.build_fixture_result(fixture)
        fixture["examiner_invocation_count"] = 0
        fixture["rows"][0]["checker_verdict"] = "COMPATIBLE"
        with self.assertRaisesRegex(core.X2Error, "PRESELECTION_OUTCOME_LEAKAGE"):
            enumerator.build_fixture_result(fixture)

    def test_06_taxonomy_mutation_changes_or_rejects_roles_not_silently(self) -> None:
        positives, _ = enumerator.load_positive_vectors()
        row = _science("A", dict(positives[0]), "COMPATIBLE", "problem_a")
        row["structural_vector"]["composition"] = "NEW_AFTER_SEARCH"
        with self.assertRaisesRegex(core.X2Error, "SCIENCE_ROW_UNMAPPED_STRUCTURAL_VALUE"):
            core.validate_science_row(row, positives)

    def test_07_no_network_imports_in_x2_wrappers(self) -> None:
        forbidden = {"socket", "requests", "urllib", "httpx", "aiohttp", "ftplib", "paramiko"}
        for relative in (
            "scripts/goal5793_x2_offline_harvester.py",
            "scripts/goal5793_x2_preentropy_enumerator.py",
        ):
            tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            imported: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            self.assertFalse(imported & forbidden, relative)

    def test_08_provider_record_order_cannot_change_component_identity(self) -> None:
        result = core.validate_offline_transcript(_transcript_with_one_work())
        exposure_registry = json.loads(
            (ROOT / "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json").read_text(encoding="utf-8")
        )
        exposure = core.build_exposure_alias_rows(exposure_registry)
        forward = core.build_identity_components(result["raw_nodes"], exposure)
        reverse = core.build_identity_components(list(reversed(result["raw_nodes"])), exposure)
        self.assertEqual(forward, reverse)


if __name__ == "__main__":
    unittest.main()
