from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"


class Goal3260RayJoinRunnerRecordsPipQueryAxisTest(unittest.TestCase):
    def test_runner_exposes_and_records_generic_pip_query_axis(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("--rtdl-pip-query-axis", text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS", text)
        self.assertIn('"query_axis": query_axis', text)
        self.assertIn("args.rtdl_pip_query_axis", text)
        self.assertIn("rtdl_pip_query_axis", text)

    def test_query_axis_is_scoped_to_rtdl_call(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("@contextlib.contextmanager", text)
        self.assertIn("def temporary_env", text)
        self.assertIn("os.environ[name] = value", text)
        self.assertIn("os.environ.pop(name, None)", text)
        self.assertIn('with temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS", query_axis):', text)


if __name__ == "__main__":
    unittest.main()
