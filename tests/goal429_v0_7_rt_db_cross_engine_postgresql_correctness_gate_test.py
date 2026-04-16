import os
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl import connect_postgresql
from rtdsl import prepare_postgresql_denorm_table
from rtdsl import query_postgresql_conjunctive_scan
from rtdsl import query_postgresql_grouped_count
from rtdsl import query_postgresql_grouped_sum
from rtdsl.db_perf import db_perf_conjunctive_scan_reference
from rtdsl.db_perf import db_perf_grouped_count_reference
from rtdsl.db_perf import db_perf_grouped_sum_reference
from rtdsl.db_perf import make_conjunctive_scan_case
from rtdsl.db_perf import make_grouped_count_case
from rtdsl.db_perf import make_grouped_sum_case


class Goal429V07RtDbCrossEnginePostgresqlCorrectnessGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dsn = os.environ.get("RTDL_POSTGRESQL_DSN", "dbname=postgres")
        if not rt.embree_version():
            raise unittest.SkipTest("Embree runtime is not available")
        if not rt.optix_version():
            raise unittest.SkipTest("OptiX runtime is not available")
        if not rt.vulkan_version():
            raise unittest.SkipTest("Vulkan runtime is not available")

    def test_conjunctive_scan_all_engines_match_postgresql(self) -> None:
        case = make_conjunctive_scan_case(4096)
        expected = rt.run_cpu_python_reference(db_perf_conjunctive_scan_reference, **case)
        self.assertEqual(rt.run_cpu(db_perf_conjunctive_scan_reference, **case), expected)
        self.assertEqual(rt.run_embree(db_perf_conjunctive_scan_reference, **case), expected)
        self.assertEqual(rt.run_optix(db_perf_conjunctive_scan_reference, **case), expected)
        self.assertEqual(rt.run_vulkan(db_perf_conjunctive_scan_reference, **case), expected)
        with connect_postgresql(self.dsn) as connection:
            prepare_postgresql_denorm_table(connection, case["table"], case["predicates"], table_name="rtdl_goal429_scan")
            pg_rows = query_postgresql_conjunctive_scan(connection, case["predicates"], table_name="rtdl_goal429_scan")
        self.assertEqual(pg_rows, expected)

    def test_grouped_count_all_engines_match_postgresql(self) -> None:
        case = make_grouped_count_case(4096)
        expected = rt.run_cpu_python_reference(db_perf_grouped_count_reference, **case)
        self.assertEqual(rt.run_cpu(db_perf_grouped_count_reference, **case), expected)
        self.assertEqual(rt.run_embree(db_perf_grouped_count_reference, **case), expected)
        self.assertEqual(rt.run_optix(db_perf_grouped_count_reference, **case), expected)
        self.assertEqual(rt.run_vulkan(db_perf_grouped_count_reference, **case), expected)
        with connect_postgresql(self.dsn) as connection:
            prepare_postgresql_denorm_table(connection, case["table"], case["query"]["predicates"], table_name="rtdl_goal429_gcount")
            pg_rows = query_postgresql_grouped_count(connection, case["query"], table_name="rtdl_goal429_gcount")
        self.assertEqual(pg_rows, expected)

    def test_grouped_sum_all_engines_match_postgresql(self) -> None:
        case = make_grouped_sum_case(4096)
        expected = rt.run_cpu_python_reference(db_perf_grouped_sum_reference, **case)
        self.assertEqual(rt.run_cpu(db_perf_grouped_sum_reference, **case), expected)
        self.assertEqual(rt.run_embree(db_perf_grouped_sum_reference, **case), expected)
        self.assertEqual(rt.run_optix(db_perf_grouped_sum_reference, **case), expected)
        self.assertEqual(rt.run_vulkan(db_perf_grouped_sum_reference, **case), expected)
        with connect_postgresql(self.dsn) as connection:
            prepare_postgresql_denorm_table(connection, case["table"], case["query"]["predicates"], table_name="rtdl_goal429_gsum")
            pg_rows = query_postgresql_grouped_sum(connection, case["query"], table_name="rtdl_goal429_gsum")
        self.assertEqual(pg_rows, expected)


if __name__ == "__main__":
    unittest.main()
