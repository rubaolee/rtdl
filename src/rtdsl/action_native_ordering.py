from __future__ import annotations

import ctypes
from dataclasses import dataclass, field
from functools import lru_cache
import hashlib
import hmac
from pathlib import Path
import secrets
from typing import Mapping

from .action_native_identity import (
    ActionNativeLibraryIdentity,
    native_library_identity,
    validate_native_library_identity,
)


GROUPED_I64X2_NATIVE_ORDER_SYMBOL = "rtdl_cuda_sort_i64_f64_i64_i64_lex"
_GROUPED_NATIVE_ORDER_CONTEXT_SEAL_KEY = secrets.token_bytes(32)


@dataclass(frozen=True)
class GroupedI64x2NativeOrderContext:
    """Compiler-bound native ordering resource, separate from continuation code.

    A full binary/ABI identity is established when the context is created and
    when a plan binds it.  Calls on the hot path revalidate only the already
    loaded object, handle, symbol, normalized path, and process-local seal.
    """

    library_ref: object = field(repr=False, compare=False)
    symbol_ref: object = field(repr=False, compare=False)
    library_identity: ActionNativeLibraryIdentity
    process_handle: int
    symbol_object_id: int
    _compiler_seal: str = field(default="", repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.library_identity, ActionNativeLibraryIdentity):
            raise TypeError("library_identity must be an ActionNativeLibraryIdentity")
        unsigned = self._seal_payload()
        object.__setattr__(
            self,
            "_compiler_seal",
            hmac.new(
                _GROUPED_NATIVE_ORDER_CONTEXT_SEAL_KEY,
                unsigned,
                hashlib.sha256,
            ).hexdigest(),
        )

    def _seal_payload(self) -> bytes:
        return repr(
            (
                "rtdl.grouped_i64x2_native_order_context.seal.v1",
                id(self.library_ref),
                id(self.symbol_ref),
                int(self.process_handle),
                int(self.symbol_object_id),
                self.library_identity.identity_digest,
                GROUPED_I64X2_NATIVE_ORDER_SYMBOL,
            )
        ).encode("utf-8")

    def validate_hot_binding(self) -> None:
        """O(1) validation of the exact process resources bound by planning."""

        from . import optix_runtime

        library = optix_runtime._load_optix_library()
        symbol = optix_runtime._find_optional_backend_symbol(
            library,
            GROUPED_I64X2_NATIVE_ORDER_SYMBOL,
        )
        raw_path = getattr(library, "_rtdl_library_path", None)
        try:
            resolved_path = str(Path(raw_path).expanduser().resolve(strict=True))
        except (OSError, TypeError, ValueError) as exc:
            raise RuntimeError("native ordering library path is invalid") from exc
        expected_seal = hmac.new(
            _GROUPED_NATIVE_ORDER_CONTEXT_SEAL_KEY,
            self._seal_payload(),
            hashlib.sha256,
        ).hexdigest()
        if (
            library is not self.library_ref
            or symbol is not self.symbol_ref
            or getattr(library, "_handle", None) != self.process_handle
            or id(symbol) != self.symbol_object_id
            or resolved_path != self.library_identity.resolved_path
            or not hmac.compare_digest(self._compiler_seal, expected_seal)
        ):
            raise RuntimeError(
                "native ordering library, handle, symbol, path, or compiler seal changed"
            )

    def validate_full_identity(self) -> None:
        """Recompute binary, version, required-symbol, path, and handle identity."""

        self.validate_hot_binding()
        validate_native_library_identity(self.library_ref, self.library_identity)

    @staticmethod
    def _pointer(value, name: str) -> int:
        interface = getattr(value, "__cuda_array_interface__", None)
        if not isinstance(interface, Mapping):
            raise TypeError(f"{name} must expose a CUDA array interface")
        pointer = interface.get("data", (None,))[0]
        if pointer is None:
            raise ValueError(f"{name} CUDA pointer is missing")
        return int(pointer)

    def sort_i64_f64_i64_i64(
        self,
        key0,
        key1,
        key2,
        order_key,
        *,
        row_count: int,
    ) -> dict[str, object]:
        self.validate_hot_binding()
        symbol = self.symbol_ref
        symbol.argtypes = [
            ctypes.c_uint64,
            ctypes.c_uint64,
            ctypes.c_uint64,
            ctypes.c_uint64,
            ctypes.c_uint64,
            ctypes.c_char_p,
            ctypes.c_uint64,
        ]
        symbol.restype = ctypes.c_int
        error = ctypes.create_string_buffer(4096)
        status = symbol(
            ctypes.c_uint64(self._pointer(key0, "key0")),
            ctypes.c_uint64(self._pointer(key1, "key1")),
            ctypes.c_uint64(self._pointer(key2, "key2")),
            ctypes.c_uint64(self._pointer(order_key, "order_key")),
            ctypes.c_uint64(int(row_count)),
            error,
            ctypes.c_uint64(len(error)),
        )
        if int(status) != 0:
            message = error.value.decode("utf-8", errors="replace").strip()
            raise RuntimeError(message or f"native grouped order failed with status {status}")
        return {
            "contract": "rtdl.grouped_i64x2_native_order_context.v1",
            "backend": "native_thrust_lexsort_i64_f64_i64_i64",
            "required_symbol": GROUPED_I64X2_NATIVE_ORDER_SYMBOL,
            "row_count": int(row_count),
            "library_identity_digest": self.library_identity.identity_digest,
            "exact_library_object_revalidated": True,
            "exact_symbol_object_revalidated": True,
            "device_resident": True,
        }

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.grouped_i64x2_native_order_context.v1",
            "available": True,
            "required_symbol": GROUPED_I64X2_NATIVE_ORDER_SYMBOL,
            "library_identity": self.library_identity.to_metadata(),
            "library_object_id": id(self.library_ref),
            "symbol_object_id": self.symbol_object_id,
            "process_handle": str(self.process_handle),
            "compiler_sealed": True,
            "native_identity_hashed_at_context_creation": True,
            "hot_validation_is_exact_object_path_handle_symbol_and_seal": True,
        }


