from __future__ import annotations

from dataclasses import dataclass
import importlib
from typing import Any, Protocol


FALLBACK_MODES = ("error", "copy", "host_stage")
DEVICE_TYPES = ("cpu", "cuda")
ACCESS_MODES = ("read", "write", "readwrite")


@dataclass(frozen=True)
class RtdlTensorDescriptor:
    data_ptr: int | None
    device_type: str
    device_id: int
    dtype: str
    shape: tuple[int, ...]
    strides: tuple[int, ...] | None = None
    byte_offset: int = 0
    access_mode: str = "read"
    stream_handle: int = 0
    owner: Any = None
    source_protocol: str = "python"

    def __post_init__(self) -> None:
        _validate_device(self.device_type, self.device_id)
        _validate_access_mode(self.access_mode)
        if any(int(dim) < 0 for dim in self.shape):
            raise ValueError("tensor descriptor shape dimensions must be non-negative")
        if self.strides is not None and len(self.strides) != len(self.shape):
            raise ValueError("tensor descriptor strides must match shape rank")
        if self.byte_offset < 0:
            raise ValueError("tensor descriptor byte_offset must be non-negative")
        if self.stream_handle != 0:
            raise ValueError("v1.7 partner descriptors reserve stream_handle; expected 0")


@dataclass(frozen=True)
class RtdlOutputSpec:
    dtype: str
    shape: tuple[int, ...]
    device_type: str
    device_id: int = 0
    required_contiguous: bool = True
    required_alignment_bytes: int = 1
    access_mode: str = "write"
    fallback_policy: str = "error"

    def __post_init__(self) -> None:
        _validate_device(self.device_type, self.device_id)
        _validate_access_mode(self.access_mode)
        _validate_fallback_policy(self.fallback_policy)
        if any(int(dim) < 0 for dim in self.shape):
            raise ValueError("output spec shape dimensions must be non-negative")
        if self.required_alignment_bytes <= 0:
            raise ValueError("required_alignment_bytes must be positive")


class PartnerAdapter(Protocol):
    name: str

    def can_export(self, obj: Any) -> bool:
        ...

    def export_tensor(
        self,
        obj: Any,
        *,
        access: str = "read",
        stream: int | None = None,
    ) -> RtdlTensorDescriptor:
        ...

    def allocate_output(self, spec: RtdlOutputSpec, *, stream: int | None = None) -> Any:
        ...

    def import_output(self, descriptor: RtdlTensorDescriptor) -> Any:
        ...


class GenericDLPackAdapter:
    name = "dlpack"

    def can_export(self, obj: Any) -> bool:
        return callable(getattr(obj, "__dlpack__", None)) and callable(getattr(obj, "__dlpack_device__", None))

    def export_tensor(
        self,
        obj: Any,
        *,
        access: str = "read",
        stream: int | None = None,
    ) -> RtdlTensorDescriptor:
        _validate_access_mode(access)
        if stream not in (None, 0):
            raise ValueError("v1.7 partner descriptors reserve stream_handle; expected 0")
        if not self.can_export(obj):
            raise TypeError("object does not implement __dlpack__ and __dlpack_device__")
        device_type, device_id = _normalize_dlpack_device(obj.__dlpack_device__())
        dtype = _dtype_name(obj)
        shape = _shape_tuple(obj)
        strides = _strides_tuple(obj)
        return RtdlTensorDescriptor(
            data_ptr=_data_ptr(obj),
            device_type=device_type,
            device_id=device_id,
            dtype=dtype,
            shape=shape,
            strides=strides,
            access_mode=access,
            stream_handle=0,
            owner=obj,
            source_protocol="dlpack",
        )

    def allocate_output(self, spec: RtdlOutputSpec, *, stream: int | None = None) -> Any:
        raise NotImplementedError("generic DLPack adapter cannot allocate framework-owned outputs")

    def import_output(self, descriptor: RtdlTensorDescriptor) -> Any:
        raise NotImplementedError("generic DLPack adapter cannot import outputs without a framework")


