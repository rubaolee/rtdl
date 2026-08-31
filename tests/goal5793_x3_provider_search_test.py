from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
import urllib.parse
from unittest import mock

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_offline_core as core
from scripts import goal5793_x3_build_provider_search_preaction as preaction
from scripts import goal5793_x3_capture_provider_search as capture
from scripts import goal5793_x3_provider_search_authority as authority


def _oa_work(term: str, suffix: str) -> dict:
    return {
        "id": f"https://openalex.org/W{suffix}",
        "doi": f"https://doi.org/10.9999/{suffix}",
        "title": f"Frozen {term} Work {suffix}",
        "publication_year": 2025,
        "authorships": [{"author": {"display_name": "Ada Tester"}}],
        "ids": {"openalex": f"https://openalex.org/W{suffix}"},
        "locations": [],
        "primary_location": None,
        "best_oa_location": None,
    }


def _arxiv_empty() -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom" '
        'xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">'
        '<opensearch:totalResults>0</opensearch:totalResults></feed>'
    ).encode()


class FakeClock:
    def __init__(self) -> None:
        self.value = datetime(2026, 8, 22, tzinfo=timezone.utc)

    def now(self) -> str:
        result = self.value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{self.value.microsecond // 1000:03d}Z"
        self.value += timedelta(milliseconds=100)
        return result

    def sleep(self, seconds: float) -> None:
        self.value += timedelta(seconds=seconds)


class FakeProvider:
    def __init__(self, *, fail_first: bool = False) -> None:
        self.calls: list[str] = []
        self.fail_first = fail_first

    def __call__(self, url, headers, timeout):  # noqa: ANN001
        self.calls.append(url)
        if self.fail_first and len(self.calls) == 1:
            return 503, [("Content-Type", "application/json")], b"retry", "HTTP_STATUS_503"
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        if parsed.scheme + "://" + parsed.netloc + parsed.path == core.OPENALEX_ENDPOINT:
            term = params["search"][0]
            cursor = params["cursor"][0]
            if term == core.TERMS[0] and cursor == "*":
                body = {"meta": {"next_cursor": "cursor-two"}, "results": [_oa_work(term, "1001")]}
            elif term == core.TERMS[0] and cursor == "cursor-two":
                body = {"meta": {"next_cursor": None}, "results": [_oa_work(term, "1002")]}
            else:
                suffix = str(2000 + core.TERMS.index(term))
                body = {"meta": {"next_cursor": None}, "results": [_oa_work(term, suffix)]}
            return 200, [("Content-Type", "application/json")], json.dumps(body, separators=(",", ":")).encode(), None
        return 200, [("Content-Type", "application/atom+xml")], _arxiv_empty(), None


def _build_transcript(*, fail_first: bool = False):
    clock = FakeClock()
    provider = FakeProvider(fail_first=fail_first)
    events: list[dict] = []
    transcript = capture.collect_search(
        fetch_fn=provider,
        sleep_fn=clock.sleep,
        now_fn=clock.now,
        event_sink=lambda event: events.append(dict(event)),
    )
    return transcript, provider, events


class Goal5793X3ProviderSearchTest(unittest.TestCase):
    def test_01_exact_22_query_schedule_and_multipage_capture(self) -> None:
        transcript, provider, events = _build_transcript()
        self.assertEqual(len(transcript["queries"]), 22)
        self.assertEqual([(q["provider"], q["term"]) for q in transcript["queries"]], [(p, t) for p in core.PROVIDER_ORDER for t in core.TERMS])
        self.assertEqual(len(transcript["queries"][0]["request_lineages"]), 2)
        self.assertEqual(transcript["network_call_count"], 23)
        self.assertEqual(len(provider.calls), 23)
        self.assertEqual(sum(event["event"] == "QUERY_COMPLETE" for event in events), 22)
        validated = authority.validate_live_transcript(transcript)
        self.assertEqual(validated["harvested"]["raw_node_count"], 12)
        self.assertEqual(len(validated["components"]), 12)

    def test_02_retry_schedule_and_global_arxiv_delay_validate(self) -> None:
        transcript, provider, _ = _build_transcript(fail_first=True)
        self.assertEqual(transcript["network_call_count"], 24)
        attempts = transcript["queries"][0]["request_lineages"][0]["attempts"]
        self.assertEqual([row["scheduled_delay_seconds"] for row in attempts], [0, 3])
        authority.validate_live_transcript(transcript)

    def test_03_origin_schedule_counts_and_seal_fail_closed(self) -> None:
        transcript, _, _ = _build_transcript()
        mutations = []
        a = copy.deepcopy(transcript); a["synthetic_fixture"] = True; mutations.append(a)
        b = copy.deepcopy(transcript); b["queries"].pop(); mutations.append(b)
        c = copy.deepcopy(transcript); c["network_call_count"] += 1; mutations.append(c)
        d = copy.deepcopy(transcript); d["candidate_work_count"] = 1; mutations.append(d)
        e = copy.deepcopy(transcript); e["queries"][0]["term"] = "convenient result"; mutations.append(e)
        for mutation in mutations:
            mutation["transcript_sha256"] = seal_document(mutation, seal_field="transcript_sha256", domain=authority.TRANSCRIPT_DOMAIN, version=1)
            with self.assertRaises((authority.X3SearchError, core.X2Error)):
                authority.validate_live_transcript(mutation)
        unsealed = copy.deepcopy(transcript); unsealed["queries"][0]["term"] = "drift"
        with self.assertRaisesRegex(authority.X3SearchError, "LIVE_TRANSCRIPT_SEAL_MISMATCH"):
            authority.validate_live_transcript(unsealed)

    def test_04_authority_has_no_science_selection_or_usability_escalation(self) -> None:
        transcript, _, _ = _build_transcript()
        with tempfile.TemporaryDirectory(prefix="goal5793_x3_authority_test_") as temp:
            path = Path(temp) / "transcript.json"
            from scripts.goal5793_x1_canonical import canonical_json_bytes
            path.write_bytes(canonical_json_bytes(transcript) + b"\n")
            # The temporary path is outside ROOT, so validate the content
            # directly; disk path binding is exercised after the real run.
            validated = authority.validate_live_transcript(transcript)
        self.assertFalse(validated["projection_boundary"]["live_origin_lost_or_relabelled"])
        self.assertTrue(validated["projection_boundary"]["reviewed_x2_parser_reuse_only"])
        self.assertFalse(any(transcript["authorization"].values()))

    def test_05_full_url_and_request_headers_are_frozen(self) -> None:
        params = core._openalex_params(core.TERMS[0], "*")
        url = capture._full_url(core.OPENALEX_ENDPOINT, params)
        self.assertIn("per-page=200", url)
        self.assertIn("cursor=%2A", url)
        self.assertIn("search=ray%20tracing%20core", url)
        self.assertEqual(capture.REQUEST_HEADERS["OpenAlex Works API"][0], ("Accept", "application/json"))
        self.assertEqual(capture.TIMEOUT_SECONDS, 120)

    def test_06_execute_once_writes_complete_transcript_and_durable_journal(self) -> None:
        clock = FakeClock(); provider = FakeProvider()
        with tempfile.TemporaryDirectory(prefix="goal5793_x3_execute_once_") as temp:
            root = Path(temp)
            preaction_path = root / "preaction.json"
            preaction_path.write_bytes(canonical_json_bytes(preaction.build_authority()) + b"\n")
            journal, transcript, failure = root / "journal.jsonl", root / "transcript.json", root / "failure.json"
            with mock.patch.object(capture, "_network_fetch", provider), mock.patch.object(capture, "_utc_now", clock.now), mock.patch.object(capture.time, "sleep", clock.sleep):
                result = capture.execute_once(preaction_path, journal, transcript, failure)
            self.assertEqual(result["status"], "COMPLETE")
            self.assertTrue(journal.is_file())
            self.assertTrue(transcript.is_file())
            self.assertFalse(failure.exists())
            events = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(events[0]["event"], "TRANSACTION_START")
            self.assertEqual(events[-1]["event"], "TRANSACTION_COMPLETE")
            self.assertEqual(sum(event["event"] == "HTTP_ATTEMPT" for event in events), 23)

    def test_07_terminal_failure_is_preserved_and_cannot_be_partial_success(self) -> None:
        clock = FakeClock()
        def always_fail(url, headers, timeout):  # noqa: ANN001
            return 503, [("Content-Type", "text/plain")], b"unavailable", "HTTP_STATUS_503"
        with tempfile.TemporaryDirectory(prefix="goal5793_x3_terminal_failure_") as temp:
            root = Path(temp)
            preaction_path = root / "preaction.json"
            preaction_path.write_bytes(canonical_json_bytes(preaction.build_authority()) + b"\n")
            journal, transcript, failure = root / "journal.jsonl", root / "transcript.json", root / "failure.json"
            with mock.patch.object(capture, "_network_fetch", always_fail), mock.patch.object(capture, "_utc_now", clock.now), mock.patch.object(capture.time, "sleep", clock.sleep):
                with self.assertRaisesRegex(authority.X3SearchError, "EXHAUSTED_RETRY"):
                    capture.execute_once(preaction_path, journal, transcript, failure)
            self.assertFalse(transcript.exists())
            self.assertTrue(failure.is_file())
            receipt = json.loads(failure.read_text(encoding="utf-8"))
            self.assertEqual(receipt["status"], "TERMINAL_INFRA_FAILURE__NO_PARTIAL_UNIVERSE__NO_RERUN")
            self.assertFalse(receipt["authorization"]["rerun"])
            self.assertEqual(sum(json.loads(line)["event"] == "HTTP_ATTEMPT" for line in journal.read_text(encoding="utf-8").splitlines()), 6)


if __name__ == "__main__":
    unittest.main()