@dataclass(frozen=True)
class GroupedI64x2NativeOrderProbe:
    available: bool
    context: GroupedI64x2NativeOrderContext | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    error: str | None = None

    @property
    def library_ref(self):
        return self.context.library_ref if self.context is not None else None

    @property
    def library_identity(self):
        return self.context.library_identity if self.context is not None else None

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.grouped_i64x2_native_order_probe.v1",
            "available": self.available,
            "context": self.context.to_metadata() if self.context is not None else None,
            "error": self.error,
            "availability_derived_from_numba_flag_only": False,
        }


@lru_cache(maxsize=1)
def probe_grouped_i64x2_native_order() -> GroupedI64x2NativeOrderProbe:
    """Load and bind the exact generic CUDA ordering helper once per process."""

    try:
        from . import optix_runtime

        library = optix_runtime._load_optix_library()
        symbol = optix_runtime._find_optional_backend_symbol(
            library,
            GROUPED_I64X2_NATIVE_ORDER_SYMBOL,
        )
        if symbol is None:
            raise RuntimeError(
                f"missing native symbol {GROUPED_I64X2_NATIVE_ORDER_SYMBOL}"
            )
        identity = native_library_identity(
            library,
            required_symbols=(GROUPED_I64X2_NATIVE_ORDER_SYMBOL,),
        )
        context = GroupedI64x2NativeOrderContext(
            library_ref=library,
            symbol_ref=symbol,
            library_identity=identity,
            process_handle=int(getattr(library, "_handle")),
            symbol_object_id=id(symbol),
        )
        context.validate_full_identity()
        return GroupedI64x2NativeOrderProbe(available=True, context=context)
    except Exception as exc:
        return GroupedI64x2NativeOrderProbe(
            available=False,
            error=f"{type(exc).__name__}: {exc}",
        )


__all__ = (
    "GROUPED_I64X2_NATIVE_ORDER_SYMBOL",
    "GroupedI64x2NativeOrderContext",
    "GroupedI64x2NativeOrderProbe",
    "probe_grouped_i64x2_native_order",
)
