from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import cmp_to_key
import math
from pathlib import Path
import re
import struct
from typing import Iterable, Literal


RT_BARNESHUT_AUTHOR_CONTRACT_VERSION = "rtdl.rt_barneshut.author_contract.v1"
RT_BARNESHUT_AUTHOR_COMMIT = "2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7"
RT_BARNESHUT_BUCKET_SIZE = 32
RT_BARNESHUT_THRESHOLD = 0.5
RT_BARNESHUT_GRAVITATIONAL_CONSTANT = 0.1


RtBarnesHutFileType = Literal["treelogy", "csv"]


@dataclass(frozen=True)
class RtBarnesHutPoint:
    mass: float
    x: float
    y: float
    z: float
    id: int


@dataclass(frozen=True)
class RtBarnesHutDataset:
    file_type: RtBarnesHutFileType
    path: str
    point_count: int
    header_values: tuple[float, ...]
    author_scaling_applied: bool
    points: tuple[RtBarnesHutPoint, ...]

    def without_points(self) -> dict[str, object]:
        payload = asdict(self)
        payload.pop("points", None)
        return payload


@dataclass
class _Node:
    cofm_x: float
    cofm_y: float
    cofm_z: float
    s: float
    point_id: int = -1
    mass: float = 0.0
    node_type: str = "leaf"
    children: list["_Node | None"] | None = None
    particles: list[int] | None = None
    dfs_index: int = 0

    def __post_init__(self) -> None:
        if self.children is None:
            self.children = [None] * 8
        if self.particles is None:
            self.particles = []


@dataclass(frozen=True)
class RtBarnesHutCpuOracleSummary:
    contract_version: str
    file_type: RtBarnesHutFileType
    source_path: str
    point_count: int
    bucket_size: int
    theta: float
    grid_size: float
    node_count: int
    leaf_count: int
    force_checksum: float
    force_abs_checksum: float
    force_min: float
    force_max: float
    first_forces: tuple[float, ...]
    claim_boundary: dict[str, bool | str]


