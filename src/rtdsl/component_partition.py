from __future__ import annotations

from collections.abc import Iterable, Sequence


def canonical_partition_labels(labels: Iterable[int], *, noise_label: int = -1) -> tuple[int, ...]:
    """Return labels canonicalized by first occurrence, preserving noise."""

    label_map: dict[int, int] = {}
    canonical: list[int] = []
    for raw_label in labels:
        label = int(raw_label)
        if label == int(noise_label) or label < 0:
            canonical.append(int(noise_label))
            continue
        if label not in label_map:
            label_map[label] = len(label_map)
        canonical.append(label_map[label])
    return tuple(canonical)


def component_signature_from_partition(
    labels: Iterable[int],
    *,
    core_count: int | None = None,
    core_flags: Sequence[int | bool] | None = None,
    noise_label: int = -1,
) -> dict[str, object]:
    """Summarize a component partition without depending on concrete label IDs."""

    canonical = canonical_partition_labels(labels, noise_label=noise_label)
    sizes: dict[int, int] = {}
    noise_count = 0
    for label in canonical:
        if int(label) == int(noise_label):
            noise_count += 1
        else:
            sizes[int(label)] = sizes.get(int(label), 0) + 1
    if core_count is None:
        if core_flags is None:
            raise ValueError("core_count or core_flags must be provided")
        core_count = sum(1 for value in core_flags if bool(value))
    component_sizes = sorted(sizes.values())
    return {
        "core_count": int(core_count),
        "component_count": len(component_sizes),
        "component_sizes": component_sizes,
        "noise_count": int(noise_count),
    }


def partition_equivalent(left: Iterable[int], right: Iterable[int], *, noise_label: int = -1) -> bool:
    """Compare two point partitions modulo nonnegative component-label renaming."""

    return canonical_partition_labels(left, noise_label=noise_label) == canonical_partition_labels(
        right,
        noise_label=noise_label,
    )


__all__ = [
    "canonical_partition_labels",
    "component_signature_from_partition",
    "partition_equivalent",
]
