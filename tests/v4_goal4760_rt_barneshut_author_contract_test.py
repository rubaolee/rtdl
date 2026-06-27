from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.rt_barneshut_author_contract import (  # noqa: E402
    RT_BARNESHUT_AUTHOR_CONTRACT_VERSION,
    load_rt_barneshut_author_dataset,
    parse_rt_barneshut_author_stdout,
    run_rt_barneshut_cpu_author_semantics_oracle,
    validate_rt_barneshut_author_contract_summary,
    write_trimmed_rt_barneshut_author_dataset,
)


class V4Goal4760RtBarnesHutAuthorContractTest(unittest.TestCase):
    def test_treelogy_loader_and_trim_preserve_author_header_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.txt"
            trimmed = Path(tmp) / "trimmed.txt"
            source.write_text(
                "\n".join(
                    [
                        "4.000000",
                        "1.000000",
                        "0.025000",
                        "0.050000",
                        "0.500000",
                        "10.0 -1.0 -1.0 -1.0 0.0 0.0 0.0",
                        "20.0 1.0 -1.0 -1.0 0.0 0.0 0.0",
                        "30.0 -1.0 1.0 1.0 0.0 0.0 0.0",
                        "40.0 1.0 1.0 1.0 0.0 0.0 0.0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            write_trimmed_rt_barneshut_author_dataset(source, trimmed, file_type="treelogy", limit=3)
            dataset = load_rt_barneshut_author_dataset(trimmed, file_type="treelogy")

            self.assertEqual(dataset.point_count, 3)
            self.assertEqual(dataset.header_values[0], 3.0)
            self.assertFalse(dataset.author_scaling_applied)

    def test_csv_loader_applies_author_scaling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "points.csv"
            source.write_text("1.0,2.0,3.0,4.0\n", encoding="utf-8")
            dataset = load_rt_barneshut_author_dataset(source, file_type="csv")

            point = dataset.points[0]
            self.assertEqual((point.x, point.y, point.z), (10.0, 20.0, 30.0))
            self.assertEqual(point.mass, 400000.0)
            self.assertTrue(dataset.author_scaling_applied)

    def test_cpu_author_semantics_oracle_is_deterministic_and_non_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.txt"
            source.write_text(
                "\n".join(
                    [
                        "6.000000",
                        "1.000000",
                        "0.025000",
                        "0.050000",
                        "0.500000",
                        "10.0 -2.0 -1.0 -1.0 0.0 0.0 0.0",
                        "20.0 -1.0 1.0 -1.0 0.0 0.0 0.0",
                        "30.0 1.0 -1.0 1.0 0.0 0.0 0.0",
                        "40.0 2.0 1.0 1.0 0.0 0.0 0.0",
                        "50.0 0.5 0.5 -0.5 0.0 0.0 0.0",
                        "60.0 -0.5 -0.5 0.5 0.0 0.0 0.0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            first = run_rt_barneshut_cpu_author_semantics_oracle(source, file_type="treelogy", limit=6)
            second = run_rt_barneshut_cpu_author_semantics_oracle(source, file_type="treelogy", limit=6)
            validate_rt_barneshut_author_contract_summary(first)

            self.assertEqual(first.contract_version, RT_BARNESHUT_AUTHOR_CONTRACT_VERSION)
            self.assertEqual(first.force_checksum, second.force_checksum)
            self.assertGreater(first.force_abs_checksum, 0.0)
            self.assertTrue(first.claim_boundary["paper_semantics_contract"])
            self.assertFalse(first.claim_boundary["rt_core_route"])
            self.assertFalse(first.claim_boundary["public_speedup_claim_authorized"])

    def test_parse_author_stdout_extracts_phase_timings(self) -> None:
        parsed = parse_rt_barneshut_author_stdout(
            "\n".join(
                [
                    "Number of points: 25000000",
                    "Preprocessing Time: 1.59359 seconds.",
                    "RT Cores Force Calculations time: 2.40888 seconds.",
                    "Execution time: 4.57178 seconds.",
                    "RT Force checksum: 1.2345e-05",
                    "RT Force abs checksum: 1.2345e-05",
                ]
            )
        )

        self.assertEqual(parsed["point_count"], 25000000)
        self.assertEqual(parsed["preprocessing_seconds"], 1.59359)
        self.assertEqual(parsed["rt_force_seconds"], 2.40888)
        self.assertEqual(parsed["execution_seconds"], 4.57178)
        self.assertEqual(parsed["rt_force_checksum"], 1.2345e-05)
        self.assertEqual(parsed["rt_force_abs_checksum"], 1.2345e-05)

    def test_probe_script_emits_non_speed_contract_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.txt"
            output = Path(tmp) / "out.json"
            source.write_text(
                "\n".join(
                    [
                        "4.000000",
                        "1.000000",
                        "0.025000",
                        "0.050000",
                        "0.500000",
                        "10.0 -1.0 -1.0 -1.0 0.0 0.0 0.0",
                        "20.0 1.0 -1.0 -1.0 0.0 0.0 0.0",
                        "30.0 -1.0 1.0 1.0 0.0 0.0 0.0",
                        "40.0 1.0 1.0 1.0 0.0 0.0 0.0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "rt_barneshut_author_contract_probe.py"),
                    "--dataset",
                    str(source),
                    "--file-type",
                    "treelogy",
                    "--limit",
                    "4",
                    "--output",
                    str(output),
                ],
                check=True,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

            self.assertEqual(payload["status"], "rt_barneshut_author_contract_probe_complete")
            self.assertTrue(payload["fairness"]["same_author_tree_and_force_cpu_contract"])
            self.assertFalse(payload["fairness"]["performance_comparison_authorized"])
            self.assertFalse(payload["claim_boundary"]["v2_v3_v4_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
