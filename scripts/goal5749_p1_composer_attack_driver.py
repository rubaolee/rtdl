#!/usr/bin/env python3
"""Behavioral fail-closed attacks for the Goal5749 trusted PTX composer."""

from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path

from goal5749_v4_callback_poc_driver import (
    POLICY_PATH,
    SOURCE_PATH,
    _preflight,
    _sha256,
    _stable,
    _target_identity,
)
from rtdsl.v4_callback_poc import (
    CallbackRole,
    compile_numba_leaf_isolated,
    compile_numba_scalar_probe_isolated,
    generate_numba_leaf,
    generate_numba_scalar_probe,
    verify_callback_source,
)
from rtdsl.v4_optix_callback_runtime import run_verified_callback_poc


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    lane = "home_linux_behavioral_feasibility"
    cc = _preflight(policy, lane)
    target = _target_identity(policy, lane, cc)
    module = verify_callback_source(SOURCE_PATH.read_text(encoding="utf-8"))
    artifacts = [compile_numba_leaf_isolated(
        generate_numba_leaf(module, role, numeric_mode="strict"),
        compute_capability=cc,
        accepted_ptx_isa=(policy["backend"]["ptx_isa_min"],
                          policy["backend"]["ptx_isa_max"]),
        allowed_external_symbols=frozenset(),
    ) for role in CallbackRole]
    scalar = compile_numba_scalar_probe_isolated(
        generate_numba_scalar_probe(module, numeric_mode="strict"),
        compute_capability=cc,
        accepted_ptx_isa=(policy["backend"]["ptx_isa_min"],
                          policy["backend"]["ptx_isa_max"]),
        allowed_external_symbols=frozenset(),
    )
    spheres = (((5.0, 0.0, 0.0), 1.0, 9),
               ((5.0, 0.0, 0.0), 1.0, 3),
               ((8.0, 0.0, 0.0), 1.0, 3))
    rays = (((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),)

    environment_match = re.search(r"(_ZN08NumbaEnv[^;\s]+);", artifacts[0].ptx)
    environment_declaration_match = re.search(
        r"(?m)^(\.common \.global[^\n]*NumbaEnv[^\n]*;)$", artifacts[0].ptx)
    if environment_match is None or environment_declaration_match is None:
        raise RuntimeError("frozen Numba PTX lacks the expected environment declaration")
    environment_symbol = environment_match.group(1)
    environment_declaration = environment_declaration_match.group(1)
    attacks = []

    def execute(name: str, mutated, expected_fragment: str) -> None:
        try:
            run_verified_callback_poc(
                module,
                mutated,
                spheres=spheres,
                rays=rays,
                tmin=0.0,
                tmax=100.0,
                route="ordinary_composed",
                wrapper_numeric_mode="strict",
                scalar_probe=scalar,
            )
        except RuntimeError as exc:
            message = str(exc)
            if expected_fragment not in message:
                raise RuntimeError(
                    f"attack {name} failed for the wrong reason: {message}") from exc
            attacks.append({
                "name": name,
                "failed_closed": True,
                "expected_error_fragment": expected_fragment,
                "observed_error": message,
            })
            return
        raise RuntimeError(f"composer attack {name} was accepted")

    target_mutation = list(artifacts)
    target_mutation[1] = dataclasses.replace(
        target_mutation[1], ptx=target_mutation[1].ptx.replace(
            ".target sm_61", ".target sm_89", 1))
    execute("target_identity_mismatch", target_mutation,
            "V4 wrapper/leaf PTX target identity mismatch")

    occurrence_mutation = list(artifacts)
    occurrence_mutation[0] = dataclasses.replace(
        occurrence_mutation[0],
        ptx=occurrence_mutation[0].ptx + f"\n// conservative occurrence {environment_symbol}\n")
    execute("numba_environment_second_occurrence", occurrence_mutation,
            "V4 Numba environment symbol is referenced by leaf PTX")

    multiple_environment = list(artifacts)
    second_declaration = environment_declaration.replace(
        environment_symbol, "_ZN08NumbaEnv13_goal5749_second")
    multiple_environment[0] = dataclasses.replace(
        multiple_environment[0],
        ptx=multiple_environment[0].ptx + "\n" + second_declaration + "\n")
    execute("multiple_numba_environment_declarations", multiple_environment,
            "V4 leaf PTX has multiple Numba environment declarations")

    external_dependency = list(artifacts)
    external_dependency[0] = dataclasses.replace(
        external_dependency[0],
        ptx=external_dependency[0].ptx + "\n.extern .func rtdl_untrusted_external();\n")
    execute("new_external_dependency", external_dependency,
            "V4 verified leaf PTX acquired an external dependency")

    duplicate_symbols = list(artifacts)
    duplicate_symbols[1] = dataclasses.replace(
        duplicate_symbols[1], abi_name=duplicate_symbols[0].abi_name)
    execute("duplicate_leaf_symbol_identity", duplicate_symbols,
            'more than one instance of overloaded function')

    record = {
        "schema": "rtdl.goal5749.p1_composer_attack_result.v1",
        "goal": 5749,
        "scope": "functional_fail_closed_only__zero_registered_timing",
        "target_identity": target,
        "attack_count": len(attacks),
        "attacks": attacks,
        "all_failed_closed": all(row["failed_closed"] for row in attacks),
        "registered_performance_timing_count": 0,
        "successful_callback_output_created": False,
        "performance_claimed": False,
    }
    record["record_sha256"] = _stable(record)
    path = output / "RESULT.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": str(path), "sha256": _sha256(path),
                      "attacks": len(attacks)}, sort_keys=True))


if __name__ == "__main__":
    main()