class PyTorchAdapter(GenericDLPackAdapter):
    name = "torch"

    def can_export(self, obj: Any) -> bool:
        return _module_root(obj) == "torch" and super().can_export(obj)

    def export_tensor(
        self,
        obj: Any,
        *,
        access: str = "read",
        stream: int | None = None,
    ) -> RtdlTensorDescriptor:
        if bool(getattr(obj, "requires_grad", False)):
            raise ValueError("grad-enabled PyTorch tensors must be detached before RTDL export")
        descriptor = super().export_tensor(obj, access=access, stream=stream)
        return _replace_source_protocol(descriptor, "torch")

    def allocate_output(self, spec: RtdlOutputSpec, *, stream: int | None = None) -> Any:
        if stream not in (None, 0):
            raise ValueError("v1.7 partner descriptors reserve stream_handle; expected 0")
        torch = importlib.import_module("torch")
        dtype = getattr(torch, spec.dtype, spec.dtype)
        return torch.empty(spec.shape, dtype=dtype, device=f"{spec.device_type}:{spec.device_id}")


class CuPyAdapter(GenericDLPackAdapter):
    name = "cupy"

    def can_export(self, obj: Any) -> bool:
        return _module_root(obj) == "cupy" and super().can_export(obj)

    def export_tensor(
        self,
        obj: Any,
        *,
        access: str = "read",
        stream: int | None = None,
    ) -> RtdlTensorDescriptor:
        descriptor = super().export_tensor(obj, access=access, stream=stream)
        return _replace_source_protocol(descriptor, "cupy")

    def allocate_output(self, spec: RtdlOutputSpec, *, stream: int | None = None) -> Any:
        if stream not in (None, 0):
            raise ValueError("v1.7 partner descriptors reserve stream_handle; expected 0")
        cupy = importlib.import_module("cupy")
        return cupy.empty(spec.shape, dtype=spec.dtype)


class PartnerContext:
    def __init__(self, adapter: PartnerAdapter | None, *, fallback: str = "error") -> None:
        _validate_fallback_policy(fallback)
        self.adapter = adapter
        self.fallback = fallback
        self.name = "none" if adapter is None else adapter.name

    def tensor(self, obj: Any, *, access: str = "read", stream: int | None = None) -> RtdlTensorDescriptor:
        if self.adapter is None:
            raise TypeError("partner='none' cannot export partner-owned tensors")
        return self.adapter.export_tensor(obj, access=access, stream=stream)

    def empty(self, shape: tuple[int, ...], *, dtype: str, device: str = "cpu:0") -> Any:
        if self.adapter is None:
            raise TypeError("partner='none' cannot allocate partner-owned outputs")
        device_type, device_id = _parse_device(device)
        spec = RtdlOutputSpec(
            dtype=dtype,
            shape=tuple(int(dim) for dim in shape),
            device_type=device_type,
            device_id=device_id,
            fallback_policy=self.fallback,
        )
        return self.adapter.allocate_output(spec, stream=None)


def register(adapter: PartnerAdapter) -> PartnerAdapter:
    name = getattr(adapter, "name", None)
    if not isinstance(name, str) or not name:
        raise ValueError("partner adapter must define a non-empty string name")
    normalized = _normalize_name(name)
    _ADAPTERS[normalized] = adapter
    return adapter


def registered() -> tuple[str, ...]:
    return tuple(sorted(_ADAPTERS))


def get(name: str) -> PartnerAdapter:
    normalized = _normalize_name(name)
    try:
        return _ADAPTERS[normalized]
    except KeyError as exc:
        raise KeyError(f"unknown partner adapter: {name}") from exc


def use(name: str = "none", *, fallback: str = "error") -> PartnerContext:
    normalized = _normalize_name(name)
    if normalized == "none":
        return PartnerContext(None, fallback=fallback)
    return PartnerContext(get(normalized), fallback=fallback)


