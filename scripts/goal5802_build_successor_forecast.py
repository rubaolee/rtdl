#!/usr/bin/env python3
"""Create the sealed Goal5802 successor forecast from manual judgements.

This is deliberately an untimed, premeasurement-only tool.  It derives every
identity from the exact supplied authorities and never supplies a probability,
interval, change reason, or fallback on the operator's behalf.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import Any, Mapping, Sequence

from experiments.goal5802_premeasurement.contract import (
    ContractError,
    build_cold_schedule,
    build_schedule,
    operation_contract as expected_operation_contract,
    successor_forecast_identity_binding,
)
from experiments.goal5802_premeasurement.successor_forecast import (
    GATES,
    PREDECESSOR_PROBABILITIES,
    REGIMES,
    REQUIRED_CHANGE_IDS,
    TASKS,
    THRESHOLDS,
    SuccessorForecastError,
    build_successor_forecast,
)
from experiments.goal5802_premeasurement.workload import (
    canonical,
    digest,
    workload_authority as expected_workload_authority,
)
from scripts.goal5802_bind_final_clean_install import (
    build_binding as rebuild_product_binding,
)


MANUAL_SCHEMA = "rtdl.goal5802.successor_forecast_manual_judgement.v1"
MANUAL_AUTHORITY_RELATIVE = (
    "history/internal_docs/"
    "goal5802_final_successor_forecast_manual_judgement_20260825.json")


class ForecastCliError(RuntimeError):
    """Fail-closed input or output error."""


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ForecastCliError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ForecastCliError(f"non-finite JSON number is forbidden: {value}")


def _regular_bytes(path: Path, label: str) -> bytes:
    if path.is_symlink():
        raise ForecastCliError(f"{label} may not be a symlink")
    try:
        metadata = path.stat()
    except OSError as error:
        raise ForecastCliError(f"{label} is unreadable: {path}") from error
    if not stat.S_ISREG(metadata.st_mode):
        raise ForecastCliError(f"{label} is not a regular file")
    try:
        return path.read_bytes()
    except OSError as error:
        raise ForecastCliError(f"{label} is unreadable: {path}") from error


def _decode_json(payload: bytes, label: str) -> Any:
    try:
        return json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_no_duplicate_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ForecastCliError(f"{label} is not strict UTF-8 JSON") from error


def _load_json(path: Path, label: str) -> Any:
    return _decode_json(_regular_bytes(path, label), label)


def _exact_keys(value: Any, keys: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise ForecastCliError(f"{label} keys differ")
    return value


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ForecastCliError(f"{label} root must be an object")
    return value


def _strict_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 \
            or any(character not in "0123456789abcdef" for character in value):
        raise ForecastCliError(f"{label} must be a lowercase SHA-256")
    return value


def _strict_nonnegative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ForecastCliError(f"{label} must be a nonnegative integer")
    return value


def _validate_source_manifest(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ForecastCliError("instrument source manifest must be nonempty")
    result: list[dict[str, Any]] = []
    paths: list[str] = []
    for index, raw in enumerate(value):
        row = _exact_keys(raw, {"path", "bytes", "sha256"},
                          f"instrument source manifest row {index}")
        path = row.get("path")
        if not isinstance(path, str) or not path or "\\" in path \
                or path.startswith("/") or Path(path).is_absolute() \
                or any(part in {"", ".", ".."} for part in path.split("/")):
            raise ForecastCliError("instrument source manifest path is unsafe")
        paths.append(path)
        result.append({
            "path": path,
            "bytes": _strict_nonnegative_int(
                row.get("bytes"), f"instrument manifest {path} bytes"),
            "sha256": _strict_sha(
                row.get("sha256"), f"instrument manifest {path} sha256"),
        })
    if len(paths) != len(set(paths)):
        raise ForecastCliError("instrument source manifest paths duplicate")
    return result


def _change_ids(value: Any, label: str) -> list[str]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ForecastCliError(f"{label} must be a change-id list")
    result = list(value)
    if not result or any(not isinstance(item, str) for item in result) \
            or len(result) != len(set(result)) \
            or any(item not in REQUIRED_CHANGE_IDS for item in result):
        raise ForecastCliError(f"{label} contains an invalid change id")
    expected = [item for item in REQUIRED_CHANGE_IDS if item in result]
    if result != expected:
        raise ForecastCliError(f"{label} change ids are not canonical")
    return result


def _manual_predictions(value: Any) -> tuple[
        list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    manual = _exact_keys(value, {
        "schema", "primary_predictions", "joint_prediction",
        "direct_context_predictions",
    }, "manual judgement")
    if manual.get("schema") != MANUAL_SCHEMA:
        raise ForecastCliError("manual judgement schema differs")

    raw_primary = manual.get("primary_predictions")
    if not isinstance(raw_primary, list) \
            or len(raw_primary) != len(TASKS) * len(REGIMES):
        raise ForecastCliError("manual primary predictions must contain six rows")
    primary: list[dict[str, Any]] = []
    expected_pairs = [(task, regime) for task in TASKS for regime in REGIMES]
    primary_keys = {
        "task", "regime", "predicted_median_interval",
        "predicted_95_percent_ci_upper_interval",
        "subjective_gate_pass_probability", "change_reason_ids",
    }
    for index, (raw, pair) in enumerate(zip(raw_primary, expected_pairs)):
        row = _exact_keys(raw, primary_keys,
                          f"manual primary prediction {index}")
        task, regime = pair
        if row.get("task") != task or row.get("regime") != regime:
            raise ForecastCliError("manual primary prediction row order differs")
        primary.append({
            "task": task,
            "regime": regime,
            "gate": GATES[regime],
            "noninferiority_threshold": THRESHOLDS[regime],
            "predicted_median_interval": row.get("predicted_median_interval"),
            "predicted_95_percent_ci_upper_interval": row.get(
                "predicted_95_percent_ci_upper_interval"),
            "subjective_gate_pass_probability": row.get(
                "subjective_gate_pass_probability"),
            "predecessor_subjective_gate_pass_probability": (
                PREDECESSOR_PROBABILITIES[pair]),
            "manual_successor_probability_entry": True,
            "probability_copied_or_defaulted_from_predecessor": False,
            "change_reason_ids": _change_ids(
                row.get("change_reason_ids"),
                f"manual primary prediction {index} change_reason_ids"),
        })

    raw_joint = _exact_keys(manual.get("joint_prediction"), {
        "all_six_gates_pass_probability_interval", "highest_risk_regime",
        "change_reason_ids",
    }, "manual joint prediction")
    joint = {
        "all_six_gates_pass_probability_interval": raw_joint.get(
            "all_six_gates_pass_probability_interval"),
        "predecessor_all_six_gates_pass_probability_interval": [0.25, 0.40],
        "manual_successor_probability_entry": True,
        "probability_copied_or_defaulted_from_predecessor": False,
        "independence_assumed": False,
        "highest_risk_regime": raw_joint.get("highest_risk_regime"),
        "change_reason_ids": _change_ids(
            raw_joint.get("change_reason_ids"),
            "manual joint prediction change_reason_ids"),
    }

    raw_direct = manual.get("direct_context_predictions")
    if not isinstance(raw_direct, list) or len(raw_direct) != len(TASKS):
        raise ForecastCliError("manual direct context must contain two rows")
    direct: list[dict[str, Any]] = []
    direct_keys = {"task", "predicted_median_interval", "change_reason_ids"}
    for index, (raw, task) in enumerate(zip(raw_direct, TASKS)):
        row = _exact_keys(raw, direct_keys,
                          f"manual direct context prediction {index}")
        if row.get("task") != task:
            raise ForecastCliError("manual direct context row order differs")
        direct.append({
            "task": task,
            "regime": "STEADY_E2E",
            "metric": "PYOPTIX_OVER_DIRECT",
            "predicted_median_interval": row.get("predicted_median_interval"),
            "manual_interval_entry": True,
            "change_reason_ids": _change_ids(
                row.get("change_reason_ids"),
                f"manual direct context prediction {index} change_reason_ids"),
        })
    return primary, joint, direct


def _validate_probability_semantics(forecast: Mapping[str, Any]) -> None:
    """Reject mathematically inconsistent manual probability judgements."""

    primary = forecast["primary_predictions"]
    for index, row in enumerate(primary):
        median = row["predicted_median_interval"]
        ci_upper = row["predicted_95_percent_ci_upper_interval"]
        if ci_upper[0] < median[0] or ci_upper[1] < median[1]:
            raise ForecastCliError(
                f"primary prediction {index} CI-upper interval is below "
                "its median interval")

    probabilities = [
        float(row["subjective_gate_pass_probability"]) for row in primary]
    joint = forecast["joint_prediction"]
    joint_interval = joint["all_six_gates_pass_probability_interval"]
    frechet_lower = max(0.0, sum(probabilities) - (len(probabilities) - 1))
    if joint_interval[0] + 1e-15 < frechet_lower \
            or joint_interval[1] > min(probabilities) + 1e-15:
        raise ForecastCliError(
            "joint all-six probability violates marginal probability bounds")
    minimum = min(probabilities)
    highest_risk = joint["highest_risk_regime"]
    if not any(
            row["regime"] == highest_risk
            and float(row["subjective_gate_pass_probability"]) == minimum
            for row in primary):
        raise ForecastCliError(
            "highest-risk regime does not contain a minimum-probability row")


def build_from_files(args: argparse.Namespace) -> dict[str, Any]:
    product = _object(_load_json(args.product_binding, "product binding"),
                      "product binding")
    workload = _object(_load_json(args.workload_authority, "workload authority"),
                       "workload authority")
    operation = _object(_load_json(args.operation_contract, "operation contract"),
                        "operation contract")
    comparative = _load_json(args.comparative_schedule, "comparative schedule")
    build_cold = _load_json(args.build_cold_schedule, "build-cold schedule")
    instrument = _validate_source_manifest(
        _load_json(args.instrument_source_manifest,
                   "instrument source manifest"))
    goal5799_bytes = _regular_bytes(args.goal5799_binding, "Goal5799 binding")
    manual_bytes = _regular_bytes(args.manual_judgement, "manual judgement")
    manual = _decode_json(manual_bytes, "manual judgement")

    expected_manual_path = (args.root / MANUAL_AUTHORITY_RELATIVE).resolve()
    try:
        observed_manual_path = args.manual_judgement.resolve(strict=True)
    except OSError as error:
        raise ForecastCliError("manual judgement path cannot be resolved") from error
    if observed_manual_path != expected_manual_path:
        raise ForecastCliError(
            "manual judgement is not the registered instrument authority path")
    manual_rows = [
        row for row in instrument
        if row["path"] == MANUAL_AUTHORITY_RELATIVE
    ]
    if len(manual_rows) != 1 \
            or manual_rows[0]["bytes"] != len(manual_bytes) \
            or manual_rows[0]["sha256"] != hashlib.sha256(
                manual_bytes).hexdigest():
        raise ForecastCliError(
            "manual judgement bytes differ from instrument source manifest")

    if product.get("schema") \
            != "rtdl.goal5802.final_clean_rtdlexe_binding.v4" \
            or product.get("status") != "PASS__FINAL_CLEAN_INSTALLED_RTLEXE":
        raise ForecastCliError("final product binding envelope differs")
    try:
        rebuilt_product = rebuild_product_binding(
            args.clean_install_root,
            source_commit=str(product.get("source_commit")),
            source_tree=str(product.get("source_tree")),
            repository_root=args.root,
            standalone_verifier=args.standalone_clean_verifier,
            native_custody_root=args.native_custody_root,
            standalone_native_custody_verifier=(
                args.standalone_native_custody_verifier),
            qualification_only_expected_trust_root_file_sha256=(
                args.qualification_only_expected_trust_root_file_sha256),
        )
    except (OSError, RuntimeError) as error:
        raise ForecastCliError(
            f"final product evidence reconstruction failed: {error}") \
            from error
    if product != rebuilt_product:
        raise ForecastCliError(
            "product binding differs from independently reconstructed "
            "clean-install/native-custody evidence")
    if workload != expected_workload_authority():
        raise ForecastCliError("workload authority differs from current contract")
    if operation != expected_operation_contract():
        raise ForecastCliError("operation contract differs from current contract")
    if comparative != build_schedule():
        raise ForecastCliError("comparative schedule differs from current contract")
    if build_cold != build_cold_schedule():
        raise ForecastCliError("build-cold schedule differs from current contract")

    primary, joint, direct = _manual_predictions(manual)
    identity = {
        "complete_product_binding_sha256": digest(product),
        "workload_authority_sha256": digest(workload),
        "operation_contract_sha256": digest(operation),
        "comparative_schedule_sha256": digest(comparative),
        "build_cold_absolute_schedule_sha256": digest(build_cold),
        "complete_instrument_source_manifest_sha256": digest(instrument),
        "goal5799_repaired_contract_sha256": hashlib.sha256(
            goal5799_bytes).hexdigest(),
    }
    try:
        expected_identity = successor_forecast_identity_binding(
            args.root, product)
    except (ContractError, OSError) as error:
        raise ForecastCliError(
            f"final product/current-source identity is invalid: {error}") \
            from error
    if identity != expected_identity:
        raise ForecastCliError(
            "supplied authorities differ from final product/current-source "
            "identity")
    forecast = build_successor_forecast(
        identity_binding=identity,
        operation_contract=operation,
        primary_predictions=primary,
        joint_prediction=joint,
        direct_context_predictions=direct,
    )
    _validate_probability_semantics(forecast)
    return forecast


def _publish_exclusive(path: Path, payload: bytes) -> None:
    """Atomically publish new bytes without ever replacing an existing path."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.tmp.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        try:
            os.chmod(temporary, 0o600)
            with os.fdopen(descriptor, "wb") as handle:
                descriptor = -1
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            if descriptor >= 0:
                os.close(descriptor)
        # link() is the create-only atomic publication point.  Unlike replace(),
        # it fails if a regular file or symlink appeared after the initial check.
        os.link(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Seal manual Goal5802 forecasts against exact final authorities; "
            "does not run measurements or authorize worker zero."))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--product-binding", type=Path, required=True)
    parser.add_argument("--clean-install-root", type=Path, required=True)
    parser.add_argument("--native-custody-root", type=Path, required=True)
    parser.add_argument("--standalone-clean-verifier", type=Path, required=True)
    parser.add_argument(
        "--qualification-only-expected-trust-root-file-sha256")
    parser.add_argument(
        "--standalone-native-custody-verifier", type=Path, required=True)
    parser.add_argument("--workload-authority", type=Path, required=True)
    parser.add_argument("--operation-contract", type=Path, required=True)
    parser.add_argument("--comparative-schedule", type=Path, required=True)
    parser.add_argument("--build-cold-schedule", type=Path, required=True)
    parser.add_argument("--instrument-source-manifest", type=Path, required=True)
    parser.add_argument("--goal5799-binding", type=Path, required=True)
    parser.add_argument("--manual-judgement", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    forecast = build_from_files(args)
    payload = canonical(forecast) + b"\n"
    _publish_exclusive(args.output, payload)
    print(json.dumps({
        "status": forecast["status"],
        "forecast_sha256": forecast["forecast_sha256"],
        "formal_worker_zero_authorized": False,
        "registered_gpu_timing_authorized": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ForecastCliError, SuccessorForecastError) as error:
        print(f"GOAL5802_SUCCESSOR_FORECAST_REJECTED: {error}", file=sys.stderr)
        raise SystemExit(2) from error
