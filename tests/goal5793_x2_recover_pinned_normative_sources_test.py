from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5793_x2_recover_pinned_normative_sources as recovery


class _Headers:
    def __init__(self, rows=()): self._rows = list(rows)
    def items(self): return list(self._rows)


class _Response:
    def __init__(self, body: bytes): self.status = 200; self.headers = _Headers([("Content-Type", "application/octet-stream")]); self._body = body
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self, limit: int): return self._body[:limit]


class _Opener:
    def __init__(self, bodies): self.bodies = list(bodies); self.calls = []
    def open(self, request, timeout=60): self.calls.append((request.full_url, dict(request.header_items()), timeout)); return _Response(self.bodies.pop(0))


def _write_json(path: Path, value): path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")


def _authority(tool: Path):
    data = tool.read_bytes()
    value = {
        "schema": "rtdl.goal5793.x2.normative_source_recovery_work_authority.v2", "date": recovery.DATE,
        "status": "PREACTION_EXTERNAL_REVIEW_REQUIRED__NO_NETWORK_EXECUTION_AUTHORIZED",
        "exact_sources": list(recovery.SOURCES),
        "recovery_tool": {"path": tool.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()},
        "network_execution_authorized_before_returned_review_and_owner_closure": False,
        "work_authority_sha256": "",
    }
    value["work_authority_sha256"] = recovery._seal(value, "work_authority_sha256", recovery.AUTHORITY_DOMAIN)
    return value


def _closure(authority_path: Path, review_path: Path, tool: Path):
    value = {
        "schema": "rtdl.goal5793.x2.normative_source_recovery_owner_closure.v1", "date": recovery.DATE,
        "bindings": {"work_authority": recovery._identity(authority_path), "returned_review": recovery._identity(review_path), "recovery_tool": recovery._identity(tool)},
        "authorization": {"authorizes_exact_pinned_source_recovery": True, "live_search": False, "beacon": False, "entropy": False, "selection": False, "candidate_work": False, "gpu_ssh_pod": False, "timing": False},
        "closure_sha256": "",
    }
    value["closure_sha256"] = recovery._seal(value, "closure_sha256", recovery.CLOSURE_DOMAIN)
    return value


class Goal5793X2RecoverPinnedNormativeSourcesTest(unittest.TestCase):
    def _tree(self, root: Path):
        tool = Path(recovery.__file__).resolve(); authority_path = root / "authority.json"; review_path = root / "review.md"; closure_path = root / "closure.json"
        _write_json(authority_path, _authority(tool)); review_path.write_text("P0=0 / P1=0\n", encoding="utf-8", newline="\n"); _write_json(closure_path, _closure(authority_path, review_path, tool))
        return authority_path, review_path, closure_path

    def test_01_no_flag_cli_boundary_exists_and_validation_needs_review_closure(self):
        with tempfile.TemporaryDirectory() as temp:
            authority, review, closure = self._tree(Path(temp))
            recovery.validate_authorities(authority, review, closure)

    def test_02_exact_two_sources_create_once_with_no_search_or_beacon(self):
        bodies = [b"A" * recovery.SOURCES[0]["bytes"], b"B" * recovery.SOURCES[1]["bytes"]]
        patched = [dict(recovery.SOURCES[0], sha256=hashlib.sha256(bodies[0]).hexdigest()), dict(recovery.SOURCES[1], sha256=hashlib.sha256(bodies[1]).hexdigest())]
        original = recovery.SOURCES
        try:
            recovery.SOURCES = tuple(patched)
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp); authority, review, closure = self._tree(root); opener = _Opener(bodies.copy())
                result = recovery.recover_sources(authority, review, closure, root / "out", opener=opener, sleeper=lambda _: None, clock=lambda: datetime(2026, 8, 22, tzinfo=timezone.utc))
                self.assertEqual(len(opener.calls), 2); self.assertEqual(result["activity"]["provider_search_calls"], 0); self.assertEqual(result["activity"]["beacon_calls"], 0)
                with self.assertRaisesRegex(recovery.RecoveryError, "RECOVERY_CREATE_ONLY_TARGET_EXISTS_OR_PARENT_INVALID"):
                    recovery.recover_sources(authority, review, closure, root / "out", opener=_Opener(bodies), sleeper=lambda _: None)
        finally:
            recovery.SOURCES = original

    def test_03_wrong_hash_is_terminal_without_alternate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); authority, review, closure = self._tree(root); opener = _Opener([b"wrong"])
            with self.assertRaisesRegex(recovery.RecoveryError, "RECOVERY_SOURCE_DRIFT__NO_ALTERNATE_OR_RETRY"):
                recovery.recover_sources(authority, review, closure, root / "out", opener=opener, sleeper=lambda _: None)
            self.assertEqual(len(opener.calls), 1); self.assertFalse((root / "out").exists())

    def test_04_review_or_tool_binding_drift_rejects_before_network(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); authority, review, closure = self._tree(root); review.write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(recovery.RecoveryError, "RECOVERY_OWNER_CLOSURE_BINDING_MISMATCH"):
                recovery.recover_sources(authority, review, closure, root / "out", opener=_Opener([]), sleeper=lambda _: None)


if __name__ == "__main__":
    unittest.main()
