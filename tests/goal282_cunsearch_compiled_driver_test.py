import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal282CuNSearchCompiledDriverTest(unittest.TestCase):
    def test_execute_compiled_driver_requires_response_file_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            binary = tmp / "driver"
            binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
            with self.assertRaisesRegex(RuntimeError, "expected response file"):
                rt.execute_compiled_cunsearch_fixed_radius_driver(
                    binary,
                    response_path=tmp / "missing.json",
                )

    def test_execute_compiled_driver_runs_stub_and_records_response(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            response = tmp / "response.json"
            binary = tmp / "driver"
            binary.write_text(
                "#!/bin/sh\n"
                f"printf '%s' '{json.dumps({'adapter': 'cunsearch', 'response_format': 'json_rows_v1', 'workload': 'fixed_radius_neighbors', 'rows': []})}' > '{response}'\n",
                encoding="utf-8",
            )
            binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
            elapsed = rt.execute_compiled_cunsearch_fixed_radius_driver(
                binary,
                response_path=response,
            )
            self.assertGreaterEqual(elapsed, 0.0)
            payload = json.loads(response.read_text(encoding="utf-8"))
            self.assertEqual(payload["adapter"], "cunsearch")


if __name__ == "__main__":
    unittest.main()
