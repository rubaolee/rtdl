import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from scripts.goal28d_complete_and_run_county_zipcode import select_county_zipcode_slice
from scripts.goal28d_complete_and_run_county_zipcode import subset_by_face_ids


class Goal28DExecutionTest(unittest.TestCase):
    def test_select_county_zipcode_slice_prefers_overlapping_low_cost_candidate(self) -> None:
        county = rt.parse_cdb_text(
            "\n".join(
                [
                    "1 4 1 4 100 0",
                    "0 0",
                    "4 0",
                    "4 4",
                    "0 0",
                    "2 4 5 8 200 0",
                    "100 100",
                    "104 100",
                    "104 104",
                    "100 100",
                ]
            ),
            name="county",
        )
        zipcode = rt.parse_cdb_text(
            "\n".join(
                [
                    "10 4 1 4 1000 0",
                    "1 1",
                    "2 1",
                    "2 2",
                    "1 1",
                    "11 4 5 8 1001 0",
                    "3 3",
                    "3.5 3",
                    "3.5 3.5",
                    "3 3",
                    "12 4 9 12 1002 0",
                    "101 101",
                    "102 101",
                    "102 102",
                    "101 101",
                ]
            ),
            name="zipcode",
        )
        selection = select_county_zipcode_slice(county, zipcode, min_zip_matches=2, target_zip_matches=2)
        self.assertEqual(selection["county_face_id"], 100)
        self.assertEqual(selection["zipcode_face_ids"], [1000, 1001])

    def test_subset_by_face_ids_filters_chains(self) -> None:
        dataset = rt.parse_cdb_text(
            "\n".join(
                [
                    "1 3 1 3 10 0",
                    "0 0",
                    "1 0",
                    "0 0",
                    "2 3 4 6 20 0",
                    "2 2",
                    "3 2",
                    "2 2",
                ]
            ),
            name="faces",
        )
        subset = subset_by_face_ids(dataset, {20}, name="subset")
        self.assertEqual(subset.name, "subset")
        self.assertEqual(len(subset.chains), 1)
        self.assertEqual(subset.chains[0].left_face_id, 20)


if __name__ == "__main__":
    unittest.main()
