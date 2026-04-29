import unittest


class Goal1134HausdorffPhaseSchemaReconcileTest(unittest.TestCase):
    def test_goal887_hausdorff_contract_declares_app_level_phase_aliases(self) -> None:
        from scripts import goal887_prepared_decision_phase_profiler as goal887

        payload = goal887.run_profile(
            scenario="hausdorff_threshold",
            mode="dry-run",
            copies=2,
            body_count=32,
            iterations=1,
            radius=0.4,
            skip_validation=False,
        )
        contract = payload["cloud_claim_contract"]

        self.assertEqual(contract["schema_scope"], "goal887_profiler_payload")
        aliases = contract["app_level_phase_aliases"]
        self.assertEqual(aliases["input_build_sec"], "run_app.run_phases.input_construction_sec")
        self.assertEqual(aliases["optix_query_sec"], "run_app.run_phases.optix_query_sec")
        self.assertIn("profiler-only", aliases["point_pack_sec"])
        self.assertIn("profiler-only", aliases["optix_close_sec"])
        self.assertIn("Goal887 required_phase_groups describe the cloud profiler payload", contract["phase_schema_note"])

    def test_other_prepared_decision_contracts_keep_profiler_schema_scope(self) -> None:
        from scripts import goal887_prepared_decision_phase_profiler as goal887

        payload = goal887.run_profile(
            scenario="ann_candidate_coverage",
            mode="dry-run",
            copies=2,
            body_count=32,
            iterations=1,
            radius=0.2,
            skip_validation=False,
        )
        contract = payload["cloud_claim_contract"]

        self.assertEqual(contract["schema_scope"], "goal887_profiler_payload")
        self.assertNotIn("app_level_phase_aliases", contract)


if __name__ == "__main__":
    unittest.main()
