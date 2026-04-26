import unittest


SCHEMA = "goal825_tier1_phase_contract_v1"
DB_SCHEMA = "goal921_db_phase_review_contract_v2"


class Goal825Tier1ProfilerContractTest(unittest.TestCase):
    def test_db_profiler_contract_is_machine_readable(self) -> None:
        module = __import__("scripts.goal756_db_prepared_session_perf", fromlist=["run_suite"])
        payload = module.run_suite(
            backends=("cpu",),
            scenario="sales_risk",
            copies=1,
            iterations=1,
            output_mode="compact_summary",
            strict=True,
        )
        self.assertEqual(payload["schema_version"], DB_SCHEMA)
        result = payload["results"][0]
        self.assertEqual(result["schema_version"], DB_SCHEMA)
        for key in result["cloud_claim_contract"]["required_phase_groups"]:
            self.assertIn(key, result)

    def test_fixed_radius_profiler_contract_names_non_claims(self) -> None:
        module = __import__("scripts.goal757_optix_fixed_radius_prepared_perf", fromlist=["_cloud_claim_contract"])
        outlier = module._cloud_claim_contract("outlier_detection", "threshold_count")
        dbscan = module._cloud_claim_contract("dbscan_clustering", "threshold_count")
        self.assertIn("prepared fixed-radius scalar threshold-count", outlier["claim_scope"])
        self.assertIn("not per-point outlier labels", outlier["non_claim"])
        self.assertIn("KNN", outlier["non_claim"])
        self.assertIn("prepared fixed-radius scalar core-count", dbscan["claim_scope"])
        self.assertIn("not per-point core flags", dbscan["non_claim"])
        self.assertIn("not full DBSCAN", dbscan["non_claim"])

    def test_robot_profiler_contract_names_compact_pose_scope(self) -> None:
        module = __import__("scripts.goal760_optix_robot_pose_flags_phase_profiler", fromlist=["run_suite"])
        payload = module.run_suite(
            mode="dry-run",
            pose_count=4,
            obstacle_count=2,
            iterations=1,
            validate=False,
        )
        self.assertEqual(payload["schema_version"], SCHEMA)
        contract = payload["cloud_claim_contract"]
        self.assertIn("compact pose summary", contract["claim_scope"])
        self.assertIn("not continuous collision detection", contract["non_claim"])
        for key in contract["required_phase_groups"]:
            self.assertIn(key, payload["phases"])


if __name__ == "__main__":
    unittest.main()