def auto(obj: Any, *, fallback: str = "error") -> PartnerContext:
    for name, adapter in _ADAPTERS.items():
        if name == "dlpack":
            continue
        if adapter.can_export(obj):
            return PartnerContext(adapter, fallback=fallback)
    if _GENERIC_DLPACK.can_export(obj):
        return PartnerContext(_GENERIC_DLPACK, fallback=fallback)
    raise TypeError("no registered partner adapter can export object")


def _normalize_name(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def _module_root(obj: Any) -> str:
    return obj.__class__.__module__.split(".", 1)[0]


def _replace_source_protocol(descriptor: RtdlTensorDescriptor, source_protocol: str) -> RtdlTensorDescriptor:
    return RtdlTensorDescriptor(
        data_ptr=descriptor.data_ptr,
        device_type=descriptor.device_type,
        device_id=descriptor.device_id,
        dtype=descriptor.dtype,
        shape=descriptor.shape,
        strides=descriptor.strides,
        byte_offset=descriptor.byte_offset,
        access_mode=descriptor.access_mode,
        stream_handle=descriptor.stream_handle,
        owner=descriptor.owner,
        source_protocol=source_protocol,
    )


def _validate_fallback_policy(fallback: str) -> None:
    if fallback not in FALLBACK_MODES:
        raise ValueError(f"fallback must be one of {FALLBACK_MODES}")


def _validate_access_mode(access: str) -> None:
    if access not in ACCESS_MODES:
        raise ValueError(f"access mode must be one of {ACCESS_MODES}")


def _validate_device(device_type: str, device_id: int) -> None:
    if device_type not in DEVICE_TYPES:
        raise ValueError(f"device_type must be one of {DEVICE_TYPES}")
    if device_id < 0:
        raise ValueError("device_id must be non-negative")


def _parse_device(device: str) -> tuple[str, int]:
    if ":" in device:
        device_type, raw_id = device.split(":", 1)
        return device_type, int(raw_id)
    return device, 0


def _normalize_dlpack_device(device: Any) -> tuple[str, int]:
    if not isinstance(device, tuple) or len(device) != 2:
        raise ValueError("__dlpack_device__ must return a two-item tuple")
    raw_type, raw_id = device
    device_id = int(raw_id)
    if isinstance(raw_type, str):
        device_type = raw_type.lower()
    else:
        # DLPack kDLCPU is 1 and kDLCUDA is 2.
        device_type = {1: "cpu", 2: "cuda"}.get(int(raw_type), f"dlpack_{int(raw_type)}")
    _validate_device(device_type, device_id)
    return device_type, device_id


def _dtype_name(obj: Any) -> str:
    dtype = getattr(obj, "dtype", None)
    if dtype is None:
        return "unknown"
    return str(dtype)


def _shape_tuple(obj: Any) -> tuple[int, ...]:
    shape = getattr(obj, "shape", None)
    if shape is None:
        return ()
    return tuple(int(dim) for dim in shape)


def _strides_tuple(obj: Any) -> tuple[int, ...] | None:
    strides = getattr(obj, "strides", None)
    if strides is None:
        return None
    return tuple(int(stride) for stride in strides)


def _data_ptr(obj: Any) -> int | None:
    data_ptr = getattr(obj, "data_ptr", None)
    if callable(data_ptr):
        return int(data_ptr())

    cuda_array = getattr(obj, "__cuda_array_interface__", None)
    if isinstance(cuda_array, dict):
        data = cuda_array.get("data")
        if isinstance(data, tuple) and data:
            return int(data[0])

    array = getattr(obj, "__array_interface__", None)
    if isinstance(array, dict):
        data = array.get("data")
        if isinstance(data, tuple) and data:
            return int(data[0])

    return None


_ADAPTERS: dict[str, PartnerAdapter] = {}
register(PyTorchAdapter())
register(CuPyAdapter())
_GENERIC_DLPACK = register(GenericDLPackAdapter())
