from __future__ import annotations

from copy import deepcopy
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import unittest

from scripts import goal5789_a2_audit_postreview_repair_packet as auditor
from scripts import goal5789_a2_build_postreview_repair_packet as builder


ROOT = Path(__file__).resolve().parents[1]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _members(archive_bytes: bytes) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    marker = builder.PREFIX + "/"
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        for member in archive.getmembers():
            handle = archive.extractfile(member)
            assert handle is not None
            assert member.name.startswith(marker)
            result[member.name[len(marker) :]] = handle.read()
    return result


def _raw_packet(
    members: list[tuple[str, bytes]],
    *,
    first_uname: str = "",
    member_pax: bool = False,
    global_pax: bool = False,
) -> bytes:
    raw = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as zipped:
        archive_format = tarfile.PAX_FORMAT if member_pax or global_pax else tarfile.GNU_FORMAT
        options: dict[str, object] = {"format": archive_format}
        if global_pax:
            options["pax_headers"] = {"comment": "EVIL_GLOBAL_PAX"}
        with tarfile.open(fileobj=zipped, mode="w", **options) as archive:
            for index, (relative, data) in enumerate(members):
                info = tarfile.TarInfo(f"{builder.PREFIX}/{relative}")
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o444
                info.uid = 0
                info.gid = 0
                info.uname = first_uname if index == 0 else ""
                info.gname = ""
                if member_pax and index == 0:
                    info.pax_headers = {"comment": "EVIL_MEMBER_PAX"}
                archive.addfile(info, io.BytesIO(data))
    return raw.getvalue()


