from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest import mock

from experiments.goal5802_premeasurement.contract import (
    ContractError,
    build_cold_schedule,
    build_schedule,
    operation_contract,
)
from experiments.goal5802_premeasurement.successor_forecast import (
    REGIMES,
    REQUIRED_CHANGE_IDS,
    SuccessorForecastError,
    TASKS,
    validate_successor_forecast,
)
from experiments.goal5802_premeasurement.workload import (
    canonical,
    digest,
    workload_authority,
)
from scripts.goal5802_build_successor_forecast import (
    ForecastCliError,
    MANUAL_AUTHORITY_RELATIVE,
    MANUAL_SCHEMA,
    main,
)


def _manual() -> dict[str, object]:
    primary = []
    for index, task in enumerate(TASKS):
        for regime_index, regime in enumerate(REGIMES):
            offset = index * len(REGIMES) + regime_index
            primary.append({
                "task": task,
                "regime": regime,
                "predicted_median_interval": [0.91 + offset / 100, 1.08],
                "predicted_95_percent_ci_upper_interval": [1.01, 1.18],
                "subjective_gate_pass_probability": 0.41 + offset / 100,
                "change_reason_ids": list(REQUIRED_CHANGE_IDS),
            })
    return {
        "schema": MANUAL_SCHEMA,
        "primary_predictions": primary,
        "joint_prediction": {
            "all_six_gates_pass_probability_interval": [0.10, 0.22],
            "highest_risk_regime": "DEPLOYMENT_COLD",
            "change_reason_ids": list(REQUIRED_CHANGE_IDS),
        },
        "direct_context_predictions": [
            {
                "task": TASKS[0],
                "predicted_median_interval": [4.5, 6.5],
                "change_reason_ids": list(REQUIRED_CHANGE_IDS),
            },
            {
                "task": TASKS[1],
                "predicted_median_interval": [8.0, 13.0],
                "change_reason_ids": list(REQUIRED_CHANGE_IDS),
            },
        ],
    }


class SuccessorForecastCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.product = {
            "schema": "rtdl.goal5802.final_clean_rtdlexe_binding.v4",
            "status": "PASS__FINAL_CLEAN_INSTALLED_RTLEXE",
            "source_commit": "1" * 40,
            "source_tree": "2" * 40,
            "identity": {"sha256": "a" * 64},
        }
        self.workload = workload_authority()
        self.operation = operation_contract()
        self.comparative = build_schedule()
        self.build_cold = build_cold_schedule()
        self.instrument = [
            {"path": "scripts/a.py", "bytes": 7, "sha256": "b" * 64},
            {"path": "tests/b.py", "bytes": 9, "sha256": "c" * 64},
        ]
        self.goal5799 = b"exact Goal5799 repaired contract bytes\n"
        self.manual = _manual()
        self.paths: dict[str, Path] = {}
        self._write_fixture("product_binding", self.product)
        self._write_fixture("workload_authority", self.workload)
        self._write_fixture("operation_contract", self.operation)
        self._write_fixture("comparative_schedule", self.comparative)
        self._write_fixture("build_cold_schedule", self.build_cold)
        self.paths["manual_judgement"] = self.root / MANUAL_AUTHORITY_RELATIVE
        self._write_fixture("manual_judgement", self.manual)
        self.paths["goal5799_binding"] = self.root / "goal5799.json"
        self.paths["goal5799_binding"].write_bytes(self.goal5799)
        self.output = self.root / "out" / "forecast.json"
        self.identity_patch = mock.patch(
            "scripts.goal5802_build_successor_forecast."
            "successor_forecast_identity_binding",
            side_effect=self._expected_identity)
        self.identity_patch.start()
        self.product_rebuild_patch = mock.patch(
            "scripts.goal5802_build_successor_forecast.rebuild_product_binding",
            return_value=copy.deepcopy(self.product))
        self.product_rebuild_patch.start()

    def tearDown(self) -> None:
        self.product_rebuild_patch.stop()
        self.identity_patch.stop()
        self.temporary.cleanup()

    def _expected_identity(
            self, root: Path, product: dict[str, object]) -> dict[str, str]:
        if product != self.product:
            raise ContractError("fake product binding rejected")
        return {
            "complete_product_binding_sha256": digest(self.product),
            "workload_authority_sha256": digest(self.workload),
            "operation_contract_sha256": digest(self.operation),
            "comparative_schedule_sha256": digest(self.comparative),
            "build_cold_absolute_schedule_sha256": digest(self.build_cold),
            "complete_instrument_source_manifest_sha256": digest(
                self.instrument),
            "goal5799_repaired_contract_sha256": hashlib.sha256(
                self.goal5799).hexdigest(),
        }

    def _write_fixture(self, name: str, value: object, *, allow_nan=False) -> None:
        path = self.paths.get(name, self.root / f"{name}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, allow_nan=allow_nan), encoding="utf-8")
        self.paths[name] = path
        if name == "manual_judgement" and hasattr(self, "instrument"):
            payload = path.read_bytes()
            self.instrument = [
                row for row in self.instrument
                if row["path"] != MANUAL_AUTHORITY_RELATIVE
            ] + [{
                "path": MANUAL_AUTHORITY_RELATIVE,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }]
            instrument_path = self.root / "instrument_source_manifest.json"
            instrument_path.write_text(
                json.dumps(self.instrument), encoding="utf-8")
            self.paths["instrument_source_manifest"] = instrument_path

    def _argv(self) -> list[str]:
        return [
            "--root", str(self.root),
            "--product-binding", str(self.paths["product_binding"]),
            "--clean-install-root", str(self.root / "clean"),
            "--native-custody-root", str(self.root / "custody"),
            "--standalone-clean-verifier", str(self.root / "clean_verify.py"),
            "--standalone-native-custody-verifier",
            str(self.root / "custody_verify.py"),
            "--workload-authority", str(self.paths["workload_authority"]),
            "--operation-contract", str(self.paths["operation_contract"]),
            "--comparative-schedule", str(self.paths["comparative_schedule"]),
            "--build-cold-schedule", str(self.paths["build_cold_schedule"]),
            "--instrument-source-manifest",
            str(self.paths["instrument_source_manifest"]),
            "--goal5799-binding", str(self.paths["goal5799_binding"]),
            "--manual-judgement", str(self.paths["manual_judgement"]),
            "--output", str(self.output),
        ]

    def test_builds_canonical_locked_forecast_bound_to_all_inputs(self) -> None:
        self.assertEqual(main(self._argv()), 0)
        payload = self.output.read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        forecast = json.loads(payload)
        self.assertEqual(payload, canonical(forecast) + b"\n")
        identity = forecast["identity_binding"]
        self.assertEqual(identity, {
            "build_cold_absolute_schedule_sha256": digest(self.build_cold),
            "comparative_schedule_sha256": digest(self.comparative),
            "complete_instrument_source_manifest_sha256": digest(
                self.instrument),
            "complete_product_binding_sha256": digest(self.product),
            "goal5799_repaired_contract_sha256": hashlib.sha256(
                self.goal5799).hexdigest(),
            "operation_contract_sha256": digest(self.operation),
            "workload_authority_sha256": digest(self.workload),
        })
        self.assertEqual(
            validate_successor_forecast(
                forecast,
                expected_identity_binding=identity,
                expected_operation_contract=self.operation),
            forecast)
        self.assertIs(
            forecast["authorization"]["formal_worker_zero_authorized"], False)
        self.assertIs(
            forecast["authorization"]["registered_gpu_timing_authorized"],
            False)

    def test_refuses_overwrite_before_rebuilding(self) -> None:
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"owner bytes")
        with self.assertRaises(FileExistsError):
            main(self._argv())
        self.assertEqual(self.output.read_bytes(), b"owner bytes")

    def test_concurrent_output_race_publishes_one_complete_forecast(self) -> None:
        barrier = threading.Barrier(2)
        original = canonical
        outcomes: list[object] = []

        def delayed(value: object) -> bytes:
            barrier.wait(timeout=5)
            return original(value)

        def invoke() -> None:
            try:
                outcomes.append(main(self._argv()))
            except BaseException as error:
                outcomes.append(error)

        with mock.patch(
                "scripts.goal5802_build_successor_forecast.canonical",
                side_effect=delayed):
            threads = [threading.Thread(target=invoke) for _ in range(2)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=10)
        self.assertEqual(sum(value == 0 for value in outcomes), 1)
        self.assertEqual(
            sum(isinstance(value, FileExistsError) for value in outcomes), 1)
        payload = self.output.read_bytes()
        forecast = json.loads(payload)
        self.assertEqual(payload, original(forecast) + b"\n")

    def test_bool_nan_missing_extra_and_row_order_all_reject(self) -> None:
        hostiles: list[dict[str, object]] = []
        boolean = copy.deepcopy(self.manual)
        boolean["primary_predictions"][0][
            "subjective_gate_pass_probability"] = True
        hostiles.append(boolean)
        nan = copy.deepcopy(self.manual)
        nan["primary_predictions"][0][
            "subjective_gate_pass_probability"] = float("nan")
        hostiles.append(nan)
        missing = copy.deepcopy(self.manual)
        del missing["primary_predictions"][0][
            "subjective_gate_pass_probability"]
        hostiles.append(missing)
        extra = copy.deepcopy(self.manual)
        extra["primary_predictions"][0]["note"] = "looks harmless"
        hostiles.append(extra)
        reordered = copy.deepcopy(self.manual)
        reordered["primary_predictions"][0], reordered["primary_predictions"][1] = (
            reordered["primary_predictions"][1],
            reordered["primary_predictions"][0],
        )
        hostiles.append(reordered)
        change_order = copy.deepcopy(self.manual)
        change_order["primary_predictions"][0]["change_reason_ids"] = list(
            reversed(REQUIRED_CHANGE_IDS))
        hostiles.append(change_order)

        for index, hostile in enumerate(hostiles):
            with self.subTest(index=index):
                self._write_fixture("manual_judgement", hostile, allow_nan=True)
                with self.assertRaises((ForecastCliError, SuccessorForecastError)):
                    main(self._argv())
                self.assertFalse(self.output.exists())

    def test_missing_or_extra_primary_rows_and_direct_order_reject(self) -> None:
        hostiles = []
        missing = copy.deepcopy(self.manual)
        missing["primary_predictions"].pop()
        hostiles.append(missing)
        extra = copy.deepcopy(self.manual)
        extra["primary_predictions"].append(
            copy.deepcopy(extra["primary_predictions"][-1]))
        hostiles.append(extra)
        direct_order = copy.deepcopy(self.manual)
        direct_order["direct_context_predictions"].reverse()
        hostiles.append(direct_order)
        for index, hostile in enumerate(hostiles):
            with self.subTest(index=index):
                self._write_fixture("manual_judgement", hostile)
                with self.assertRaises(ForecastCliError):
                    main(self._argv())

    def test_changed_contract_authorities_reject_before_output(self) -> None:
        hostile_operation = copy.deepcopy(self.operation)
        hostile_operation["status"] = "POSTRESULT_CHANGE"
        self._write_fixture("operation_contract", hostile_operation)
        with self.assertRaisesRegex(ForecastCliError, "operation contract differs"):
            main(self._argv())
        self.assertFalse(self.output.exists())

    def test_coherent_envelope_valid_fake_product_is_rejected(self) -> None:
        hostile_product = copy.deepcopy(self.product)
        hostile_product["identity"]["sha256"] = "f" * 64
        self._write_fixture("product_binding", hostile_product)
        with self.assertRaisesRegex(ForecastCliError, "product binding differs"):
            main(self._argv())
        self.assertFalse(self.output.exists())

    def test_manifest_reorder_path_trick_and_goal5799_substitution_reject(self) -> None:
        reordered = list(reversed(self.instrument))
        self._write_fixture("instrument_source_manifest", reordered)
        with self.assertRaisesRegex(ForecastCliError, "supplied authorities"):
            main(self._argv())
        self.assertFalse(self.output.exists())

        self._write_fixture("instrument_source_manifest", self.instrument)
        unsafe = copy.deepcopy(self.instrument)
        unsafe[0]["path"] = "scripts/../other.py"
        self._write_fixture("instrument_source_manifest", unsafe)
        with self.assertRaisesRegex(ForecastCliError, "unsafe"):
            main(self._argv())

        self._write_fixture("instrument_source_manifest", self.instrument)
        self.paths["goal5799_binding"].write_bytes(b"coherent substitute\n")
        with self.assertRaisesRegex(ForecastCliError, "supplied authorities"):
            main(self._argv())

    def test_duplicate_json_keys_and_invalid_manifest_reject(self) -> None:
        self.paths["manual_judgement"].write_bytes(
            b'{"schema":"a","schema":"b"}')
        with self.assertRaisesRegex(ForecastCliError, "duplicate JSON key"):
            main(self._argv())

        self._write_fixture("manual_judgement", self.manual)
        hostile_manifest = copy.deepcopy(self.instrument)
        hostile_manifest[1]["bytes"] = True
        self._write_fixture("instrument_source_manifest", hostile_manifest)
        with self.assertRaisesRegex(ForecastCliError, "nonnegative integer"):
            main(self._argv())

    def test_output_is_not_created_when_manual_changes_omit_required_id(self) -> None:
        omitted = REQUIRED_CHANGE_IDS[-1]
        hostile = copy.deepcopy(self.manual)
        for row in hostile["primary_predictions"]:
            row["change_reason_ids"].remove(omitted)
        hostile["joint_prediction"]["change_reason_ids"].remove(omitted)
        for row in hostile["direct_context_predictions"]:
            row["change_reason_ids"].remove(omitted)
        self._write_fixture("manual_judgement", hostile)
        with self.assertRaises(SuccessorForecastError):
            main(self._argv())
        self.assertFalse(self.output.exists())

    def test_cross_row_probability_semantics_reject(self) -> None:
        interval = copy.deepcopy(self.manual)
        interval["primary_predictions"][0][
            "predicted_95_percent_ci_upper_interval"] = [0.80, 0.89]
        self._write_fixture("manual_judgement", interval)
        with self.assertRaisesRegex(ForecastCliError, "CI-upper interval"):
            main(self._argv())

        impossible_joint = copy.deepcopy(self.manual)
        impossible_joint["joint_prediction"][
            "all_six_gates_pass_probability_interval"] = [0.43, 0.44]
        self._write_fixture("manual_judgement", impossible_joint)
        with self.assertRaisesRegex(ForecastCliError, "marginal probability"):
            main(self._argv())

        wrong_risk = copy.deepcopy(self.manual)
        wrong_risk["joint_prediction"]["highest_risk_regime"] = "PREPARE"
        self._write_fixture("manual_judgement", wrong_risk)
        with self.assertRaisesRegex(ForecastCliError, "highest-risk"):
            main(self._argv())

    def test_real_manual_judgement_file_passes_semantic_checks(self) -> None:
        real = Path(__file__).resolve().parents[1] / (
            "history/internal_docs/"
            "goal5802_final_successor_forecast_manual_judgement_20260825.json")
        self._write_fixture(
            "manual_judgement",
            json.loads(real.read_text(encoding="utf-8")))
        self.assertEqual(main(self._argv()), 0)


if __name__ == "__main__":
    unittest.main()
