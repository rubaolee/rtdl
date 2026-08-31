from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import tarfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"
BUDGET_PATH = DOCS / "goal5791_pre_pod_conservative_runtime_budget_20260817.json"
AUDIT_PATH = DOCS / "goal5791_pre_pod_portable_base_and_bundle_audit_20260817.json"
G5784_RAW = DOCS / "goal5784_a3_v5_raw_preservation_20260815.tar.gz"
G5785_RAW = (
    DOCS
    / "goal5785_v6_rtx4000ada_final_result_20260816"
    / "GOAL5785_EVIDENCE.tar.gz"
)
A1_V4 = DOCS / "goal5790_a1_portable_source_v4_20260816.tar.gz"
V8 = DOCS / "goal5790_portable_source_v8_20260816.tar.gz"


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_member_name(name: str) -> bool:
    normalized = name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    return (
        bool(normalized)
        and not normalized.startswith("/")
        and not pure.is_absolute()
        and ".." not in pure.parts
        and "." not in pure.parts
    )


class Goal5791PrePodBaseBudgetAuditTest(unittest.TestCase):
    def test_budget_rebuilds_from_frozen_goal5784_and_goal5785_raw(self) -> None:
        budget = _load(BUDGET_PATH)
        authorities = {item["goal"]: item for item in budget["historical_raw_authorities"]}
        self.assertEqual(_sha256_file(G5784_RAW), authorities[5784]["sha256"])
        self.assertEqual(_sha256_file(G5785_RAW), authorities[5785]["sha256"])

        target_units = {
            "triangle__cit_patents__rt_2a1",
            "triangle__com_dblp__rt_2a1",
            "triangle__soc_livejournal1__rt_2a1",
        }
        grouped: dict[tuple[str, str], list[dict]] = {}
        goal5784_endpoints: list[float] = []
        worker_counts: dict[int, int] = {}

        sources = (
            (5784, G5784_RAW, "formal_a3_v5/workers/worker_"),
            (5785, G5785_RAW, "RAW/workers/"),
        )
        for goal, path, prefix in sources:
            count = 0
            with tarfile.open(path, "r:gz") as archive:
                for member in archive.getmembers():
                    if not (
                        member.isfile()
                        and member.name.startswith(prefix)
                        and member.name.endswith(".json")
                    ):
                        continue
                    payload = archive.extractfile(member).read()
                    record = json.loads(payload)
                    if not record.get("formal_worker"):
                        continue
                    count += 1
                    endpoint = sum(
                        float(row["registered_complete_endpoint_seconds"])
                        for row in record["rows"]
                    )
                    if goal == 5784:
                        goal5784_endpoints.append(endpoint)
                    if record["unit_id"] in target_units:
                        grouped.setdefault(
                            (record["unit_id"], record["lifecycle"]), []
                        ).append(
                            {
                                "value": endpoint,
                                "goal": goal,
                                "member": member.name,
                                "sha256": _sha256_bytes(payload),
                                "bytes": len(payload),
                                "method": record["method"],
                            }
                        )
            worker_counts[goal] = count

        self.assertEqual(worker_counts, {5784: 128, 5785: 464})
        self.assertEqual(len(goal5784_endpoints), 128)
        self.assertAlmostEqual(sum(goal5784_endpoints), 8189.453474088106, places=12)
        self.assertEqual(len(grouped), 6)
        self.assertTrue(all(len(values) == 32 for values in grouped.values()))

        frozen = {
            (item["unit_id"], item["lifecycle"]): item
            for item in budget["endpoint_bound_derivation"]["selected_scope_maxima"]
        }
        maxima: list[float] = []
        for key in sorted(grouped):
            observed = max(grouped[key], key=lambda item: item["value"])
            expected = frozen[key]
            self.assertEqual(observed["value"], expected["maximum_registered_endpoint_seconds"])
            self.assertEqual(observed["goal"], expected["source_goal"])
            self.assertEqual(observed["member"], expected["source_member"])
            self.assertEqual(observed["sha256"], expected["source_member_sha256"])
            self.assertEqual(observed["bytes"], expected["source_member_bytes"])
            self.assertEqual(observed["method"], expected["source_method"])
            maxima.append(observed["value"])

        derivation = budget["formal_budget_derivation"]
        endpoint_bound = sum(maxima) * 16
        overhead_per_worker = (10174.0 - sum(goal5784_endpoints)) / 128
        overhead_bound = overhead_per_worker * 96
        before_safety = endpoint_bound + overhead_bound
        formal = before_safety * 1.25
        total = formal + 3600.0
        self.assertAlmostEqual(endpoint_bound, derivation["registered_endpoint_bound_seconds"], places=12)
        self.assertAlmostEqual(overhead_per_worker, derivation["nonendpoint_overhead_seconds_per_worker"], places=12)
        self.assertAlmostEqual(overhead_bound, derivation["nonendpoint_overhead_bound_seconds"], places=12)
        self.assertAlmostEqual(before_safety, derivation["formal_before_safety_seconds"], places=12)
        self.assertAlmostEqual(formal, 16085.148858741304, places=12)
        self.assertAlmostEqual(total, 19685.148858741304, places=12)
        self.assertEqual(budget["frozen_budget"]["recommended_minimum_owner_window_hours"], 7.0)

    def test_selected_a1_v4_base_rehashes_and_manifest_recounts(self) -> None:
        audit = _load(AUDIT_PATH)
        selected = audit["selected_base"]
        self.assertEqual(_sha256_file(A1_V4), selected["archive"]["sha256"])
        manifest_name = selected["embedded_manifest"]["member"]
        dangerous_suffixes = (
            ".tar", ".tar.gz", ".tgz", ".zip", ".whl", ".egg", ".jar",
            ".7z", ".so", ".dll", ".dylib", ".exe", ".o", ".a",
            ".ptx", ".cubin", ".fatbin", ".pyc", ".pyo",
        )
        seen: set[str] = set()
        payloads: dict[str, bytes] = {}
        with tarfile.open(A1_V4, "r:gz") as archive:
            for member in archive.getmembers():
                self.assertTrue(member.isfile(), member.name)
                self.assertTrue(_safe_member_name(member.name), member.name)
                self.assertNotIn(member.name, seen)
                seen.add(member.name)
                payload = archive.extractfile(member).read()
                self.assertEqual(len(payload), member.size)
                payloads[member.name] = payload
                lower = member.name.lower()
                self.assertFalse(lower.endswith(dangerous_suffixes), member.name)
                self.assertFalse(payload.startswith(b"\x7fELF"), member.name)
                self.assertFalse(payload.startswith(b"MZ"), member.name)
                self.assertFalse(payload.startswith(b"PK\x03\x04"), member.name)
                self.assertFalse(payload.startswith(b"\x1f\x8b"), member.name)
                self.assertFalse(len(payload) > 262 and payload[257:262] == b"ustar", member.name)

        self.assertEqual(len(payloads), 730)
        manifest_payload = payloads.pop(manifest_name)
        self.assertEqual(_sha256_bytes(manifest_payload), selected["embedded_manifest"]["sha256"])
        manifest = json.loads(manifest_payload)
        self.assertEqual(manifest["file_count_excluding_this_manifest"], 729)
        self.assertEqual(len(manifest["files"]), 729)
        self.assertEqual(set(payloads), {item["path"] for item in manifest["files"]})
        for item in manifest["files"]:
            payload = payloads[item["path"]]
            self.assertEqual(len(payload), item["size_bytes"], item["path"])
            self.assertEqual(_sha256_bytes(payload), item["sha256"], item["path"])
        self.assertEqual(sum(len(payload) for payload in payloads.values()), 20207434)
        self.assertEqual(manifest["source_tree_sha256"], selected["source_tree_sha256"])

    def test_v8_nested_elf_rejection_reproduces(self) -> None:
        audit = _load(AUDIT_PATH)
        rejection = audit["v8_direct_base_rejection"]
        self.assertEqual(_sha256_file(V8), rejection["archive"]["sha256"])
        nested = rejection["nested_container"]
        with tarfile.open(V8, "r:gz") as archive:
            payload = archive.extractfile(nested["member"]).read()
        self.assertEqual(len(payload), nested["bytes"])
        self.assertEqual(_sha256_bytes(payload), nested["sha256"])
        expected = {item["path"]: item for item in nested["deep_members"]}
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            for path, item in expected.items():
                deep_payload = archive.extractfile(path).read()
                self.assertEqual(len(deep_payload), item["bytes"])
                self.assertEqual(_sha256_bytes(deep_payload), item["sha256"])
                if item["classification"] == "prebuilt_elf_native":
                    self.assertTrue(deep_payload.startswith(b"\x7fELF"))

    def test_all_authorizations_remain_false(self) -> None:
        budget = _load(BUDGET_PATH)
        audit = _load(AUDIT_PATH)
        self.assertTrue(budget["not_a_performance_result"])
        self.assertTrue(budget["not_execution_authority"])
        self.assertTrue(audit["not_a_performance_result"])
        self.assertTrue(audit["not_execution_authority"])
        self.assertTrue(all(value is False for value in budget["authorization"].values()))
        self.assertTrue(all(value is False for value in audit["authorization"].values()))
        self.assertFalse(budget["anti_outcome_adjustment"]["these_values_may_change_after_any_goal5791_target_timing"])


if __name__ == "__main__":
    unittest.main()