def _float32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _float_to_uint(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", _float32(value)))[0]


def _float_exp(bits: int) -> int:
    unsigned = bits & 0x7FFFFFFF
    if unsigned == 0 or unsigned >= 0x7F800000:
        return 0
    unsigned >>= 23
    return -126 if unsigned == 0 else int(unsigned) - 127


def _float_sig(bits: int) -> int:
    return bits & 0x007FFFFF


def _uint_log2(value: int) -> int:
    if value <= 0:
        raise ValueError("uint log2 requires a positive integer")
    return value.bit_length() - 1


def _float_xor_msb(p: float, q: float) -> int:
    p = _float32(p)
    q = _float32(q)
    if p == q or p == -q:
        return -2**31
    p_bits = _float_to_uint(p)
    q_bits = _float_to_uint(q)
    p_exp = _float_exp(p_bits)
    q_exp = _float_exp(q_bits)
    if p_exp == q_exp:
        sig_xor = _float_sig(p_bits) ^ _float_sig(q_bits)
        if sig_xor > 0:
            return p_exp + _uint_log2(sig_xor) - 23
        return p_exp
    return max(p_exp, q_exp)


def _zorder_compare(left: RtBarnesHutPoint, right: RtBarnesHutPoint) -> int:
    p = (_float32(left.x), _float32(left.y), _float32(left.z))
    q = (_float32(right.x), _float32(right.y), _float32(right.z))
    differing_exp = -2**31
    axis = 0
    for j in range(2, -1, -1):
        if (p[j] < 0.0) != (q[j] < 0.0):
            return -1 if p[j] < q[j] else 1
        y = _float_xor_msb(p[j], q[j])
        if differing_exp < y:
            differing_exp = y
            axis = j
    if p[axis] < q[axis]:
        return -1
    if p[axis] > q[axis]:
        return 1
    return left.id - right.id


def load_rt_barneshut_author_dataset(
    path: str | Path,
    *,
    file_type: RtBarnesHutFileType,
    limit: int | None = None,
) -> RtBarnesHutDataset:
    path = Path(path)
    if limit is not None and limit <= 0:
        raise ValueError("limit must be positive when provided")

    points: list[RtBarnesHutPoint] = []
    header_values: tuple[float, ...] = ()
    if file_type == "treelogy":
        with path.open("r", encoding="utf-8") as handle:
            header_lines = [handle.readline().strip() for _ in range(5)]
            header_values = tuple(float(value) for value in header_lines if value)
            for line in handle:
                if not line.strip():
                    continue
                mass, x, y, z, *_velocity = (float(part) for part in line.split())
                points.append(
                    RtBarnesHutPoint(
                        mass=_float32(mass),
                        x=_float32(x),
                        y=_float32(y),
                        z=_float32(z),
                        id=len(points),
                    )
                )
                if limit is not None and len(points) >= limit:
                    break
        scaling = False
    elif file_type == "csv":
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                x, y, z, mass = (float(part) for part in line.strip().split(",")[:4])
                points.append(
                    RtBarnesHutPoint(
                        mass=_float32(mass * 1.0e5),
                        x=_float32(x * 10.0),
                        y=_float32(y * 10.0),
                        z=_float32(z * 10.0),
                        id=len(points),
                    )
                )
                if limit is not None and len(points) >= limit:
                    break
        scaling = True
    else:
        raise ValueError(f"unsupported RT-BarnesHut file_type: {file_type!r}")

    if not points:
        raise ValueError(f"no RT-BarnesHut points loaded from {path}")

    return RtBarnesHutDataset(
        file_type=file_type,
        path=str(path),
        point_count=len(points),
        header_values=header_values,
        author_scaling_applied=scaling,
        points=tuple(points),
    )


def write_trimmed_rt_barneshut_author_dataset(
    source_path: str | Path,
    output_path: str | Path,
    *,
    file_type: RtBarnesHutFileType,
    limit: int,
) -> Path:
    if limit <= 0:
        raise ValueError("limit must be positive")
    source_path = Path(source_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if file_type == "treelogy":
        with source_path.open("r", encoding="utf-8") as source:
            header = [source.readline() for _ in range(5)]
            if len(header) < 5 or any(line == "" for line in header):
                raise ValueError("treelogy source is missing the five-line header")
            header[0] = f"{float(limit):.6f}\n"
            rows = []
            for line in source:
                if line.strip():
                    rows.append(line)
                if len(rows) >= limit:
                    break
        if len(rows) < limit:
            raise ValueError(f"source only had {len(rows)} rows, expected {limit}")
        output_path.write_text("".join(header + rows), encoding="utf-8")
    elif file_type == "csv":
        rows = []
        with source_path.open("r", encoding="utf-8") as source:
            for line in source:
                if line.strip():
                    rows.append(line)
                if len(rows) >= limit:
                    break
        if len(rows) < limit:
            raise ValueError(f"source only had {len(rows)} rows, expected {limit}")
        output_path.write_text("".join(rows), encoding="utf-8")
    else:
        raise ValueError(f"unsupported RT-BarnesHut file_type: {file_type!r}")

    return output_path


def _grid_size(points: Iterable[RtBarnesHutPoint]) -> float:
    max_abs = max(max(abs(point.x), abs(point.y), abs(point.z)) for point in points)
    return float(math.ceil(max_abs) * 2.0)


def _insert_node(parent: _Node, point: _Node, s: float) -> None:
    offset_x = offset_y = offset_z = 0.0
    octant = 0
    if parent.cofm_z < point.cofm_z:
        octant = 4
        offset_z = s
    if parent.cofm_y < point.cofm_y:
        octant += 2
        offset_y = s
    if parent.cofm_x < point.cofm_x:
        octant += 1
        offset_x = s
    child = parent.children[octant]
    if child is None:
        point.s = s
        parent.children[octant] = point
        return
    half_r = 0.5 * s
    if child.node_type == "leaf":
        inner = _Node(
            cofm_x=(parent.cofm_x - half_r) + offset_x,
            cofm_y=(parent.cofm_y - half_r) + offset_y,
            cofm_z=(parent.cofm_z - half_r) + offset_z,
            s=half_r,
            node_type="non_leaf",
        )
        _insert_node(inner, point, half_r)
        _insert_node(inner, child, half_r)
        parent.children[octant] = inner
    else:
        _insert_node(child, point, half_r)


def _compute_com(node: _Node) -> None:
    if node.node_type != "non_leaf":
        return
    total_mass = 0.0
    x = y = z = 0.0
    for child in node.children:
        if child is None:
            continue
        _compute_com(child)
        total_mass += child.mass
        x += child.cofm_x * child.mass
        y += child.cofm_y * child.mass
        z += child.cofm_z * child.mass
    if total_mass != 0.0:
        node.mass = total_mass
        node.cofm_x = x / total_mass
        node.cofm_y = y / total_mass
        node.cofm_z = z / total_mass


def _build_author_bucket_tree(dataset: RtBarnesHutDataset) -> tuple[_Node, tuple[RtBarnesHutPoint, ...], float]:
    sorted_points = tuple(sorted(dataset.points, key=cmp_to_key(_zorder_compare)))
    normalized_points = tuple(
        RtBarnesHutPoint(mass=point.mass, x=point.x, y=point.y, z=point.z, id=index)
        for index, point in enumerate(sorted_points)
    )
    grid_size = _grid_size(normalized_points)
    root = _Node(0.0, 0.0, 0.0, grid_size, point_id=-1, node_type="non_leaf")

    for start in range(0, len(normalized_points), RT_BARNESHUT_BUCKET_SIZE):
        chunk = normalized_points[start : start + RT_BARNESHUT_BUCKET_SIZE]
        mass = sum(point.mass for point in chunk)
        cofm_x = sum(point.x * point.mass for point in chunk) / mass
        cofm_y = sum(point.y * point.mass for point in chunk) / mass
        cofm_z = sum(point.z * point.mass for point in chunk) / mass
        node = _Node(cofm_x, cofm_y, cofm_z, grid_size * 0.5, point_id=-1, mass=mass)
        node.particles.extend(point.id for point in chunk)
        _insert_node(root, node, grid_size * 0.5)

    _compute_com(root)
    return root, normalized_points, grid_size


def _distance(point: RtBarnesHutPoint, node: _Node) -> float:
    dx = point.x - node.cofm_x
    dy = point.y - node.cofm_y
    dz = point.z - node.cofm_z
    return math.sqrt((dx * dx) + (dy * dy) + (dz * dz))


def _force_contribution(point: RtBarnesHutPoint, node: _Node, points: tuple[RtBarnesHutPoint, ...]) -> float:
    result = 0.0
    if node.node_type == "leaf":
        for particle_id in node.particles:
            if particle_id == point.id:
                continue
            other = points[particle_id]
            dx = point.x - other.x
            dy = point.y - other.y
            dz = point.z - other.z
            r2 = (dx * dx) + (dy * dy) + (dz * dz)
            if r2 != 0.0:
                result += ((point.mass * other.mass) / r2) * RT_BARNESHUT_GRAVITATIONAL_CONSTANT
        return result

    dx = point.x - node.cofm_x
    dy = point.y - node.cofm_y
    dz = point.z - node.cofm_z
    r2 = (dx * dx) + (dy * dy) + (dz * dz)
    if r2 == 0.0:
        return 0.0
    return ((point.mass * node.mass) / r2) * RT_BARNESHUT_GRAVITATIONAL_CONSTANT


def _force_on(point: RtBarnesHutPoint, node: _Node, points: tuple[RtBarnesHutPoint, ...]) -> float:
    if node.node_type == "leaf":
        if (
            node.mass != 0.0
            and not (point.x == node.cofm_x and point.y == node.cofm_y and point.z == node.cofm_z)
        ):
            return _force_contribution(point, node, points)
        return 0.0

    if node.s < _distance(point, node) * RT_BARNESHUT_THRESHOLD:
        return _force_contribution(point, node, points)

    total = 0.0
    for child in node.children:
        if child is not None:
            total += _force_on(point, child, points)
    return total


def _count_nodes(node: _Node) -> tuple[int, int]:
    total = 1
    leaves = 1 if node.node_type == "leaf" else 0
    for child in node.children:
        if child is None:
            continue
        child_total, child_leaves = _count_nodes(child)
        total += child_total
        leaves += child_leaves
    return total, leaves


def run_rt_barneshut_cpu_author_semantics_oracle(
    path: str | Path,
    *,
    file_type: RtBarnesHutFileType,
    limit: int,
    first_force_count: int = 8,
) -> RtBarnesHutCpuOracleSummary:
    dataset = load_rt_barneshut_author_dataset(path, file_type=file_type, limit=limit)
    root, points, grid_size = _build_author_bucket_tree(dataset)
    forces = tuple(_force_on(point, root, points) for point in points)
    node_count, leaf_count = _count_nodes(root)
    return RtBarnesHutCpuOracleSummary(
        contract_version=RT_BARNESHUT_AUTHOR_CONTRACT_VERSION,
        file_type=file_type,
        source_path=str(path),
        point_count=len(points),
        bucket_size=RT_BARNESHUT_BUCKET_SIZE,
        theta=RT_BARNESHUT_THRESHOLD,
        grid_size=grid_size,
        node_count=node_count,
        leaf_count=leaf_count,
        force_checksum=sum(forces),
        force_abs_checksum=sum(abs(force) for force in forces),
        force_min=min(forces),
        force_max=max(forces),
        first_forces=tuple(forces[:first_force_count]),
        claim_boundary={
            "paper_semantics_contract": True,
            "performance_route": False,
            "rt_core_route": False,
            "public_speedup_claim_authorized": False,
            "authors_code_comparison_speedup_authorized": False,
            "purpose": "same-input CPU oracle for RT-BarnesHut route validation",
        },
    )


_AUTHOR_TIMING_PATTERNS = {
    "preprocessing_seconds": re.compile(r"Preprocessing Time:\s*([0-9.]+)"),
    "rt_force_seconds": re.compile(r"RT Cores Force Calculations time:\s*([0-9.]+)"),
    "execution_seconds": re.compile(r"Execution time:\s*([0-9.]+)"),
    "point_count": re.compile(r"Number of points:\s*([0-9]+)"),
    "rt_force_checksum": re.compile(r"RT Force checksum:\s*([-+0-9.eE]+)"),
    "rt_force_abs_checksum": re.compile(r"RT Force abs checksum:\s*([-+0-9.eE]+)"),
}


def parse_rt_barneshut_author_stdout(stdout: str) -> dict[str, float | int]:
    parsed: dict[str, float | int] = {}
    for key, pattern in _AUTHOR_TIMING_PATTERNS.items():
        match = pattern.search(stdout)
        if match is None:
            continue
        value = match.group(1)
        parsed[key] = int(value) if key == "point_count" else float(value)
    return parsed


def validate_rt_barneshut_author_contract_summary(summary: RtBarnesHutCpuOracleSummary) -> None:
    if summary.contract_version != RT_BARNESHUT_AUTHOR_CONTRACT_VERSION:
        raise ValueError("unexpected RT-BarnesHut contract version")
    if summary.point_count <= 0:
        raise ValueError("point_count must be positive")
    if summary.bucket_size != RT_BARNESHUT_BUCKET_SIZE:
        raise ValueError("bucket size mismatch")
    if summary.node_count < summary.leaf_count:
        raise ValueError("node_count must be >= leaf_count")
    if not math.isfinite(summary.force_checksum):
        raise ValueError("force checksum must be finite")
    if not summary.claim_boundary.get("paper_semantics_contract"):
        raise ValueError("summary must preserve paper_semantics_contract boundary")
