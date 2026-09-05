"""Trusted compiler for V4 custom-AABB bounded relation emission."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass, replace
from enum import Enum
import hashlib
import json
from pathlib import Path
import sys
import threading
import weakref

from .v4_bounded_relation import (
    CompiledBoundedRelationContract,
    VerifiedBoundedRelationAuthority,
    compile_bounded_relation_contract,
    verify_bounded_relation_schema,
)
from .v4_bounded_relation_optix_wrapper_codegen import (
    generate_trusted_bounded_relation_wrapper_v1,
)
from .v4_callback_abi import CompiledCallbackAbi, verify_compiled_callback_abi
from .v4_callback_ir import CallbackRole, RuntimeStatus, ScalarKind
from .v4_callback_numba_codegen import (
    FORMAL_NUMBA_SOURCE_SCHEMA,
    GeneratedFormalNumbaLeaf,
    FormalNumbaLeafCachePolicy,
    _Emitter,
    _Value,
    _emit_helper,
    _integer_bounds,
    _device_function_artifact_dict,
    _device_function_artifact_from_dict,
    _leaf_scalar_kinds,
    _parameter_types,
    _parameter_name,
    _reachable_helpers,
    compile_formal_numba_leaves_isolated,
)
from .v4_callback_optix_wrapper_codegen import GeneratedOptixWrapper
from .v4_callback_optix_wrapper_codegen import _prototype
from .v4_callback_poc import DeviceFunctionArtifact
from .v4_callback_ptx_composer import (
    ComposedCallbackPtx,
    bind_inline_callback_ptx,
)
from .v4_inline_cuda_codegen import lower_formal_leaves_to_inline_cuda
from .v4_triangle_optix_compiler import _compile_nvrtc
from .v4_executable_cache import (
    V4ExecutableCachePolicy,
    load_executable_cache_entry,
    store_executable_cache_entry,
)


@dataclass(frozen=True, eq=False)
class VerifiedBoundedRelationExecutable:
    schema: str
    authority_sha256: str
    contract_sha256: str
    abi_sha256: str
    wrapper: GeneratedOptixWrapper
    wrapper_ptx: str
    wrapper_ptx_sha256: str
    generated_leaves: tuple[GeneratedFormalNumbaLeaf, ...]
    compiled_leaves: tuple[DeviceFunctionArtifact, ...]
    inline_cuda_source_sha256: str
    inline_cuda_leaf_sha256: tuple[tuple[str, str], ...]
    composed: ComposedCallbackPtx
    compiler_options: tuple[str, ...]
    nvrtc_log_sha256: str
    executable_sha256: str


_LIVE_EXECUTABLES: dict[
    int,
    tuple[
        weakref.ReferenceType[VerifiedBoundedRelationExecutable],
        tuple[object, ...],
    ],
] = {}
_LIVE_EXECUTABLES_LOCK = threading.Lock()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _compiler_source_identity() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    names = (
        "_v4_numba_compile_child.py",
        "v4_bounded_relation_optix_compiler.py",
        "v4_bounded_relation_optix_wrapper_codegen.py",
        "v4_callback_numba_codegen.py",
        "v4_callback_ptx_composer.py",
        "v4_inline_cuda_codegen.py",
        "v4_triangle_optix_compiler.py",
    )
    return {name: _file_sha256(root / name) for name in names}


def _compiler_options(
    compute_capability: tuple[int, int],
    optix_include: str | Path,
    cuda_include: str | Path,
) -> tuple[str, ...]:
    return (
        f"-I{Path(optix_include).resolve()}",
        f"-I{Path(cuda_include).resolve()}",
        f"-I{Path(cuda_include).resolve() / 'nv'}",
        "-I/usr/include",
        "-I/usr/include/x86_64-linux-gnu",
        "--std=c++14",
        f"--gpu-architecture=compute_{compute_capability[0]}{compute_capability[1]}",
        "--relocatable-device-code=true",
        "-D__x86_64__=1",
        "-D__LP64__=1",
    )


def _cache_key(
    fresh,
    contract,
    abi,
    any_hit_proof_authority,
    *,
    compute_capability: tuple[int, int],
    accepted_ptx_isa: tuple[str, str],
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    options: tuple[str, ...],
) -> dict[str, object]:
    return {
        "schema": "rtdl.v4.bounded_relation_executable_cache_key.v1",
        "authority_sha256": _authority_sha256(fresh),
        "contract_sha256": contract.contract_sha256,
        "abi_sha256": abi.abi_sha256,
        "proof_sha256": any_hit_proof_authority.proof_sha256,
        "compute_capability": list(compute_capability),
        "accepted_ptx_isa": list(accepted_ptx_isa),
        "python_version": expected_python_version,
        "numba_version": expected_numba_version,
        "numpy_version": expected_numpy_version,
        "compiler_options": list(options),
        "compiler_sources": _compiler_source_identity(),
    }


def _generated_leaf_document(leaf: GeneratedFormalNumbaLeaf) -> dict[str, object]:
    return {
        "schema": leaf.schema,
        "role": leaf.role.value,
        "abi_name": leaf.abi_name,
        "parameter_order": list(leaf.parameter_order),
        "parameter_types": list(leaf.parameter_types),
        "generated_source": leaf.generated_source,
        "generated_source_sha256": leaf.generated_source_sha256,
        "callback_ir_sha256": leaf.callback_ir_sha256,
        "callback_effect_digest": leaf.callback_effect_digest,
        "callback_abi_sha256": leaf.callback_abi_sha256,
        "nonce_word": leaf.nonce_word,
        "numeric_mode": leaf.numeric_mode,
        "error_sites": [[code, path] for code, path in leaf.error_sites],
        "compiler_function_count": leaf.compiler_function_count,
    }


def _load_generated_leaf(value: object) -> GeneratedFormalNumbaLeaf:
    fields = {
        "schema", "role", "abi_name", "parameter_order", "parameter_types",
        "generated_source", "generated_source_sha256", "callback_ir_sha256",
        "callback_effect_digest", "callback_abi_sha256", "nonce_word",
        "numeric_mode", "error_sites", "compiler_function_count",
    }
    if not isinstance(value, dict) or set(value) != fields:
        raise RuntimeError("bounded-relation executable cache leaf shape differs")
    try:
        leaf = GeneratedFormalNumbaLeaf(
            schema=str(value["schema"]),
            role=CallbackRole(str(value["role"])),
            abi_name=str(value["abi_name"]),
            parameter_order=tuple(str(item) for item in value["parameter_order"]),
            parameter_types=tuple(str(item) for item in value["parameter_types"]),
            generated_source=str(value["generated_source"]),
            generated_source_sha256=str(value["generated_source_sha256"]),
            callback_ir_sha256=str(value["callback_ir_sha256"]),
            callback_effect_digest=str(value["callback_effect_digest"]),
            callback_abi_sha256=str(value["callback_abi_sha256"]),
            nonce_word=int(value["nonce_word"]),
            numeric_mode=str(value["numeric_mode"]),
            error_sites=tuple(
                (int(row[0]), str(row[1])) for row in value["error_sites"]
            ),
            compiler_function_count=int(value["compiler_function_count"]),
        )
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise RuntimeError(
            f"bounded-relation executable cache leaf is malformed: {exc}"
        ) from exc
    if hashlib.sha256(leaf.generated_source.encode("utf-8")).hexdigest() \
            != leaf.generated_source_sha256:
        raise RuntimeError("bounded-relation cached generated source digest differs")
    return leaf


def _wrapper_document(wrapper: GeneratedOptixWrapper) -> dict[str, object]:
    return {
        "schema": wrapper.schema,
        "physical_template": wrapper.physical_template,
        "callback_ir_sha256": wrapper.callback_ir_sha256,
        "callback_abi_sha256": wrapper.callback_abi_sha256,
        "source": wrapper.source,
        "source_sha256": wrapper.source_sha256,
        "role_symbols": [list(row) for row in wrapper.role_symbols],
        "linked_role_symbols": wrapper.linked_role_symbols,
    }


def _load_wrapper(value: object) -> GeneratedOptixWrapper:
    fields = {
        "schema", "physical_template", "callback_ir_sha256",
        "callback_abi_sha256", "source", "source_sha256", "role_symbols",
        "linked_role_symbols",
    }
    if not isinstance(value, dict) or set(value) != fields:
        raise RuntimeError("bounded-relation executable cache wrapper shape differs")
    wrapper = GeneratedOptixWrapper(
        schema=str(value["schema"]),
        physical_template=str(value["physical_template"]),
        callback_ir_sha256=str(value["callback_ir_sha256"]),
        callback_abi_sha256=str(value["callback_abi_sha256"]),
        source=str(value["source"]),
        source_sha256=str(value["source_sha256"]),
        role_symbols=tuple(
            (str(row[0]), str(row[1])) for row in value["role_symbols"]
        ),
        linked_role_symbols=bool(value["linked_role_symbols"]),
    )
    if hashlib.sha256(wrapper.source.encode("utf-8")).hexdigest() \
            != wrapper.source_sha256:
        raise RuntimeError("bounded-relation cached wrapper source digest differs")
    return wrapper


def _composed_document(composed: ComposedCallbackPtx) -> dict[str, object]:
    return {
        "ptx": composed.ptx,
        "ptx_sha256": composed.ptx_sha256,
        "ptx_version": composed.ptx_version,
        "ptx_target": composed.ptx_target,
        "address_size": composed.address_size,
        "wrapper_ptx_sha256": composed.wrapper_ptx_sha256,
        "leaf_bindings": [list(row) for row in composed.leaf_bindings],
        "stripped_wrapper_externs": list(composed.stripped_wrapper_externs),
        "stripped_numba_environments": list(composed.stripped_numba_environments),
    }


def _executable_record(
    fresh,
    contract,
    abi,
    *,
    wrapper: GeneratedOptixWrapper,
    composed: ComposedCallbackPtx,
    generated: tuple[GeneratedFormalNumbaLeaf, ...],
    compiled: tuple[DeviceFunctionArtifact, ...],
    inline_cuda_sha256: str,
    inline_leaf_sha256: tuple[tuple[str, str], ...],
    options: tuple[str, ...],
    log: str,
) -> dict[str, object]:
    return {
        "schema": "rtdl.v4.verified_bounded_relation_executable.v1",
        "authority": _authority_sha256(fresh),
        "contract": contract.contract_sha256,
        "abi": abi.abi_sha256,
        "wrapper_source": wrapper.source_sha256,
        "wrapper_ptx": composed.wrapper_ptx_sha256,
        "generated": [item.generated_source_sha256 for item in generated],
        "compiled": [item.ptx_sha256 for item in compiled],
        "inline_cuda": inline_cuda_sha256,
        "inline_cuda_leaves": inline_leaf_sha256,
        "composed": composed.ptx_sha256,
        "options": options,
        "nvrtc_log": hashlib.sha256(log.encode()).hexdigest(),
    }


def _cache_payload(executable: VerifiedBoundedRelationExecutable, log: str) -> dict[str, object]:
    return {
        "schema": "rtdl.v4.bounded_relation_executable_cache_payload.v1",
        "wrapper": _wrapper_document(executable.wrapper),
        "wrapper_ptx": executable.wrapper_ptx,
        "generated_leaves": [
            _generated_leaf_document(item) for item in executable.generated_leaves
        ],
        "compiled_leaves": [
            _device_function_artifact_dict(item) for item in executable.compiled_leaves
        ],
        "inline_cuda_source_sha256": executable.inline_cuda_source_sha256,
        "inline_cuda_leaf_sha256": [list(row) for row in executable.inline_cuda_leaf_sha256],
        "composed": _composed_document(executable.composed),
        "compiler_options": list(executable.compiler_options),
        "nvrtc_log": log,
        "executable_sha256": executable.executable_sha256,
    }


def _load_cached_executable(
    payload: object,
    fresh,
    contract,
    abi,
    *,
    compute_capability: tuple[int, int],
    accepted_ptx_isa: tuple[str, str],
    expected_python_version: str,
    expected_numba_version: str,
    options: tuple[str, ...],
) -> tuple[VerifiedBoundedRelationExecutable, str]:
    fields = {
        "schema", "wrapper", "wrapper_ptx", "generated_leaves",
        "compiled_leaves", "inline_cuda_source_sha256",
        "inline_cuda_leaf_sha256", "composed", "compiler_options",
        "nvrtc_log", "executable_sha256",
    }
    if not isinstance(payload, dict) or set(payload) != fields \
            or payload["schema"] \
            != "rtdl.v4.bounded_relation_executable_cache_payload.v1":
        raise RuntimeError("bounded-relation executable cache payload shape differs")
    generated = tuple(_load_generated_leaf(item) for item in payload["generated_leaves"])
    if tuple(item.role for item in generated) != tuple(CallbackRole) or any(
        item.callback_ir_sha256 != fresh.physical.callback.ir_sha256
        or item.callback_effect_digest != fresh.physical.callback.effect_digest
        or item.callback_abi_sha256 != abi.abi_sha256
        for item in generated
    ):
        raise RuntimeError("bounded-relation cached generated leaf binding differs")
    compiled = tuple(
        _device_function_artifact_from_dict(
            item,
            leaf=leaf,
            compute_capability=compute_capability,
            accepted_ptx_isa=accepted_ptx_isa,
            allowed_external_symbols=frozenset(),
            expected_python_version=expected_python_version,
            expected_numba_version=expected_numba_version,
        )
        for item, leaf in zip(payload["compiled_leaves"], generated, strict=True)
    )
    wrapper = _load_wrapper(payload["wrapper"])
    wrapper_ptx = str(payload["wrapper_ptx"])
    if wrapper.callback_ir_sha256 != fresh.physical.callback.ir_sha256 \
            or wrapper.callback_abi_sha256 != abi.abi_sha256:
        raise RuntimeError("bounded-relation cached wrapper binding differs")
    symbols = {item.role: item.abi_name for item in compiled}
    composed = bind_inline_callback_ptx(
        wrapper_ptx, exact_symbols_by_role=symbols
    )
    if _composed_document(composed) != payload["composed"]:
        raise RuntimeError("bounded-relation cached composed PTX differs")
    inline_leaf_sha256 = tuple(
        (str(row[0]), str(row[1])) for row in payload["inline_cuda_leaf_sha256"]
    )
    log = str(payload["nvrtc_log"])
    record = _executable_record(
        fresh,
        contract,
        abi,
        wrapper=wrapper,
        composed=composed,
        generated=generated,
        compiled=compiled,
        inline_cuda_sha256=str(payload["inline_cuda_source_sha256"]),
        inline_leaf_sha256=inline_leaf_sha256,
        options=options,
        log=log,
    )
    executable_sha256 = _digest(record)
    if list(options) != payload["compiler_options"] \
            or executable_sha256 != payload["executable_sha256"]:
        raise RuntimeError("bounded-relation cached executable identity differs")
    return VerifiedBoundedRelationExecutable(
        schema=str(record["schema"]),
        authority_sha256=str(record["authority"]),
        contract_sha256=contract.contract_sha256,
        abi_sha256=abi.abi_sha256,
        wrapper=wrapper,
        wrapper_ptx=wrapper_ptx,
        wrapper_ptx_sha256=composed.wrapper_ptx_sha256,
        generated_leaves=generated,
        compiled_leaves=compiled,
        inline_cuda_source_sha256=str(payload["inline_cuda_source_sha256"]),
        inline_cuda_leaf_sha256=inline_leaf_sha256,
        composed=composed,
        compiler_options=options,
        nvrtc_log_sha256=str(record["nvrtc_log"]),
        executable_sha256=executable_sha256,
    ), log


_SNAPSHOT_IN_PROGRESS = object()


def _structural_snapshot(
    value: object,
    memo: dict[int, object] | None = None,
) -> object:
    """Freeze verified live inputs without re-running compiler derivations."""

    if memo is None:
        memo = {}
    if isinstance(value, Enum):
        return (
            "enum",
            type(value).__module__,
            type(value).__qualname__,
            value.value,
        )
    if value is None or isinstance(value, (bool, int, float, str, bytes)):
        return value
    if isinstance(value, Path):
        return ("path", str(value))
    identity = id(value)
    if identity in memo:
        snapshot = memo[identity]
        if snapshot is _SNAPSHOT_IN_PROGRESS:
            raise RuntimeError("cyclic live bounded-relation seal value")
        return snapshot
    memo[identity] = _SNAPSHOT_IN_PROGRESS
    if is_dataclass(value) and not isinstance(value, type):
        snapshot = (
            "dataclass",
            type(value).__module__,
            type(value).__qualname__,
            tuple(
                (
                    field.name,
                    _structural_snapshot(getattr(value, field.name), memo),
                )
                for field in fields(value)
            ),
        )
    elif isinstance(value, tuple):
        snapshot = (
            "tuple",
            tuple(_structural_snapshot(item, memo) for item in value),
        )
    elif isinstance(value, list):
        snapshot = (
            "list",
            tuple(_structural_snapshot(item, memo) for item in value),
        )
    elif isinstance(value, Mapping):
        rows = [
            (
                _structural_snapshot(key, memo),
                _structural_snapshot(item, memo),
            )
            for key, item in value.items()
        ]
        snapshot = ("mapping", tuple(sorted(rows, key=repr)))
    elif isinstance(value, (set, frozenset)):
        snapshot = (
            "set",
            tuple(sorted(
                (_structural_snapshot(item, memo) for item in value),
                key=repr,
            )),
        )
    else:
        del memo[identity]
        raise RuntimeError(
            "unsupported live bounded-relation seal value: "
            f"{type(value).__module__}.{type(value).__qualname__}"
        )
    memo[identity] = snapshot
    return snapshot


def _live_seal(
    executable: VerifiedBoundedRelationExecutable,
    authority,
    contract,
    abi,
    proof,
) -> tuple[object, ...]:
    structural = _structural_snapshot((
        authority,
        contract,
        abi,
        proof,
        executable,
    ))
    return (
        structural,
        _authority_sha256(authority),
        contract.contract_sha256,
        abi.abi_sha256,
        proof.proof_sha256,
        executable.executable_sha256,
        executable.authority_sha256,
        executable.contract_sha256,
        executable.abi_sha256,
        hashlib.sha256(executable.wrapper.source.encode("utf-8")).hexdigest(),
        hashlib.sha256(executable.wrapper_ptx.encode("utf-8")).hexdigest(),
        hashlib.sha256(executable.composed.ptx.encode("utf-8")).hexdigest(),
        tuple(
            (
                item.generated_source_sha256,
                hashlib.sha256(item.generated_source.encode("utf-8")).hexdigest(),
            )
            for item in executable.generated_leaves
        ),
        tuple(
            (item.ptx_sha256, hashlib.sha256(item.ptx.encode("utf-8")).hexdigest())
            for item in executable.compiled_leaves
        ),
    )


def _register_live_executable(executable, authority, contract, abi, proof) -> None:
    identity = id(executable)
    seal = _live_seal(
        executable, authority, contract, abi, proof
    )

    def remove_dead(reference) -> None:
        with _LIVE_EXECUTABLES_LOCK:
            current = _LIVE_EXECUTABLES.get(identity)
            if current is not None and current[0] is reference:
                del _LIVE_EXECUTABLES[identity]

    reference = weakref.ref(executable, remove_dead)
    with _LIVE_EXECUTABLES_LOCK:
        current = _LIVE_EXECUTABLES.get(identity)
        if current is not None and current[0]() is not None:
            raise RuntimeError("bounded-relation executable identity collision")
        _LIVE_EXECUTABLES[identity] = (reference, seal)


def _inline_wrapper(
    wrapper: GeneratedOptixWrapper,
    abi: CompiledCallbackAbi,
    leaves: tuple[GeneratedFormalNumbaLeaf, ...],
) -> tuple[GeneratedOptixWrapper, str, tuple[tuple[str, str], ...]]:
    if not leaves or any(
            leaf.callback_ir_sha256 != abi.callback_ir_sha256
            or leaf.callback_effect_digest != abi.callback_effect_digest
            for leaf in leaves):
        raise RuntimeError(
            "bounded-relation fused lowering requires the exact standard "
            "callback IR and effect projection")
    roles = {item.role: item for item in abi.roles}
    trusted_finite = {
        role.value: frozenset(
            _parameter_name(field.path)
            for field in roles[role].inputs
            if field.scalar == "f32" or field.scalar == "device_ptr<f32>"
        )
        for role in CallbackRole
    }
    definitions, leaf_identities = lower_formal_leaves_to_inline_cuda(
        leaves,
        trusted_finite_inputs_by_role=trusted_finite,
        # These exact emitter error-code/site pairs are discharged by
        # ``v4_relation_boxes`` before any GAS/cache/launch publication.  The
        # inline lowerer requires every listed pair to exist and removes no
        # unlisted failure guard.  ANY_HIT is deliberately absent: its checked
        # U32 payload increment remains a dynamic device obligation.
        proven_failure_guards_by_role={
            CallbackRole.BOUNDS.value: frozenset(
                [(2, site) for site in range(1, 7)]
                + [(3, site) for site in range(7, 13)]
                + [(10, 13)]),
            CallbackRole.MAKE_RAY.value: frozenset(
                [(7, 1)]
                + [(2, site) for site in range(2, 8)]
                + [(3, site) for site in range(8, 18)]
                + [(9, 18)]
                + [(3, site) for site in range(19, 29)]
                + [(9, 29)]),
            CallbackRole.INTERSECTION.value: frozenset(
                [(2, site) for site in range(1, 15)]
                + [(3, 15), (3, 16), (3, 17), (11, 18)]),
            CallbackRole.CLOSEST_HIT.value: frozenset({(2, 1)}),
            CallbackRole.MISS.value: frozenset(
                (2, site) for site in range(1, 9)),
        },
    )
    prototypes = "\n".join(_prototype(roles[role]) for role in CallbackRole)
    if wrapper.source.count(prototypes) != 1:
        raise RuntimeError("bounded-relation wrapper prototype anchor drift")
    source = wrapper.source.replace(
        prototypes, prototypes + "\n\n" + definitions, 1)
    source_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return (
        replace(wrapper, source=source, source_sha256=source_sha256),
        hashlib.sha256(definitions.encode("utf-8")).hexdigest(),
        leaf_identities,
    )


class _BoundedRelationEmitter(_Emitter):
    """Checked integer addition needed by payload counters.

    This extends only the frozen verified IR-to-Numba emitter.  It does not
    accept Python callables or arbitrary device code.
    """

    def _numeric(self, op, left, right, result_type, path):
        kinds = _leaf_scalar_kinds(result_type, self.records)
        if op != "add" or not all(
                kind in {ScalarKind.I32, ScalarKind.U32,
                         ScalarKind.I64, ScalarKind.U64}
                for kind in kinds):
            return super()._numeric(op, left, right, result_type, path)
        leaves: list[str] = []
        for a, b, kind in zip(left.leaves, right.leaves, kinds):
            low, high = _integer_bounds(kind)
            if low == 0:
                self.emit(f"if {b} > {high} - {a}:")
            else:
                self.emit(
                    f"if ({b} > 0 and {a} > {high} - {b}) or "
                    f"({b} < 0 and {a} < {low} - {b}):")
            with self.block():
                self.emit_failure(RuntimeStatus.INTEGER_OVERFLOW, path)
            temp = self.temp("checked_add")
            self.emit(f"{temp} = {a} + {b}")
            leaves.append(temp)
        return _Value(result_type, tuple(leaves))


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _authority_sha256(authority: VerifiedBoundedRelationAuthority) -> str:
    return _digest({
        "callback": authority.physical.callback.ir_sha256,
        "effect": authority.physical.callback.effect_digest,
        "physical_schema": authority.physical.schema.schema_sha256,
        "target": authority.physical.target.target_sha256,
        "relation_schema": authority.schema.schema_sha256,
        "nonce": authority.authority_nonce,
    })


def _fresh(authority, contract, abi, any_hit_proof_authority):
    fresh = verify_bounded_relation_schema(authority.physical, authority.schema)
    if fresh != authority:
        raise RuntimeError("bounded-relation authority does not rederive")
    expected_abi = verify_compiled_callback_abi(
        abi, fresh.physical.callback,
        any_hit_proof_authority=any_hit_proof_authority,
        physical_schema_authority=fresh.physical)
    if expected_abi != abi:
        raise RuntimeError("bounded-relation ABI binding drift")
    expected_contract = compile_bounded_relation_contract(
        fresh, abi_sha256=abi.abi_sha256)
    if expected_contract != contract or contract.executable:
        raise RuntimeError("exact non-executable relation contract is required")
    return fresh


def generate_bounded_relation_numba_leaf(
    authority: VerifiedBoundedRelationAuthority,
    abi: CompiledCallbackAbi,
    role: CallbackRole,
    *,
    any_hit_proof_authority,
) -> GeneratedFormalNumbaLeaf:
    fresh = verify_bounded_relation_schema(authority.physical, authority.schema)
    if fresh != authority:
        raise RuntimeError("bounded-relation authority does not rederive")
    if verify_compiled_callback_abi(
            abi, fresh.physical.callback,
            any_hit_proof_authority=any_hit_proof_authority,
            physical_schema_authority=fresh.physical) != abi:
        raise RuntimeError("bounded-relation ABI binding drift")
    role_abi = next((item for item in abi.roles if item.role is role), None)
    if role_abi is None:
        raise RuntimeError(f"role is absent from ABI: {role.value}")
    function = fresh.physical.callback.program.function_for_role(role)
    emitter = _BoundedRelationEmitter(
        verified=fresh.physical.callback, abi=abi, role_abi=role_abi)
    for helper in sorted(emitter.helpers.values(), key=lambda item: item.name):
        _emit_helper(emitter, helper)
        emitter.emit()
    emitter.emit_role(function)
    source = "\n".join(emitter.lines) + "\n"
    compile(source, "<rtdl-v4-generated-bounded-relation>", "exec")
    return GeneratedFormalNumbaLeaf(
        schema=FORMAL_NUMBA_SOURCE_SCHEMA,
        role=role,
        abi_name=role_abi.symbol,
        parameter_order=role_abi.parameter_order,
        parameter_types=_parameter_types(role_abi),
        generated_source=source,
        generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        callback_ir_sha256=fresh.physical.callback.ir_sha256,
        callback_effect_digest=fresh.physical.callback.effect_digest,
        callback_abi_sha256=abi.abi_sha256,
        nonce_word=role_abi.nonce_word,
        numeric_mode="strict",
        error_sites=tuple(emitter.sites),
        compiler_function_count=1 + len(_reachable_helpers(function, emitter.helpers)),
    )


def compile_verified_bounded_relation_executable(
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
    *,
    any_hit_proof_authority,
    compute_capability: tuple[int, int],
    optix_include: str | Path,
    cuda_include: str | Path,
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    accepted_ptx_isa: tuple[str, str] = ("8.0", "9.0"),
    python_executable: str = sys.executable,
    formal_leaf_cache: FormalNumbaLeafCachePolicy | None = None,
    executable_cache: V4ExecutableCachePolicy | None = None,
) -> tuple[VerifiedBoundedRelationExecutable, str]:
    fresh = _fresh(authority, contract, abi, any_hit_proof_authority)
    if compute_capability != tuple(
            int(item) for item in fresh.physical.target.compute_capability.split(".")):
        raise RuntimeError("target compute capability does not match authority")
    if executable_cache is not None and not isinstance(
            executable_cache, V4ExecutableCachePolicy):
        raise TypeError("executable_cache must be V4ExecutableCachePolicy or None")
    options = _compiler_options(
        compute_capability,
        optix_include,
        cuda_include,
    )
    cache_key = _cache_key(
        fresh,
        contract,
        abi,
        any_hit_proof_authority,
        compute_capability=compute_capability,
        accepted_ptx_isa=accepted_ptx_isa,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
        options=options,
    )
    if executable_cache is not None:
        cached = load_executable_cache_entry(executable_cache, cache_key)
        if cached is not None:
            executable, log = _load_cached_executable(
                cached,
                fresh,
                contract,
                abi,
                compute_capability=compute_capability,
                accepted_ptx_isa=accepted_ptx_isa,
                expected_python_version=expected_python_version,
                expected_numba_version=expected_numba_version,
                options=options,
            )
            _register_live_executable(
                executable,
                authority,
                contract,
                abi,
                any_hit_proof_authority,
            )
            return executable, log
    generated: list[GeneratedFormalNumbaLeaf] = []
    for role in CallbackRole:
        leaf = generate_bounded_relation_numba_leaf(
            fresh, abi, role,
            any_hit_proof_authority=any_hit_proof_authority)
        generated.append(leaf)
    compiled = list(compile_formal_numba_leaves_isolated(
        generated,
        compute_capability=compute_capability,
        accepted_ptx_isa=accepted_ptx_isa,
        allowed_external_symbols=frozenset(),
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
        python_executable=python_executable,
        formal_leaf_cache=formal_leaf_cache,
    ))
    symbols = {
        role.value: artifact.abi_name
        for role, artifact in zip(CallbackRole, compiled, strict=True)
    }
    base_wrapper = generate_trusted_bounded_relation_wrapper_v1(
        fresh, contract, abi,
        any_hit_proof_authority=any_hit_proof_authority)
    wrapper, inline_cuda_sha256, inline_leaf_sha256 = _inline_wrapper(
        base_wrapper, abi, tuple(generated))
    wrapper_ptx, log = _compile_nvrtc(wrapper.source, options)
    composed = bind_inline_callback_ptx(
        wrapper_ptx, exact_symbols_by_role=symbols)
    generated_tuple = tuple(generated)
    compiled_tuple = tuple(compiled)
    record = _executable_record(
        fresh,
        contract,
        abi,
        wrapper=wrapper,
        composed=composed,
        generated=generated_tuple,
        compiled=compiled_tuple,
        inline_cuda_sha256=inline_cuda_sha256,
        inline_leaf_sha256=inline_leaf_sha256,
        options=options,
        log=log,
    )
    executable = VerifiedBoundedRelationExecutable(
        schema=record["schema"], authority_sha256=record["authority"],
        contract_sha256=contract.contract_sha256, abi_sha256=abi.abi_sha256,
        wrapper=wrapper, wrapper_ptx=wrapper_ptx,
        wrapper_ptx_sha256=composed.wrapper_ptx_sha256,
        generated_leaves=generated_tuple, compiled_leaves=compiled_tuple,
        inline_cuda_source_sha256=inline_cuda_sha256,
        inline_cuda_leaf_sha256=inline_leaf_sha256,
        composed=composed, compiler_options=options,
        nvrtc_log_sha256=record["nvrtc_log"],
        executable_sha256=_digest(record),
    )
    if executable_cache is not None:
        store_executable_cache_entry(
            executable_cache,
            cache_key,
            _cache_payload(executable, log),
        )
    _register_live_executable(
        executable,
        authority,
        contract,
        abi,
        any_hit_proof_authority,
    )
    return executable, log


def consume_verified_bounded_relation_executable(
    executable: VerifiedBoundedRelationExecutable,
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
    *,
    any_hit_proof_authority,
) -> str:
    if not isinstance(executable, VerifiedBoundedRelationExecutable):
        raise TypeError("live VerifiedBoundedRelationExecutable is required")
    with _LIVE_EXECUTABLES_LOCK:
        registered = _LIVE_EXECUTABLES.pop(id(executable), None)
    if registered is None or registered[0]() is not executable:
        raise RuntimeError("bounded-relation executable is forged, serialized, or consumed")
    expected_live_seal = registered[1]
    observed_live_seal = _live_seal(
        executable,
        authority,
        contract,
        abi,
        any_hit_proof_authority,
    )
    if observed_live_seal != expected_live_seal:
        raise RuntimeError("bounded-relation executable binding drift")
    return executable.composed.ptx


__all__ = [
    "VerifiedBoundedRelationExecutable",
    "compile_verified_bounded_relation_executable",
    "consume_verified_bounded_relation_executable",
    "generate_bounded_relation_numba_leaf",
]
