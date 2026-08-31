from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from goal5776_build_formal_result_evidence import build, _digest


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Goal5776FormalEvidenceTest(unittest.TestCase):
    def _fixture(self, root: Path) -> dict[str, Path]:
        raw = root / "raw"
        workers = raw / "workers"
        workers.mkdir(parents=True)
        for index in range(464):
            (workers / f"{index:04d}.json").write_text(
                json.dumps({"worker_index": index}) + "\n", encoding="utf-8")
        closeout = root / "closeout"
        closeout.mkdir()
        (closeout / "FINAL.json").write_text(json.dumps({
            "schema": "rtdl.goal5776.real_scale_v2_v4_final.v1",
            "measurement_complete": True,
            "worker_count": 464,
            "independent_row_count": 34,
        }) + "\n", encoding="utf-8")
        execution = root / "EXECUTION_SOURCE.tar.gz"
        native = root / "librtdl_optix.so"
        cache_manifest = root / "FORMAL_NUMBA_LEAF_CACHE_MANIFEST.json"
        evidence = root / "FIXED_RADIUS_REFINEMENT_EVIDENCE.json"
        data_manifest = root / "DATA_MANIFEST.json"
        runtime_budget = root / "RUNTIME_BUDGET.json"
        expected_value = root / "EXPECTED_VALUE_STATEMENT.md"
        for path, data in (
            (execution, b"source"), (native, b"native"),
            (cache_manifest, b'{"cache":true}\n'),
            (evidence, b'{"proof":true}\n'),
            (data_manifest, b'{"data":true}\n'),
            (runtime_budget, b'{"budget":true}\n'),
            (expected_value, b'negative prior is frozen\n'),
        ):
            path.write_bytes(data)
        cache = root / "cache"
        cache.mkdir()
        (cache / "leaf.bin").write_bytes(b"leaf")
        functional = root / "TARGET_FUNCTIONAL"
        functional.mkdir()
        for index in range(126):
            (functional / f"{index:03d}.json").write_text(
                json.dumps({"trial": index}) + "\n", encoding="utf-8")
        records_digest = hashlib.sha256()
        for path in sorted(functional.glob("[0-9][0-9][0-9].json")):
            records_digest.update(path.name.encode("utf-8"))
            records_digest.update(b"\0")
            records_digest.update(bytes.fromhex(_sha(path)))
        functional_summary = functional / "SUMMARY.json"
        functional_summary.write_text(
            json.dumps({
                "functional_trial_count": 126,
                "functional_records_sha256": records_digest.hexdigest(),
                "cache_population_observation_count": 1,
                "cache_population_cost_is_free": False,
                "cache_population_observation_is_not_formal_performance": True,
            }) + "\n",
            encoding="utf-8")
        plan = root / "PLAN.json"
        identities = {
            "bundle_sha256": "1" * 64,
            "data_archive_sha256": "2" * 64,
            "execution_source_sha256": _sha(execution),
            "rtdbscan_evidence_sha256": _sha(evidence),
            "native_library_sha256": _sha(native),
            "target_identity_sha256": "3" * 64,
            "prepared_identity_sha256": "4" * 64,
            "formal_identity_sha256": "5" * 64,
            "leaf_cache_manifest_sha256": _sha(cache_manifest),
            "runtime_budget_sha256": _sha(runtime_budget),
            "expected_value_statement_sha256": _sha(expected_value),
        }
        plan_payload = {
            "schema": "rtdl.goal5776.real_scale_plan.v1",
            **{key: identities[key] for key in (
                "bundle_sha256", "data_archive_sha256",
                "prepared_identity_sha256", "target_identity_sha256",
                "formal_identity_sha256",
                "runtime_budget_sha256",
                "expected_value_statement_sha256",
            )},
            "conservative_budget_seconds": 123.0,
        }
        plan.write_text(json.dumps(plan_payload, sort_keys=True) + "\n")
        identities["plan_sha256"] = _sha(plan)
        runtime = root / "RUNTIME.json"
        runtime_payload = {
            "schema": "rtdl.goal5776.real_scale_runtime.v1",
            **identities,
            "formal_contract_sha256": "6" * 64,
            "execution_source_path": str(execution),
            "native_library_path": str(native),
            "leaf_cache_manifest_path": str(cache_manifest),
            "leaf_cache_root": str(cache),
            "rtdbscan_evidence_path": str(evidence),
            "data_manifest_path": str(data_manifest),
            "data_manifest_sha256": _sha(data_manifest),
            "runtime_budget_path": str(runtime_budget),
            "expected_value_statement_path": str(expected_value),
            "conservative_budget_seconds": 123.0,
            "target_functional_root": str(functional),
            "target_functional_summary_sha256": _sha(functional_summary),
        }
        runtime.write_text(json.dumps(runtime_payload, sort_keys=True) + "\n")
        prepared = root / "PREPARED.json"
        prepared.write_text(json.dumps({
            "schema": "rtdl.goal5776.create_only_target_prepare_result.v1",
            **identities,
            "conservative_budget_seconds": 123.0,
            "target_functional_summary_sha256": _sha(functional_summary),
            "runtime_sha256": _sha(runtime),
            "all_126_functional_trials_correct_and_behavioral_true_optix": True,
            "formal_worker_count": 0,
            "registered_formal_timing_count": 0,
            "formal_requires_second_exact_owner_authority": True,
        }, sort_keys=True) + "\n")
        authority = root / "FORMAL_AUTHORITY.json"
        authority_body = {
            "schema": "rtdl.goal5776.owner_formal_authority.v2",
            **identities,
            "formal_contract_sha256": runtime_payload["formal_contract_sha256"],
            "runtime_sha256": _sha(runtime),
            "expected_worker_count": 464,
            "expected_independent_row_count": 34,
            "owner_authorized_exactly_once": True,
            "repair_retry_resume_replacement_allowed": False,
            "owner_confirmed_conservative_budget_seconds": 123.0,
        }
        authority.write_text(json.dumps({
            **authority_body, "authority_sha256": _digest(authority_body),
        }, sort_keys=True) + "\n")
        return {
            "raw_root": raw, "closeout_root": closeout,
            "runtime_path": runtime, "plan_path": plan,
            "prepared_path": prepared, "authority_path": authority,
        }

    def test_archive_is_deterministic_and_manifest_rehashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = self._fixture(root)
            output, twin = root / "evidence.tar.gz", root / "twin.tar.gz"
            result = build(**paths, output=output, twin=twin)
            self.assertTrue(result["twin_byte_identical"])
            self.assertEqual(output.read_bytes(), twin.read_bytes())
            with gzip.open(output, "rb") as stream:
                archive = tarfile.open(fileobj=io.BytesIO(stream.read()), mode="r:")
                members = {m.name: archive.extractfile(m).read()
                           for m in archive.getmembers() if m.isfile()}
            manifest = json.loads(members["GOAL5776_EVIDENCE_MANIFEST.json"])
            self.assertEqual(manifest["worker_count"], 464)
            self.assertEqual(manifest["independent_row_count"], 34)
            self.assertEqual(manifest["target_functional_payload_count"], 127)
            self.assertEqual(manifest["conservative_budget_seconds"], 123.0)
            for row in manifest["payloads"]:
                self.assertEqual(
                    hashlib.sha256(members[row["path"]]).hexdigest(),
                    row["sha256"],
                )

    def test_evidence_rejects_fixed_radius_byte_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = self._fixture(root)
            evidence = Path(json.loads(paths["runtime_path"].read_text())[
                "rtdbscan_evidence_path"])
            evidence.write_bytes(b"tampered")
            with self.assertRaisesRegex(RuntimeError, "identity mismatch"):
                build(
                    **paths, output=root / "evidence.tar.gz",
                    twin=root / "twin.tar.gz")


if __name__ == "__main__":
    unittest.main()
