from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.rt_barneshut_author_contract import (  # noqa: E402
    run_rt_barneshut_cpu_author_semantics_oracle,
)
from rtdsl.v4_rt_barneshut_author_route import (  # noqa: E402
    V4_RT_BARNESHUT_AUTHOR_ROUTE_VERSION,
    run_v4_rt_barneshut_external_author_rt_core_route,
    validate_v4_rt_barneshut_author_route_result,
)


def _write_treelogy(path: Path, *, count: int = 6) -> None:
    rows = [
        "10.0 -2.0 -1.0 -1.0 0.0 0.0 0.0",
        "20.0 -1.0 1.0 -1.0 0.0 0.0 0.0",
        "30.0 1.0 -1.0 1.0 0.0 0.0 0.0",
        "40.0 2.0 1.0 1.0 0.0 0.0 0.0",
        "50.0 0.5 0.5 -0.5 0.0 0.0 0.0",
        "60.0 -0.5 -0.5 0.5 0.0 0.0 0.0",
    ][:count]
    path.write_text(
        "\n".join(
            [
                f"{float(count):.6f}",
                "1.000000",
                "0.025000",
                "0.050000",
                "0.500000",
                *rows,
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_fake_author_binary(path: Path, checksum: float) -> None:
    path.write_text(
        textwrap.dedent(
            f"""
            import sys
            print("Number of points: 6")
            print("Preprocessing Time: 0.111 seconds.")
            print("RT Cores Force Calculations time: 0.022 seconds.")
            print("Execution time: 0.133 seconds.")
            print("RT Force checksum: {checksum:.17g}")
            print("RT Force abs checksum: {abs(checksum):.17g}")
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


class V4Goal4761RtBarnesHutAuthorRouteTest(unittest.TestCase):
    def test_external_author_rt_core_route_preserves_non_native_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.txt"
            trimmed = tmp_path / "trimmed.txt"
            fake_author = tmp_path / "fake_author.py"
            _write_treelogy(source)
            checksum = run_rt_barneshut_cpu_author_semantics_oracle(
                source, file_type="treelogy", limit=6
            ).force_checksum
            _write_fake_author_binary(fake_author, checksum)

            result = run_v4_rt_barneshut_external_author_rt_core_route(
                dataset=source,
                file_type="treelogy",
                limit=6,
                author_binary=fake_author,
                trimmed_dataset=trimmed,
                author_command_prefix=(sys.executable,),
            )
            validate_v4_rt_barneshut_author_route_result(result)

            self.assertEqual(result.route_version, V4_RT_BARNESHUT_AUTHOR_ROUTE_VERSION)
            self.assertTrue(result.rt_core_execution)
            self.assertTrue(result.external_author_binary)
            self.assertFalse(result.native_v4_operator)
            self.assertFalse(result.v4_performance_claim_authorized)
            self.assertTrue(result.checksum_validation["passes_float_output_tolerance"])
            self.assertEqual(result.phase_seconds["rt_force_seconds"], 0.022)
            self.assertFalse(result.claim_boundary["v2_v3_v4_speedup_claim_authorized"])

    def test_checksum_mismatch_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.txt"
            trimmed = tmp_path / "trimmed.txt"
            fake_author = tmp_path / "fake_author.py"
            _write_treelogy(source)
            _write_fake_author_binary(fake_author, 123.0)

            result = run_v4_rt_barneshut_external_author_rt_core_route(
                dataset=source,
                file_type="treelogy",
                limit=6,
                author_binary=fake_author,
                trimmed_dataset=trimmed,
                author_command_prefix=(sys.executable,),
            )

            self.assertFalse(result.checksum_validation["passes_float_output_tolerance"])
            with self.assertRaises(ValueError):
                validate_v4_rt_barneshut_author_route_result(result)

    def test_probe_script_writes_route_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.txt"
            trimmed = tmp_path / "trimmed.txt"
            fake_author = tmp_path / "fake_author.py"
            output = tmp_path / "route.json"
            _write_treelogy(source)
            checksum = run_rt_barneshut_cpu_author_semantics_oracle(
                source, file_type="treelogy", limit=6
            ).force_checksum
            _write_fake_author_binary(fake_author, checksum)

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "v4_rt_barneshut_author_route_probe.py"),
                    "--dataset",
                    str(source),
                    "--file-type",
                    "treelogy",
                    "--limit",
                    "6",
                    "--author-binary",
                    str(fake_author),
                    "--author-command-prefix",
                    sys.executable,
                    "--trimmed-dataset",
                    str(trimmed),
                    "--output",
                    str(output),
                ],
                check=True,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

            self.assertEqual(payload["route_kind"], "external_author_rt_core_reference_route")
            self.assertTrue(payload["rt_core_execution"])
            self.assertFalse(payload["native_v4_operator"])
            self.assertTrue(payload["checksum_validation"]["passes_float_output_tolerance"])


if __name__ == "__main__":
    unittest.main()
