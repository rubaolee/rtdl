from __future__ import annotations

import base64
import copy
from datetime import datetime, timedelta, timezone
import io
import unittest
import zipfile

from scripts.goal5793_x2_offline_author_code import validate_author_code_fixture
from scripts.goal5793_x2_offline_core import X2Error


def _utc(seconds: float) -> str:
    value = datetime(2026, 8, 22, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return value.strftime("%Y-%m-%dT%H:%M:%S.") + f"{value.microsecond // 1000:03d}Z"


def _zip(files: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for path in sorted(files):
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0)); info.external_attr = 0o100444 << 16
            archive.writestr(info, files[path])
    return stream.getvalue()


ARCHIVE = _zip({"LICENSE": b"MIT\n", "src/main.py": b"print('ok')\n"})


def _plan(url: str = "https://github.com/example/project"):
    return {"source": "PDF_ANNOTATION", "url": url}


def _materialization(*, archive: bytes = ARCHIVE):
    return {
        "kind": "GIT_REPOSITORY", "archive_format": "zip", "license_path": "LICENSE", "requested_ref": "main",
        "resolved_commit": "1" * 40, "resolved_tree": "2" * 40, "lfs_objects": [], "submodules": [],
    }


def _lineage(url: str = "https://github.com/example/project", *, body: bytes = ARCHIVE, start: float = 0):
    return {
        "source": "PDF_ANNOTATION", "url": url,
        "attempts": [{
            "attempt": 1, "scheduled_delay_seconds": 0, "request_url": url, "request_headers": [],
            "request_started_at_utc": _utc(start), "status": 200, "response_headers": [],
            "response_received_at_utc": _utc(start + 0.1), "body_base64": base64.b64encode(body).decode("ascii"), "error": None,
        }],
        "materialization": _materialization(archive=body),
    }


def _fixture():
    return {
        "schema": "rtdl.goal5793.x2.offline_author_code_fixture.v1", "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
        "synthetic_fixture": True, "network_call_count": 0, "direct_link_plan": [_plan()], "link_lineages": [_lineage()],
    }


class Goal5793X2OfflineAuthorCodeTest(unittest.TestCase):
    def test_01_single_exact_repository_materializes_for_structure_only(self):
        result = validate_author_code_fixture(_fixture())
        self.assertEqual(result["status"], "AUTHOR_CODE_MATERIALIZED_FOR_STRUCTURAL_COMPARISON_ONLY")
        self.assertFalse(result["selection_eligibility_changed_by_author_code"])
        self.assertFalse(any(result["authorization"].values()))

    def test_02_every_link_is_required_and_multiple_identities_are_ambiguous(self):
        fixture = _fixture(); second_url = "https://gitlab.com/example/other"
        fixture["direct_link_plan"].append(_plan(second_url)); second = _lineage(second_url, start=1)
        second["materialization"]["resolved_commit"] = "3" * 40; fixture["link_lineages"].append(second)
        result = validate_author_code_fixture(fixture)
        self.assertEqual(result["status"], "NA_AMBIGUOUS_AUTHOR_CODE__NO_MANUAL_CHOICE")
        fixture["link_lineages"].pop()
        with self.assertRaisesRegex(X2Error, "AUTHOR_CODE_ALL_DIRECT_LINKS_NOT_ATTEMPTED"):
            validate_author_code_fixture(fixture)

    def test_03_lfs_and_submodule_gaps_are_not_hidden(self):
        pointer = b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"a" * 64 + b"\nsize 12\n"
        archive = _zip({"LICENSE": b"MIT\n", "large.bin": pointer})
        fixture = _fixture(); fixture["link_lineages"][0] = _lineage(body=archive)
        fixture["link_lineages"][0]["materialization"]["lfs_objects"] = [{"path": "large.bin", "oid_sha256": "a" * 64, "bytes": 12, "fetched": False, "object_sha256": None}]
        self.assertEqual(validate_author_code_fixture(fixture)["status"], "NA_INCOMPLETE_LFS_OR_SUBMODULE")
        fixture = _fixture(); fixture["link_lineages"][0]["materialization"]["submodules"] = [{"path": "vendor/sub", "commit": "4" * 40, "fetched": False}]
        self.assertEqual(validate_author_code_fixture(fixture)["status"], "NA_INCOMPLETE_LFS_OR_SUBMODULE")

    def test_04_unsafe_archive_member_rejects(self):
        bad = _zip({"../escape": b"x", "LICENSE": b"MIT\n"})
        fixture = _fixture(); fixture["link_lineages"][0] = _lineage(body=bad)
        with self.assertRaisesRegex(X2Error, "AUTHOR_CODE_ARCHIVE_PATH_INVALID"):
            validate_author_code_fixture(fixture)

    def test_05_success_does_not_allow_unrecorded_followup_attempts_or_manual_choice(self):
        fixture = _fixture(); extra = copy.deepcopy(fixture["link_lineages"][0]["attempts"][0]); extra["attempt"] = 2; extra["scheduled_delay_seconds"] = 3
        extra["request_started_at_utc"] = _utc(4); extra["response_received_at_utc"] = _utc(4.1)
        fixture["link_lineages"][0]["attempts"].append(extra)
        with self.assertRaisesRegex(X2Error, "AUTHOR_CODE_ATTEMPTS_AFTER_SUCCESS"):
            validate_author_code_fixture(fixture)


if __name__ == "__main__":
    unittest.main()
