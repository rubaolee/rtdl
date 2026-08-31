from __future__ import annotations

import ast
import base64
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import unittest

from scripts import goal5793_x2_offline_core as core


ROOT = Path(__file__).resolve().parents[1]


def _utc(offset_seconds: float) -> str:
    value = datetime(2026, 8, 22, tzinfo=timezone.utc) + timedelta(seconds=offset_seconds)
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"


def _attempt(
    body: bytes,
    *,
    attempt: int = 1,
    delay: int = 0,
    status: int | None = 200,
    error: str | None = None,
    start_offset_seconds: float = 0,
) -> dict[str, object]:
    return {
        "attempt": attempt,
        "scheduled_delay_seconds": delay,
        "request_url": core.OPENALEX_ENDPOINT,
        "request_headers": [],
        "request_started_at_utc": _utc(start_offset_seconds),
        "status": status,
        "response_headers": [],
        "response_received_at_utc": _utc(start_offset_seconds + 0.1),
        "body_base64": base64.b64encode(body).decode("ascii"),
        "error": error,
    }


def _empty_transcript() -> dict[str, object]:
    queries: list[dict[str, object]] = []
    query_index = 0
    for provider in core.PROVIDER_ORDER:
        for term in core.TERMS:
            if provider == "OpenAlex Works API":
                body = json.dumps({"meta": {"next_cursor": None}, "results": []}, separators=(",", ":")).encode()
                params = core._openalex_params(term, "*")
            else:
                body = (
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<feed xmlns="http://www.w3.org/2005/Atom" '
                    'xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">'
                    '<opensearch:totalResults>0</opensearch:totalResults></feed>'
                ).encode()
                params = core._arxiv_params(term, 0)
            attempt = _attempt(body, start_offset_seconds=query_index * 10)
            attempt["request_url"] = core.OPENALEX_ENDPOINT if provider == "OpenAlex Works API" else core.ARXIV_ENDPOINT
            queries.append(
                {
                    "provider": provider,
                    "term": term,
                    "request_lineages": [{"request_sequence": 0, "params": params, "attempts": [attempt]}],
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


def _pulse(*, chain: int, index: int, timestamp: str, uri: str, output: str, previous: tuple[str, str] | None = None) -> dict[str, object]:
    values = [] if previous is None else [{"uri": previous[0], "type": "previous", "value": previous[1]}]
    return {
        "pulse": {
            "uri": uri,
            "version": "2.0",
            "cipherSuite": 0,
            "period": 60000,
            "certificateId": "1" * 128,
            "chainIndex": chain,
            "pulseIndex": index,
            "timeStamp": timestamp,
            "localRandomValue": "2" * 128,
            "external": {"sourceId": "3" * 128, "statusCode": 0, "value": "4" * 128},
            "listValues": values,
            "precommitmentValue": "5" * 128,
            "statusCode": 0,
            "signatureValue": "AA==",
            "outputValue": output,
        }
    }


def _vector(**overrides: str) -> dict[str, str]:
    base = {
        "geometry_family": "BUILTIN_TRIANGLE",
        "primitive_type": "TRIANGLE",
        "ray_construction": "ORIGIN_DIRECTION",
        "hit_policy": "CLOSEST_HIT_OR_MISS",
        "multiplicity": "ZERO_OR_ONE",
        "boundary_convention": "CLOSED",
        "tie_break": "MIN_PRIMITIVE_ID",
        "numeric_domain": "BINARY32_PINNED_GEOMETRY",
        "overflow_domain": "FAIL_CLOSED_STATUS_BEFORE_OUTPUT",
        "decode": "PER_QUERY_VALUE",
        "continuation": "SINGLE_TRACE",
        "composition": "INDEPENDENT_PER_QUERY",
        "ownership_epoch": "STATIC_IMMUTABLE",
    }
    base.update(overrides)
    return base


def _science_row(candidate_id: str, vector: dict[str, str], *, expected: str, risks: dict[str, bool], family: str) -> dict[str, object]:
    return {
        "schema": core.SCHEMA_SCIENCE_ROW,
        "candidate_id": candidate_id,
        "canonical_work_identity": "doi:10.1000/" + candidate_id.lower(),
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


class Goal5793X2OfflineCoreTest(unittest.TestCase):
    def test_01_module_has_no_network_client_imports(self) -> None:
        tree = ast.parse((ROOT / "scripts/goal5793_x2_offline_core.py").read_text(encoding="utf-8"))
        forbidden = {"socket", "requests", "urllib", "httpx", "aiohttp", "ftplib", "paramiko"}
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertFalse(imported & forbidden)

    def test_02_full_22_query_zero_result_transcript(self) -> None:
        result = core.validate_offline_transcript(_empty_transcript())
        self.assertEqual(result["query_count"], 22)
        self.assertEqual(result["raw_node_count"], 0)
        self.assertEqual(result["network_call_count"], 0)

    def test_03_query_order_and_retry_schedule_fail_closed(self) -> None:
        transcript = _empty_transcript()
        transcript["queries"][0], transcript["queries"][1] = transcript["queries"][1], transcript["queries"][0]
        with self.assertRaisesRegex(core.X2Error, "GLOBAL_QUERY_SCHEDULE_MISMATCH"):
            core.validate_offline_transcript(transcript)
        transcript = _empty_transcript()
        transcript["queries"][0]["request_lineages"][0]["attempts"][0]["scheduled_delay_seconds"] = 3
        with self.assertRaisesRegex(core.X2Error, "TRANSCRIPT_RETRY_SCHEDULE_DRIFT"):
            core.validate_offline_transcript(transcript)

    def test_04_normalization_and_fallback_are_stable(self) -> None:
        self.assertEqual(core.normalize_doi("https://doi.org/10.1145/ABC"), "10.1145/abc")
        self.assertEqual(core.normalize_arxiv("https://arxiv.org/abs/2501.01234v3"), "2501.01234")
        self.assertEqual(core.normalize_openalex("https://openalex.org/w123"), "W123")
        a = core.fallback_sha256("{Ray}--Tracing & Systems", "Smith, Ada", 2025)
        b = core.fallback_sha256("Ray Tracing and Systems", "Ada Smith", "2025")
        self.assertEqual(a, b)

    def test_05_strong_transitive_dedup_and_conflict(self) -> None:
        base = {
            "term": "OptiX",
            "query_index": 0,
            "page_index": 0,
            "ordinal": 0,
            "record_sha256": "0" * 64,
            "title": "same work",
            "first_author": "smith",
            "year": 2024,
            "fallback_sha256": core.fallback_sha256("same work", "smith", 2024),
            "raw_title": "Same Work",
            "raw_first_author": "Smith",
        }
        one = dict(base, node_id="n1", provider="OpenAlex Works API", doi="10.1/a", arxiv=None, openalex="W1")
        two = dict(base, node_id="n2", provider="arXiv API", doi="10.1/a", arxiv="2401.00001", openalex=None)
        components = core.build_identity_components([one, two], [])
        self.assertEqual(len(components), 1)
        self.assertEqual(components[0]["component_id"], "doi:10.1/a")
        self.assertFalse(components[0]["identity_conflict"])
        bad = dict(base, node_id="n3", provider="OpenAlex Works API", doi="10.1/b", arxiv="2401.00001", openalex="W2")
        components = core.build_identity_components([one, two, bad], [])
        self.assertTrue(components[0]["identity_conflict"])
        self.assertEqual(components[0]["identity_disposition"], "IDENTITY_CONFLICT__SELECTION_INELIGIBLE")

    def test_06_all_186_exposure_rows_and_conservative_match(self) -> None:
        registry = json.loads((ROOT / "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json").read_text(encoding="utf-8"))
        exposure = core.build_exposure_alias_rows(registry)
        self.assertEqual(len(exposure), 186)
        self.assertEqual(sum(row["strong_identifier_present"] for row in exposure), 7)
        ref = exposure[0]
        year = ref["year"] or 2020
        node = {
            "node_id": "n",
            "provider": "OpenAlex Works API",
            "term": "OptiX",
            "query_index": 0,
            "page_index": 0,
            "ordinal": 0,
            "record_sha256": "0" * 64,
            "doi": None,
            "arxiv": None,
            "openalex": "W999",
            "title": ref["title"],
            "first_author": ref["first_author"],
            "year": year,
            "fallback_sha256": core.fallback_sha256(ref["title"], ref["first_author"], year),
            "raw_title": ref["title"],
            "raw_first_author": ref["first_author"],
        }
        component = core.build_identity_components([node], exposure)[0]
        self.assertEqual(component["identity_disposition"], "PREEXISTING_PROJECT_EXPOSURE__SELECTION_INELIGIBLE")
        self.assertTrue(component["exposure_matches"])

    def test_07_science_roles_and_triplet_enumerator(self) -> None:
        positive = _vector()
        no_risk = {key: False for key in core.RISK_FLAGS}
        a = _science_row(
            "A",
            _vector(ray_construction="FINITE_SEGMENT"),
            expected="COMPATIBLE",
            risks=no_risk,
            family="family_a",
        )
        b = _science_row(
            "B",
            _vector(geometry_family="CUSTOM_AABB", primitive_type="CUSTOM_AABB_BOX_OR_INTERVAL"),
            expected="UNKNOWN",
            risks=no_risk,
            family="family_b",
        )
        risks = dict(no_risk, continuation=True)
        c = _science_row("C", _vector(), expected="UNKNOWN", risks=risks, family="family_c")
        rows = [core.validate_science_row(row, [positive]) for row in (a, b, c)]
        self.assertTrue(rows[0]["role_A"])
        self.assertTrue(rows[1]["role_B"])
        self.assertTrue(rows[2]["role_C"])
        self.assertIn(["A", "B", "C"], core.enumerate_ordered_triplets(rows))

    def test_08_unmapped_value_and_outcome_leakage_fail_closed(self) -> None:
        row = _science_row(
            "A",
            _vector(geometry_family="NEW_FAMILY"),
            expected="COMPATIBLE",
            risks={key: False for key in core.RISK_FLAGS},
            family="family_a",
        )
        with self.assertRaisesRegex(core.X2Error, "SCIENCE_ROW_UNMAPPED_STRUCTURAL_VALUE"):
            core.validate_science_row(row, [_vector()])
        row = _science_row(
            "A", _vector(), expected="COMPATIBLE", risks={key: False for key in core.RISK_FLAGS}, family="family_a"
        )
        row["actual_exam_outcome"] = "GOOD"
        with self.assertRaisesRegex(core.X2Error, "PRESELECTION_OUTCOME_LEAKAGE"):
            core.validate_science_row(row, [_vector()])

    def test_09_selection_known_answer_and_boundary(self) -> None:
        protocol = json.loads((ROOT / core.S0_PROTOCOL_PATH).read_text(encoding="utf-8"))
        kat = protocol["deferred_entropy"]["known_answer_test"]
        inputs = dict(kat["inputs"])
        frame = core.build_selection_frame(inputs)
        self.assertEqual(len(frame), 1345)
        self.assertEqual(core.sha256_bytes(frame), "a5904e12a9795bdc984b73095cc38cc670328fbb074a8db5e736c1fff0d4d92e")
        base = dict(inputs)
        base.pop("counter")
        result = core.select_index(base, 7)
        self.assertEqual(result["selected_index"], 2)
        boundary = core.select_index(
            base,
            7,
            synthetic_digest_sequence=["f" * 62 + "fe", "0" * 63 + "a"],
        )
        self.assertEqual([item["accepted"] for item in boundary["evaluations"]], [False, True])
        self.assertEqual(boundary["selected_index"], 3)

    def test_10_selection_cardinality_zero_and_one(self) -> None:
        protocol = json.loads((ROOT / core.S0_PROTOCOL_PATH).read_text(encoding="utf-8"))
        base = dict(protocol["deferred_entropy"]["known_answer_test"]["inputs"])
        base.pop("counter")
        zero = core.select_index(base, 0)
        self.assertEqual(zero["hash_evaluation_count"], 0)
        self.assertEqual(zero["selected_index"], None)
        one = core.select_index({**base, "ordered_triplet_count": 1}, 1)
        self.assertEqual(one["hash_evaluation_count"], 1)
        self.assertEqual(one["selected_index"], 0)

    def test_11_exact_anchor_and_target_timestamp_checks(self) -> None:
        previous = _pulse(
            chain=2,
            index=100,
            timestamp="2027-01-01T00:00:00.000Z",
            uri="https://beacon.nist.gov/beacon/2.0/pulse/2/100",
            output="6" * 128,
        )
        anchor = _pulse(
            chain=2,
            index=101,
            timestamp="2027-01-01T00:01:00.000Z",
            uri="https://beacon.nist.gov/beacon/2.0/pulse/2/101",
            output="7" * 128,
            previous=(previous["pulse"]["uri"], previous["pulse"]["outputValue"]),
        )
        not_before = core.parse_timestamp_ms("2027-01-01T00:00:30.000Z")
        verified = core.validate_anchor_first_next(anchor, previous, not_before)
        target = _pulse(
            chain=2,
            index=1541,
            timestamp="2027-01-02T00:01:00.000Z",
            uri="https://beacon.nist.gov/beacon/2.0/pulse/2/1541",
            output="8" * 128,
        )
        target_ms = core.parse_timestamp_ms("2027-01-02T00:01:00.000Z")
        self.assertEqual(core.validate_exact_target(target, verified["anchor"], target_ms)["pulse_index"], 1541)
        wrong = copy.deepcopy(target)
        wrong["pulse"]["timeStamp"] = "2027-01-02T00:02:00.000Z"
        with self.assertRaisesRegex(core.X2Error, "NIST_NEXT_CLOSEST_TARGET_REJECTED"):
            core.validate_exact_target(wrong, verified["anchor"], target_ms)

    def test_12_openalex_retry_and_cursor_pagination_are_exact(self) -> None:
        transcript = _empty_transcript()
        work = {
            "id": "https://openalex.org/W123", "doi": "https://doi.org/10.1000/openalex",
            "ids": {"openalex": "https://openalex.org/W123"}, "title": "Offline Cursor Work",
            "authorships": [{"author": {"display_name": "Ada Smith"}}], "publication_year": 2025,
        }
        first = core.canonical_bytes({"meta": {"next_cursor": "cursor-two"}, "results": [work]})
        second = core.canonical_bytes({"meta": {"next_cursor": None}, "results": []})
        transcript["queries"][0]["request_lineages"] = [
            {
                "request_sequence": 0, "params": core._openalex_params(core.TERMS[0], "*"),
                "attempts": [
                    _attempt(b"temporary", status=500, start_offset_seconds=0),
                    _attempt(first, attempt=2, delay=3, start_offset_seconds=3.1),
                ],
            },
            {"request_sequence": 1, "params": core._openalex_params(core.TERMS[0], "cursor-two"), "attempts": [_attempt(second, start_offset_seconds=4)]},
        ]
        result = core.validate_offline_transcript(transcript)
        self.assertEqual(result["raw_node_count"], 1)
        self.assertEqual(len(result["response_evidence"]), 23)
        self.assertEqual(len(result["response_evidence"][0]["attempts"]), 2)
        broken = copy.deepcopy(transcript)
        broken["queries"][0]["request_lineages"] = broken["queries"][0]["request_lineages"][:1]
        with self.assertRaisesRegex(core.X2Error, "OPENALEX_INCOMPLETE_PAGINATION"):
            core.validate_offline_transcript(broken)

    def test_13_arxiv_pagination_and_total_drift_fail_closed(self) -> None:
        transcript = _empty_transcript()
        def feed(total: int, identifier: str, title: str) -> bytes:
            return (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">'
                f'<opensearch:totalResults>{total}</opensearch:totalResults>'
                f'<entry><id>https://arxiv.org/abs/{identifier}</id><title>{title}</title>'
                '<published>2025-01-01T00:00:00Z</published><author><name>Ada Smith</name></author></entry></feed>'
            ).encode()
        query = len(core.TERMS)
        transcript["queries"][query]["request_lineages"] = [
            {"request_sequence": 0, "params": core._arxiv_params(core.TERMS[0], 0), "attempts": [dict(_attempt(feed(2, "2501.00001", "First Work"), start_offset_seconds=110), request_url=core.ARXIV_ENDPOINT)]},
            {"request_sequence": 1, "params": core._arxiv_params(core.TERMS[0], 1), "attempts": [dict(_attempt(feed(2, "2501.00002", "Second Work"), start_offset_seconds=113.1), request_url=core.ARXIV_ENDPOINT)]},
        ]
        result = core.validate_offline_transcript(transcript)
        self.assertEqual(result["raw_node_count"], 2)
        broken = copy.deepcopy(transcript)
        body = feed(3, "2501.00002", "Second Work")
        broken["queries"][query]["request_lineages"][1]["attempts"] = [dict(_attempt(body, start_offset_seconds=113.1), request_url=core.ARXIV_ENDPOINT)]
        with self.assertRaisesRegex(core.X2Error, "ARXIV_TOTAL_RESULTS_CHANGED"):
            core.validate_offline_transcript(broken)


if __name__ == "__main__":
    unittest.main()
