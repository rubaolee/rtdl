import unittest

from examples import rtdl_facility_knn_assignment as app


def _primary_from_rows(rows: list[dict[str, object]]) -> tuple[dict[int, int], dict[int, int]]:
    primary_by_customer: dict[int, int] = {}
    primary_load: dict[int, int] = {}
    for row in rows:
        if int(row["neighbor_rank"]) != 1:
            continue
        customer_id = int(row["query_id"])
        depot_id = int(row["neighbor_id"])
        primary_by_customer[customer_id] = depot_id
        primary_load[depot_id] = primary_load.get(depot_id, 0) + 1
    return dict(sorted(primary_by_customer.items())), dict(sorted(primary_load.items()))


class Goal730FacilityKnnCompactOutputTest(unittest.TestCase):
    def test_compact_primary_modes_match_primary_assignment_from_rows(self) -> None:
        rows_payload = app.run_case("cpu_python_reference", copies=8, output_mode="rows")
        primary_payload = app.run_case("cpu_python_reference", copies=8, output_mode="primary_assignments")
        summary_payload = app.run_case("cpu_python_reference", copies=8, output_mode="summary")

        expected_primary, expected_load = _primary_from_rows(rows_payload["rows"])

        self.assertEqual(rows_payload["k"], app.K)
        self.assertEqual(primary_payload["k"], app.PRIMARY_K)
        self.assertEqual(summary_payload["k"], app.PRIMARY_K)
        self.assertEqual(primary_payload["primary_depot_by_customer"], expected_primary)
        self.assertEqual(primary_payload["primary_depot_load"], expected_load)
        self.assertEqual(summary_payload["primary_depot_load"], expected_load)
        self.assertEqual(primary_payload["row_count"], rows_payload["customer_count"])
        self.assertEqual(summary_payload["row_count"], rows_payload["customer_count"])

    def test_compact_modes_omit_full_fallback_payload(self) -> None:
        primary_payload = app.run_case("cpu_python_reference", copies=4, output_mode="primary_assignments")
        summary_payload = app.run_case("cpu_python_reference", copies=4, output_mode="summary")

        self.assertNotIn("rows", primary_payload)
        self.assertNotIn("choices_by_customer", primary_payload)
        self.assertIn("primary_depot_by_customer", primary_payload)
        self.assertNotIn("rows", summary_payload)
        self.assertNotIn("choices_by_customer", summary_payload)
        self.assertNotIn("primary_depot_by_customer", summary_payload)

    def test_embree_primary_assignment_matches_cpu_reference(self) -> None:
        expected = app.run_case("cpu_python_reference", copies=8, output_mode="primary_assignments")
        actual = app.run_case("embree", copies=8, output_mode="primary_assignments")

        self.assertEqual(actual["primary_depot_by_customer"], expected["primary_depot_by_customer"])
        self.assertEqual(actual["primary_depot_load"], expected["primary_depot_load"])
        self.assertEqual(actual["row_count"], expected["row_count"])

    def test_rejects_invalid_copies_and_output_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "copies must be >= 1"):
            app.make_facility_knn_case(copies=0)
        with self.assertRaisesRegex(ValueError, "output_mode"):
            app.run_case("cpu_python_reference", output_mode="bad")


if __name__ == "__main__":
    unittest.main()
