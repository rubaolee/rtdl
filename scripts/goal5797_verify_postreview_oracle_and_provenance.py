"""Independent stdlib-only verifier for Goal5797's post-review correction."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
INPUT = HISTORY / (
    "goal5797_a1_oracle_counterfactual_and_source_provenance_result_"
    "20260823.json")
OUTPUT = HISTORY / (
    "goal5797_a1_oracle_counterfactual_and_source_provenance_independent_"
    "verification_20260823.json")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify_pin(pin: dict[str, object]) -> None:
    path = ROOT / str(pin["path"])
    require(path.is_file(), f"missing pinned file: {path}")
    require(path.stat().st_size == pin["bytes"], f"byte drift: {path}")
    require(sha_file(path) == pin["sha256"], f"hash drift: {path}")


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def main() -> None:
    result = json.loads(INPUT.read_text(encoding="utf-8"))
    require(result["status"] == "PASS", "input result is not PASS")
    seal = result["result_sha256"]
    unsealed = dict(result)
    del unsealed["result_sha256"]
    require(sha_bytes(canonical(unsealed)) == seal, "result seal mismatch")

    verify_pin(result["review"])
    p1 = result["p1_closure"]
    leaf = p1["P1_1_every_populated_contract_leaf"]
    require(leaf["populated_leaf_count"] == 19, "populated leaf count mismatch")
    require(leaf["decision_bearing_count"] == 19, "decision-bearing count mismatch")
    require(leaf["explicit_non_decision_bearing_count"] == 0,
            "unexpected non-decision-bearing leaf")
    require(leaf["require_status_ok_leaf"]["verdict_delta"] == "ACCEPT_TO_REJECT",
            "require_status_ok is not live")
    verify_pin(leaf["primary"])
    verify_pin(leaf["independent_verification"])

    oracle = result["oracle_scope"]
    verify_pin(oracle["source"])
    verify_pin(oracle["executed_result"])
    oracle_path = ROOT / str(oracle["source"]["path"])
    require(imports(oracle_path) <= {
        "__future__", "argparse", "hashlib", "json", "math", "pathlib", "struct",
    }, "independent oracle imports a non-stdlib implementation route")

    counterfactual = p1["P1_2_oracle_counterfactual"]
    rows = counterfactual["rows"]
    require(len(rows) == 5, "counterfactual row count mismatch")
    mechanisms = {row["mechanism"] for row in rows}
    require(mechanisms == {
        "role_effect_closure", "payload_attribute_abi_ownership",
        "physical_geometry_binding", "device_status_continuation",
        "checked_program_executable_identity",
    }, "counterfactual mechanism set mismatch")
    for row in rows:
        require(canonical(row["registered_attack_exposing_expected"]) != canonical(
            row["observed_invalid_program_result"]),
            f"oracle does not distinguish {row['mechanism']}")
        require(row["oracle_detects"] is True, "oracle_detects is not true")
        require(row["platform_automatic_diagnostic"] == "NO_DIAGNOSTIC",
                "unexpected platform diagnostic")
        require(row["optix_validation"] == "PASS", "OptiX validation not PASS")
        require(row["optix_validation_error_message_count"] == 0,
                "OptiX validation emitted an error")
        require(row["cuda_last_error"] == "SUCCESS", "CUDA last error not success")
        require(row["process_exit_code"] == 0, "process exit not zero")
        require(row["rtdl_prelaunch_gate"] == "REJECT", "gate did not reject")
    require(counterfactual["platform_automatic_check_detection_count"] == 0,
            "platform detection count mismatch")
    require(counterfactual["developer_oracle_detection_count_on_registered_inputs"] == 5,
            "oracle detection count mismatch")
    require(counterfactual["rtdl_prelaunch_gate_rejection_count"] == 5,
            "gate rejection count mismatch")

    provenance = result["device_source_provenance"]
    for key in ("base", "direct_host_arm", "pyoptix_host_arm",
                "goal5797_mutation_harness"):
        verify_pin(provenance[key])
    require(provenance["classification"].endswith("NOT_RTDL_GENERATED"),
            "device-source origin remains ambiguous")
    require(provenance["goal5797_valid_a_device_sha256_matches_base"] is True,
            "valid-A/base equality not established")

    accounting = result["goal5796_accounting"]
    for key in ("successor_result", "source_backed_responsibility_tables_v2",
                "same_host_transaction"):
        verify_pin(accounting[key])
    require(accounting["A_direct_B_pyoptix_D_rtdl_outputs_exact_and_identical"] is True,
            "A/B/D accounting missing")
    claims = result["claims"]
    require(claims["registered_performance_timing_count"] == 0,
            "timing appeared in post-review correction")
    require(claims["goal5798_timing_authorized"] is False,
            "Goal5798 timing was improperly authorized")
    require(claims["lx1_performance_host_authorized"] is False,
            "lx1 was improperly authorized")

    verification: dict[str, object] = {
        "schema": "rtdl.goal5797_a1.oracle_and_provenance_verification.v1",
        "status": "PASS",
        "imports_rtdl": False,
        "imports_pyoptix": False,
        "source_result_sha256": sha_file(INPUT),
        "verified_populated_leaf_count": 19,
        "verified_oracle_detection_count": 5,
        "verified_platform_detection_count": 0,
        "verified_gate_rejection_count": 5,
        "verified_device_source_origin": "HAND_WRITTEN_MATCHED_EXPERIMENT",
        "registered_performance_timing_count": 0,
    }
    verification["result_sha256"] = sha_bytes(canonical(verification))
    OUTPUT.write_bytes(json.dumps(
        verification, indent=2, sort_keys=True,
    ).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": "PASS",
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "file_sha256": sha_file(OUTPUT),
        "source_result_sha256": sha_file(INPUT),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
