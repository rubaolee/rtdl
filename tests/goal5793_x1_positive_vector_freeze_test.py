from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import goal5793_x1_build_positive_vector_freeze as builder
from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT / "history/internal_docs/goal5789_a2_contract_evidence_20260821"


class PositiveVectorFreezeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = builder.build_freeze()
        cls.second = builder.build_freeze()

    def test_dry_build_deterministic_and_sealed(self) -> None:
        self.assertEqual(
            canonical_json_bytes(self.first), canonical_json_bytes(self.second)
        )
        self.assertEqual(
            self.first["authority_sha256"],
            seal_document(
                self.first,
                seal_field="authority_sha256",
                domain="rtdl.goal5793.x1.positive_vector_freeze",
                version=1,
            ),
        )

    def test_real_fifteen_lane_a2_replay_is_exact_six_nine_zero(self) -> None:
        replay = self.first["historical_replay"]
        self.assertEqual(replay["lane_count"], 15)
        self.assertEqual(
            replay["semantic_counts"],
            {
                "COMPATIBLE_FOR_DECLARED_DOMAIN": 6,
                "UNKNOWN": 9,
                "INCOMPATIBLE": 0,
            },
        )
        self.assertTrue(replay["all_stored_results_reproduced_exactly"])
        self.assertEqual(len({row["unit_id"] for row in replay["rows"]}), 15)
        for row in replay["rows"]:
            for kind in ("certificate", "result"):
                record = row[kind]
                path = ROOT / record["path"]
                self.assertEqual(path.stat().st_size, record["bytes"])
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"]
                )

    def test_every_current_positive_has_provenance_and_dedup_keeps_rows(self) -> None:
        rows = self.first["positive_rows"]
        self.assertEqual(self.first["positive_row_count"], 7)
        self.assertEqual(
            [row["row_id"] for row in rows],
            [*builder.EXPECTED_POSITIVE_IDS, builder.HELD_OUT_ID],
        )
        self.assertEqual(self.first["unique_structural_vector_count"], 4)
        dedup_provenance = [
            row_id
            for vector in self.first["unique_structural_vectors"]
            for row_id in vector["row_provenance"]
        ]
        self.assertCountEqual(dedup_provenance, [row["row_id"] for row in rows])
        axes = self.first["structural_axis_vocabulary"]
        for row in rows:
            self.assertEqual(list(row["structural_vector"]), axes)

    def test_particle_rtxrmq_shared_callback_does_not_claim_discrimination(self) -> None:
        identity = self.first["particle_rtxrmq_callback_identity"]
        self.assertTrue(identity["byte_identical_callback_contract"])
        self.assertFalse(identity["semantic_discrimination_added_by_shared_callback_identity"])
        rows = {row["row_id"]: row for row in self.first["positive_rows"]}
        particle = rows["particle__microfluidics_5000"]
        rtxrmq = rows[builder.HELD_OUT_ID]
        self.assertEqual(
            particle["callback_program_sha256"], rtxrmq["callback_program_sha256"]
        )
        self.assertEqual(particle["callback_ir_sha256"], rtxrmq["callback_ir_sha256"])
        self.assertNotEqual(
            particle["structural_vector_sha256"],
            rtxrmq["structural_vector_sha256"],
        )

    def test_identity_source_result_and_instance_size_do_not_steer_vector(self) -> None:
        certificate = json.loads(
            (A2 / "certificates/particle__microfluidics_5000.json").read_text(
                encoding="utf-8"
            )
        )
        baseline = builder.structural_vector(certificate)
        mutated = deepcopy(certificate)
        mutated["semantic_request"]["contract_id"] = "renamed.without.dispatch.v1"
        mutated["certificate_sha256"] = "0" * 64
        mutated["evidence_contract"]["source_pins"] = {"renamed/path": "1" * 64}
        for item in mutated["physical_encoding"]["maps"]:
            item["source_pin"] = "renamed/path"
            item["source_sha256"] = "1" * 64
        mutated["instance_contract"]["capacity"] = 999
        mutated["instance_contract"]["element_count"] = 999
        mutated["instance_contract"]["input_sha256"] = "2" * 64
        for item in mutated["instance_contract"]["bindings"]:
            item["owner_nonce"] = "renamed-owner"
            item["element_count"] = 999
        mutated["target_contract"]["native_sha256"] = "3" * 64
        self.assertEqual(baseline, builder.structural_vector(mutated))

    def test_semantic_structure_mutation_changes_vector(self) -> None:
        certificate = json.loads(
            (A2 / "certificates/particle__microfluidics_5000.json").read_text(
                encoding="utf-8"
            )
        )
        baseline = builder.structural_vector(certificate)
        mutated = deepcopy(certificate)
        mutated["semantic_request"]["policy"]["tie_policy"] = "hostile_tie"
        self.assertNotEqual(baseline, builder.structural_vector(mutated))

    def test_scope_is_historical_only_and_all_future_actions_are_zero(self) -> None:
        scope = self.first["scope"]
        self.assertEqual(
            self.first["status"],
            "FORMAL_HISTORICAL_POSITIVE_VECTOR_AUTHORITY__NOT_FUTURE_GENERALIZATION_EVIDENCE",
        )
        self.assertTrue(scope["formal_history_authority"])
        self.assertTrue(scope["historical_a2_replay_only"])
        self.assertFalse(scope["a2_controls_future_candidate"])
        for key in (
            "future_candidate_examiner_invocation_count",
            "search_call_count",
            "entropy_call_count",
            "candidate_implementation_count",
            "candidate_execution_count",
            "gpu_or_ssh_count",
            "registered_timing_count",
        ):
            self.assertEqual(scope[key], 0)
        self.assertFalse(scope["authorizes_future_candidate_exam"])
        self.assertFalse(scope["authorizes_execution"])
        self.assertFalse(scope["publication_authorized"])

    def test_packet_manifest_and_checker_bytes_are_hard_pinned(self) -> None:
        roots = self.first["frozen_roots"]
        manifest = roots["a2_postreview_packet_manifest"]
        self.assertEqual(
            manifest["sha256"], builder.EXPECTED_PACKET_MANIFEST_SHA256
        )
        for path, expected in builder.EXPECTED_DEPENDENCY_SHA256.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
        loaded = roots["exact_loaded_dependencies"]
        self.assertEqual(len(loaded), 3)
        for record in loaded.values():
            self.assertEqual(
                Path(record["loaded_origin"]).resolve(),
                (ROOT / record["path"]).resolve(),
            )

    def test_coordinated_replacement_of_manifest_is_rejected_by_external_pin(self) -> None:
        original = json.loads(builder.PACKET_MANIFEST_PATH.read_text(encoding="utf-8"))
        original["payloads"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_manifest_attack_") as td:
            counterfeit = Path(td) / "manifest.json"
            counterfeit.write_text(json.dumps(original), encoding="utf-8")
            with patch.object(builder, "PACKET_MANIFEST_PATH", counterfeit):
                with self.assertRaisesRegex(
                    ValueError, "postreview packet manifest bytes changed"
                ):
                    builder.build_freeze()


if __name__ == "__main__":
    unittest.main()
