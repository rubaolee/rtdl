from __future__ import annotations

import unittest

import rtdsl as rt


class _CloseOwner:
    def __init__(self) -> None:
        self.close_count = 0

    def close(self) -> None:
        self.close_count += 1


class Goal5044PublicPreparedGeometrySessionContractTest(unittest.TestCase):
    def test_public_symbols_and_regime_contract_are_exported(self) -> None:
        for name in (
            "PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION",
            "PREPARED_GEOMETRY_SESSION_API_MATURITY",
            "PREPARED_GEOMETRY_SESSION_REGIME_LABELS",
            "PreparedGeometrySession",
            "PreparedQueryBatch",
            "describe_prepared_geometry_session_contract",
            "prepared_geometry_session",
            "validate_prepared_geometry_session_contract",
        ):
            self.assertTrue(hasattr(rt, name), name)
            self.assertIn(name, rt.__all__)

        contract = rt.describe_prepared_geometry_session_contract()
        validation = rt.validate_prepared_geometry_session_contract(contract)
        self.assertEqual("accept", validation["status"])
        self.assertEqual((), validation["errors"])
        self.assertEqual(
            (
                "cold_cli_one_shot",
                "warm_process_fresh",
                "prepared_base_distinct_query_batch",
                "prepared_replay_same_input_diagnostic",
            ),
            contract["regime_labels"],
        )
        self.assertTrue(contract["same_input_replay_must_be_diagnostic"])
        self.assertTrue(contract["distinct_query_batch_required_for_query_many"])
        self.assertTrue(contract["cold_cli_one_shot_is_separate_from_warm_process_fresh"])
        self.assertFalse(contract["public_speedup_claim_authorized"])
        self.assertFalse(contract["true_zero_copy_claim_authorized"])

    def test_session_reuses_existing_cache_key_and_rejects_app_shaped_primitives(self) -> None:
        session = rt.prepared_geometry_session(
            primitive="directed_segment_point_location_2d",
            backend="optix",
            base_fingerprint={"base": "left-map", "rows": 1024},
            parameters={"scale": 15000},
            partner="numba",
            device="cuda:0",
        )

        self.assertEqual(rt.PREPARED_GEOMETRY_SESSION_CONTRACT_VERSION, session.to_metadata()["contract_version"])
        self.assertEqual("directed_segment_point_location_2d", session.cache_key.primitive)
        self.assertEqual("optix", session.cache_key.backend)
        self.assertEqual("numba", session.cache_key.partner)

        with self.assertRaisesRegex(ValueError, "app-shaped"):
            rt.prepared_geometry_session(
                primitive="rayjoin_overlay_fast_path",
                backend="optix",
                base_fingerprint="base",
            )

    def test_distinct_batches_are_query_many_and_same_input_replay_is_diagnostic(self) -> None:
        session = rt.prepared_geometry_session(
            primitive="planar_map_segment_pair_relation_2d",
            backend="optix",
            base_fingerprint="left-map-v1",
            coordinate_domain_fingerprint={"scale": 15000, "domain": "usa-top4"},
        )

        first = session.prepare_query_batch(
            {"chain_range": [0, 1000], "query_map": "right"},
            query_count=1000,
            batch_id="batch_a",
            require_distinct=True,
        )
        second = session.prepare_query_batch(
            {"chain_range": [1000, 2000], "query_map": "right"},
            query_count=1000,
            batch_id="batch_b",
            require_distinct=True,
        )
        replay = session.prepare_query_batch(
            {"chain_range": [0, 1000], "query_map": "right"},
            query_count=1000,
            batch_id="batch_a_replay",
        )

        self.assertEqual("prepared_base_distinct_query_batch", first.regime_label)
        self.assertEqual("prepared_base_distinct_query_batch", second.regime_label)
        self.assertEqual("prepared_replay_same_input_diagnostic", replay.regime_label)
        self.assertFalse(replay.distinct_query_batch)
        self.assertEqual("batch_a", replay.replay_of_batch_id)
        self.assertEqual(3, session.query_batch_count)
        self.assertEqual(2, session.distinct_query_batch_count)
        self.assertEqual(1, session.replay_batch_count)
        self.assertFalse(replay.to_metadata()["replay_only_speedup_claim_authorized"])

        with self.assertRaisesRegex(ValueError, "same-input replay"):
            session.prepare_query_batch(
                {"chain_range": [0, 1000], "query_map": "right"},
                query_count=1000,
                batch_id="bad_query_many_label",
                require_distinct=True,
            )

    def test_run_metadata_records_phases_without_authorizing_speedup_claims(self) -> None:
        session = rt.prepared_geometry_session(
            primitive="planar_map_segment_pair_relation_2d",
            backend="optix",
            base_fingerprint="base",
            base_phase_timing={
                "compile_setup_sec": 0.95,
                "per_input_workspace_setup_sec": 1.70,
            },
        )
        batch = session.prepare_query_batch(
            {"chain_range": [0, 10]},
            query_count=10,
            batch_id="distinct_batch",
        )
        run = session.run_metadata(
            batch,
            output="device_columns",
            phase_timing={
                "compile_setup_sec": 0.95,
                "per_input_workspace_setup_sec": 1.70,
                "kernel_run_sec": 0.05,
            },
            device_residency={
                "device_resident_candidate": True,
                "materializes_host_rows_for_bridge": False,
            },
        )

        self.assertEqual("prepared_base_distinct_query_batch", run["regime_label"])
        self.assertFalse(run["same_input_replay_is_diagnostic"])
        self.assertTrue(run["query_many_claim_authorized"])
        self.assertEqual(0.95, run["phase_timing"]["compile_setup_sec"])
        self.assertEqual(1.70, run["phase_timing"]["per_input_workspace_setup_sec"])
        self.assertFalse(run["public_speedup_claim_authorized"])
        self.assertFalse(run["true_zero_copy_claim_authorized"])

    def test_context_manager_closes_owned_session_once(self) -> None:
        owner = _CloseOwner()
        with rt.prepared_geometry_session(
            primitive="aabb_index_query_2d",
            backend="optix",
            base_fingerprint="base",
            owner=owner,
        ) as session:
            self.assertFalse(session.closed)
            self.assertEqual(0, owner.close_count)

        self.assertTrue(session.closed)
        self.assertEqual(1, owner.close_count)
        session.close()
        self.assertEqual(1, owner.close_count)

    def test_invalid_phase_timing_and_foreign_batch_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-negative"):
            rt.prepared_geometry_session(
                primitive="aabb_index_query_2d",
                backend="optix",
                base_fingerprint="base",
                base_phase_timing={"compile_setup_sec": -1.0},
            )

        left = rt.prepared_geometry_session(
            primitive="aabb_index_query_2d",
            backend="optix",
            base_fingerprint="left",
        )
        right = rt.prepared_geometry_session(
            primitive="aabb_index_query_2d",
            backend="optix",
            base_fingerprint="right",
        )
        foreign = right.prepare_query_batch("query", batch_id="foreign")
        with self.assertRaisesRegex(ValueError, "does not belong"):
            left.run_metadata(foreign)


if __name__ == "__main__":
    unittest.main()