class Goal5789A2PostreviewRepairPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = (
            b"# Goal5789-A2 postreview packet test fixture\n\n"
            b"This is not a formal result or packet.\n"
        )
        cls.result = builder._fixture_result(cls.report)
        cls.result_bytes = builder._pretty(cls.result)
        cls.archive, cls.manifest_bytes, cls.manifest = builder.build_packet(
            result_bytes=cls.result_bytes,
            report_bytes=cls.report,
            fixture_mode=True,
        )
        cls.payloads = _members(cls.archive)
        cls.audit = auditor.audit(
            cls.archive,
            cls.archive,
            cls.manifest_bytes,
            fixture_mode=True,
        )

    def test_deterministic_137_payload_packet_and_exact_accounting(self) -> None:
        archive_2, manifest_2, parsed_2 = builder.build_packet(
            result_bytes=self.result_bytes,
            report_bytes=self.report,
            fixture_mode=True,
        )
        self.assertEqual(archive_2, self.archive)
        self.assertEqual(manifest_2, self.manifest_bytes)
        self.assertEqual(parsed_2, self.manifest)
        self.assertEqual(self.manifest["payload_count"], 137)
        self.assertEqual(self.manifest["claim_boundary"]["predecessor_payload_count"], 120)
        self.assertEqual(self.manifest["claim_boundary"]["added_payload_count"], 17)
        self.assertEqual(
            self.manifest["historical_boundary"][
                "predecessor_packet_contained_rtxrmq_direct_repository_payload"
            ],
            False,
        )
        self.assertTrue(
            self.manifest["historical_boundary"][
                "predecessor_packet_carried_goal5783_source_archive"
            ]
        )
        self.assertEqual(
            self.manifest["claim_boundary"]["hostile_matrix_negative_mutation_count"],
            143,
        )
        self.assertEqual(
            self.manifest["claim_boundary"]["hostile_matrix_baseline_case_count"], 15
        )
        self.assertEqual(
            self.manifest["claim_boundary"]["hostile_matrix_tcb_passing_control_count"],
            1,
        )
        self.assertFalse(
            self.manifest["claim_boundary"][
                "hostile_matrix_all_cases_are_negative_or_rejections_claimed"
            ]
        )
        self.assertFalse(
            self.manifest["claim_boundary"]["hermetic_python_environment_claimed"]
        )
        self.assertEqual(self.archive[:10], auditor.CANONICAL_GZIP_HEADER)
        paths = {row["path"] for row in self.manifest["payloads"]}
        self.assertTrue(set(builder.DYNAMIC_TOOL_ADDITIONS).issubset(paths))
        self.assertEqual(
            _sha(self.payloads[builder.RTXRMQ_SOURCE_REL]), builder.RTXRMQ_SOURCE_SHA256
        )
        self.assertEqual(self.audit["manifest"]["payload_count"], 137)
        self.assertTrue(self.audit["checks"]["predecessor_120_payloads_byte_unchanged"])
        self.assertTrue(self.audit["checks"]["added_17_payloads_exact"])
        self.assertTrue(self.audit["checks"]["callback_authority_byte_identical"])
        self.assertTrue(self.audit["checks"]["callback_authority_pin_byte_identical"])

    def test_official_result_and_report_exact_contract_is_accepted_without_packet_write(self) -> None:
        result_bytes = (ROOT / builder.POSTREVIEW_RESULT_REL).read_bytes()
        report_bytes = (ROOT / builder.POSTREVIEW_REPORT_REL).read_bytes()
        parsed_builder = builder._validate_postreview_pair(
            result_bytes, report_bytes, fixture_mode=False
        )
        parsed_auditor = auditor._validate_result(
            result_bytes, report_bytes, fixture_mode=False
        )
        self.assertEqual(parsed_builder, parsed_auditor)
        self.assertEqual(
            parsed_builder["finding_absorption"]["p2_1_reason_oracle_specificity"][
                "negative_mutation_count"
            ],
            143,
        )
        self.assertEqual(
            parsed_builder["finding_absorption"]["p2_1_reason_oracle_specificity"][
                "baseline_count"
            ],
            15,
        )
        self.assertEqual(
            parsed_builder["finding_absorption"]["p2_1_reason_oracle_specificity"][
                "tcb_ceiling_passing_control_count"
            ],
            1,
        )

    def test_missing_direct_source_is_rejected(self) -> None:
        members = dict(self.payloads)
        manifest = members.pop("PACKET_MANIFEST.json")
        members.pop(builder.RTXRMQ_SOURCE_REL)
        attacked = builder._tar_bytes(members, manifest)
        with self.assertRaisesRegex(RuntimeError, "exact member set"):
            auditor.audit(attacked, attacked, self.manifest_bytes, fixture_mode=True)

    def test_extra_member_is_rejected(self) -> None:
        members = dict(self.payloads)
        manifest = members.pop("PACKET_MANIFEST.json")
        members["unexpected/extra.txt"] = b"extra"
        attacked = builder._tar_bytes(members, manifest)
        with self.assertRaisesRegex(RuntimeError, "exact member set"):
            auditor.audit(attacked, attacked, self.manifest_bytes, fixture_mode=True)

    def test_claim_and_authorization_escalation_are_rejected(self) -> None:
        payloads = dict(self.payloads)
        payloads.pop("PACKET_MANIFEST.json")
        for branch, key in (
            ("claim_boundary", "semantic_soundness_claimed"),
            ("authorization", "authorizes_goal5793_s0_authoring"),
        ):
            with self.subTest(branch=branch):
                manifest = deepcopy(self.manifest)
                manifest[branch][key] = True
                manifest_bytes = builder._pretty(manifest)
                attacked = builder._tar_bytes(payloads, manifest_bytes)
                with self.assertRaisesRegex(RuntimeError, "claims, or authorization"):
                    auditor.audit(attacked, attacked, manifest_bytes, fixture_mode=True)

    def test_alias_member_path_is_rejected(self) -> None:
        members = list(self.payloads.items())
        members.append(("scripts/../scripts/goal5789_alias.py", b"alias"))
        attacked = _raw_packet(members)
        with self.assertRaisesRegex(RuntimeError, "noncanonical packet path"):
            auditor.audit(attacked, attacked, self.manifest_bytes, fixture_mode=True)

    def test_noncanonical_uname_and_pax_metadata_are_rejected(self) -> None:
        members = list(self.payloads.items())
        attacks = (
            ("uname", {"first_uname": "EVIL"}, "metadata is noncanonical"),
            ("member_pax", {"member_pax": True}, "forbidden PAX metadata"),
            ("global_pax", {"global_pax": True}, "forbidden global PAX metadata"),
        )
        for label, options, expected in attacks:
            with self.subTest(label=label):
                attacked = _raw_packet(members, **options)
                with self.assertRaisesRegex(RuntimeError, expected):
                    auditor.audit(
                        attacked,
                        attacked,
                        self.manifest_bytes,
                        fixture_mode=True,
                    )

    def test_noncanonical_member_order_and_gzip_header_are_rejected(self) -> None:
        reversed_order = _raw_packet(list(reversed(list(self.payloads.items()))))
        with self.assertRaisesRegex(RuntimeError, "relative-path order"):
            auditor.audit(
                reversed_order,
                reversed_order,
                self.manifest_bytes,
                fixture_mode=True,
            )

        bad_header = bytearray(self.archive)
        bad_header[4] = 1  # gzip MTIME must be exactly zero.
        attacked = bytes(bad_header)
        with self.assertRaisesRegex(RuntimeError, "gzip header or flags"):
            auditor.audit(
                attacked,
                attacked,
                self.manifest_bytes,
                fixture_mode=True,
            )

    def test_stale_audit_is_rejected_before_replay(self) -> None:
        stored = auditor._pretty(self.audit)
        alternate_report = self.report + b"alternate valid fixture revision\n"
        alternate_result = builder._pretty(builder._fixture_result(alternate_report))
        archive, manifest_bytes, _ = builder.build_packet(
            result_bytes=alternate_result,
            report_bytes=alternate_report,
            fixture_mode=True,
        )
        with self.assertRaisesRegex(RuntimeError, "stale"):
            auditor.verify_stored_audit(
                stored,
                archive,
                archive,
                manifest_bytes,
                fixture_mode=True,
            )


if __name__ == "__main__":
    unittest.main()
