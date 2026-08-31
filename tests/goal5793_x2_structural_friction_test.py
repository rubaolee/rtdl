from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts import goal5793_x2_structural_friction as friction


SOURCE = b"""from rtdsl.v4_semantically_admitted_compiler import admit_builtin_triangle_compilation
from rtdsl.optix_runtime import _load_optix_library

def run(x):
    # OptiX and cudaMalloc are retained as exact lexical evidence.
    admit_builtin_triangle_compilation(x)
    _load_optix_library()
    return len(x)
"""


def _lineage(path: str, raw: bytes) -> dict[str, object]:
    return {
        "schema": friction.SCHEMA,
        "lineage_id": "synthetic-lineage-1",
        "predecessor_lineage_ids": [],
        "app_owned_files": [{"path": path, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}],
        "generated_paths": [],
        "authority_scalar_paths": {
            "manual": ["semantic.output_type", "physical.geometry_family"],
            "defaulted": ["physical.gas_update_policy"],
            "derived": ["identity.source_sha256"],
            "unresolved": [],
        },
        "stage_records": [
            {
                "stage": "SOURCE_PROJECTION",
                "status": "PRESENT",
                "artifact": {"path": path, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()},
                "reason": None,
            },
            {"stage": "CALLBACK_IR", "status": "ABSENT", "artifact": None, "reason": "NOT_REACHED_CALLBACK_IR"},
        ],
        "failures": [{"stage": "CALLBACK_IR", "reason": "NOT_REACHED_CALLBACK_IR"}],
        "baseline": {"status": "NA", "reason": "NO_EXACT_FUNCTIONALLY_MATCHED_BASELINE", "source_pins": []},
    }


class Goal5793X2StructuralFrictionTest(unittest.TestCase):
    def test_01_counts_public_private_unresolved_tokens_and_first_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "app.py"
            path.write_bytes(SOURCE)
            result = friction.measure_lineage(root, _lineage("app.py", SOURCE))
        metrics = result["metrics"]
        self.assertEqual(metrics["app_owned_file_count"]["value"], 1)
        self.assertEqual(metrics["public_api_calls"]["value"], 1)
        self.assertEqual(metrics["private_api_calls"]["value"], 1)
        self.assertGreaterEqual(metrics["unresolved_api_calls"]["value"], 1)
        self.assertEqual(metrics["manual_authority_fields"]["value"], 2)
        self.assertGreaterEqual(metrics["raw_cuda_optix_tokens"]["value"], 2)
        self.assertEqual(metrics["first_diagnostic_failure_location"]["value"]["stage"], "CALLBACK_IR")
        self.assertEqual(metrics["author_or_direct_baseline"]["status"], "NA")
        self.assertIsNone(metrics["author_or_direct_baseline"]["value"])
        self.assertFalse(result["supports_easy_productive_simpler_less_code_or_better_than_cuda_claim"])

    def test_02_file_identity_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "app.py"
            path.write_bytes(SOURCE + b"\n")
            with self.assertRaisesRegex(friction.FrictionError, "FRICTION_APP_FILE_IDENTITY_MISMATCH"):
                friction.measure_lineage(root, _lineage("app.py", SOURCE))

    def test_03_authority_class_overlap_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_bytes(SOURCE)
            lineage = _lineage("app.py", SOURCE)
            lineage["authority_scalar_paths"]["derived"].append("semantic.output_type")
            with self.assertRaisesRegex(friction.FrictionError, "FRICTION_AUTHORITY_FIELD_CLASS_OVERLAP"):
                friction.measure_lineage(root, lineage)

    def test_04_absent_stage_requires_reason_and_na_never_becomes_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_bytes(SOURCE)
            lineage = _lineage("app.py", SOURCE)
            lineage["stage_records"][1]["reason"] = ""
            with self.assertRaisesRegex(friction.FrictionError, "FRICTION_ABSENT_STAGE_REASON_INVALID"):
                friction.measure_lineage(root, lineage)
            lineage = _lineage("app.py", SOURCE)
            lineage["baseline"] = {"status": "NA", "reason": "", "source_pins": []}
            with self.assertRaisesRegex(friction.FrictionError, "FRICTION_BASELINE_NA_REASON_INVALID"):
                friction.measure_lineage(root, lineage)

    def test_05_rows_digest_is_order_independent_but_ids_unique(self) -> None:
        rows = [{"lineage_id": "b", "value": 2}, {"lineage_id": "a", "value": 1}]
        self.assertEqual(friction.rows_digest(rows), friction.rows_digest(list(reversed(rows))))
        with self.assertRaisesRegex(friction.FrictionError, "FRICTION_LINEAGE_ID_DUPLICATE"):
            friction.rows_digest([rows[0], rows[0]])


if __name__ == "__main__":
    unittest.main()

