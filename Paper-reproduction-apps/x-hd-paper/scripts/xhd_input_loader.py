from __future__ import annotations

from pathlib import Path

import numpy as np


_PLY_NUMPY_TYPES = {
    "char": "i1",
    "int8": "i1",
    "uchar": "u1",
    "uint8": "u1",
    "short": "i2",
    "int16": "i2",
    "ushort": "u2",
    "uint16": "u2",
    "int": "i4",
    "int32": "i4",
    "uint": "u4",
    "uint32": "u4",
    "float": "f4",
    "float32": "f4",
    "double": "f8",
    "float64": "f8",
}


def _split_wkt_top_level(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError(f"unbalanced WKT parentheses near: {text[:80]}")
        elif char == "," and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    if depth != 0:
        raise ValueError(f"unbalanced WKT parentheses near: {text[:80]}")
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def _strip_wkt_outer_parens(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("(") or not stripped.endswith(")"):
        return stripped
    depth = 0
    for index, char in enumerate(stripped):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError(f"unbalanced WKT parentheses near: {text[:80]}")
            if depth == 0 and index != len(stripped) - 1:
                return stripped
    if depth != 0:
        raise ValueError(f"unbalanced WKT parentheses near: {text[:80]}")
    return stripped[1:-1].strip()


def _wkt_type_and_body(text: str) -> tuple[str, str]:
    start = text.find("(")
    end = text.rfind(")")
    if start < 0 or end <= start:
        raise ValueError(f"invalid WKT geometry: {text}")
    prefix = text[:start].strip()
    if not prefix:
        raise ValueError(f"WKT geometry has no type: {text}")
    geom_type = prefix.split()[0].upper()
    if text[end + 1 :].strip():
        raise ValueError(f"unexpected trailing WKT text: {text[end + 1:].strip()}")
    return geom_type, text[start + 1 : end].strip()


def _parse_wkt_coordinate_sequence(sequence: str, *, n_dims: int) -> list[tuple[float, ...]]:
    points: list[tuple[float, ...]] = []
    for item in sequence.split(","):
        parts = item.strip().split()
        if not parts:
            continue
        if len(parts) != n_dims:
            raise ValueError(f"WKT coordinate has {len(parts)} dims, expected {n_dims}: {item.strip()}")
        points.append(tuple(float(value) for value in parts))
    if not points:
        raise ValueError("empty WKT coordinate sequence")
    return points


def _parse_wkt_geometry_line(line: str, *, n_dims: int) -> list[tuple[float, ...]] | None:
    text = line.strip()
    if not text:
        return None
    geom_type, body = _wkt_type_and_body(text)
    if not body or body.upper() == "EMPTY":
        raise ValueError(f"empty WKT geometry: {text}")
    if geom_type == "POINT":
        points = _parse_wkt_coordinate_sequence(body, n_dims=n_dims)
        if len(points) != 1:
            raise ValueError(f"POINT WKT must contain exactly one coordinate, got {len(points)}: {text}")
        return points
    if geom_type == "LINESTRING":
        return _parse_wkt_coordinate_sequence(body, n_dims=n_dims)
    if geom_type == "MULTILINESTRING":
        points: list[tuple[float, ...]] = []
        for line_string in _split_wkt_top_level(body):
            points.extend(_parse_wkt_coordinate_sequence(_strip_wkt_outer_parens(line_string), n_dims=n_dims))
        return points
    if geom_type == "POLYGON":
        rings = _split_wkt_top_level(body)
        if not rings:
            raise ValueError(f"empty POLYGON WKT: {text}")
        # The X-HD author WKT loader consumes polygon boundaries as points. For
        # paper-app parity we mirror the current contract captured in Goal5302:
        # only outer rings feed the Hausdorff point set; holes are ignored.
        return _parse_wkt_coordinate_sequence(_strip_wkt_outer_parens(rings[0]), n_dims=n_dims)
    if geom_type == "MULTIPOLYGON":
        points = []
        for polygon in _split_wkt_top_level(body):
            rings = _split_wkt_top_level(_strip_wkt_outer_parens(polygon))
            if not rings:
                raise ValueError(f"empty polygon inside MULTIPOLYGON WKT: {text}")
            points.extend(_parse_wkt_coordinate_sequence(_strip_wkt_outer_parens(rings[0]), n_dims=n_dims))
        if not points:
            raise ValueError(f"empty MULTIPOLYGON WKT: {text}")
        return points
    raise ValueError(f"unsupported X-HD WKT geometry type: {geom_type}")


def _parse_wkt_point_line(line: str) -> tuple[float, ...] | None:
    points = _parse_wkt_geometry_line(line, n_dims=2)
    if points is None:
        return None
    if len(points) != 1:
        raise ValueError(f"expected one POINT WKT coordinate, got {len(points)}")
    return points[0]


def load_wkt_points(path: Path, *, n_dims: int) -> list[tuple[float, ...]]:
    points: list[tuple[float, ...]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row_points = _parse_wkt_geometry_line(line, n_dims=n_dims)
        if row_points is None:
            continue
        points.extend(row_points)
    if not points:
        raise ValueError(f"{path} contains no WKT point rows")
    return points


def point_matrix_to_rows(matrix: np.ndarray) -> list[tuple[float, ...]]:
    coords = np.asarray(matrix, dtype=np.float64)
    if coords.ndim != 2:
        raise ValueError("point matrix must be 2-D")
    return [tuple(float(value) for value in row) for row in coords]


def lift_point_matrix_2d_to_3d_zero_z(matrix: np.ndarray, *, copy: bool = True) -> np.ndarray:
    """Embed an Nx2 point matrix into Nx3 by appending a zero z coordinate."""

    coords = np.asarray(matrix, dtype=np.float64)
    if coords.ndim != 2 or coords.shape[1] != 2:
        raise ValueError("zero-z lift expects an Nx2 point matrix")
    lifted = np.empty((coords.shape[0], 3), dtype=np.float64)
    lifted[:, :2] = coords
    lifted[:, 2] = 0.0
    if copy:
        return np.ascontiguousarray(lifted)
    return lifted


def load_wkt_point_matrix(path: Path, *, n_dims: int) -> np.ndarray:
    total_points = 0
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            row_points = _parse_wkt_geometry_line(line, n_dims=n_dims)
            if row_points is not None:
                total_points += len(row_points)
    if total_points == 0:
        raise ValueError(f"{path} contains no WKT point rows")

    matrix = np.empty((total_points, n_dims), dtype=np.float64)
    offset = 0
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            row_points = _parse_wkt_geometry_line(line, n_dims=n_dims)
            if row_points is None:
                continue
            count = len(row_points)
            matrix[offset : offset + count, :] = np.asarray(row_points, dtype=np.float64)
            offset += count
    if offset != total_points:
        raise RuntimeError("WKT point count changed while loading matrix")
    return matrix


def _read_ascii_ply_vertex_header(path: Path, *, n_dims: int) -> tuple[int, list[int], int]:
    if n_dims not in {2, 3}:
        raise ValueError("PLY loader supports only 2D or 3D point coordinates")

    vertex_count: int | None = None
    property_names: list[str] = []
    in_vertex_properties = False
    header_lines = 0
    with path.open("r", encoding="utf-8", errors="strict") as fh:
        first = fh.readline().strip()
        header_lines += 1
        if first != "ply":
            raise ValueError(f"{path} is not a PLY file")
        fmt = fh.readline().strip()
        header_lines += 1
        if fmt != "format ascii 1.0":
            raise ValueError(f"{path} must be ASCII PLY for this bounded app bridge, got: {fmt}")
        for line in fh:
            header_lines += 1
            text = line.strip()
            if text.startswith("element vertex "):
                vertex_count = int(text.split()[-1])
                in_vertex_properties = True
                continue
            if text.startswith("element ") and not text.startswith("element vertex "):
                in_vertex_properties = False
            if in_vertex_properties and text.startswith("property "):
                property_names.append(text.split()[-1])
            if text == "end_header":
                break
        else:
            raise ValueError(f"{path} PLY header has no end_header")

        if vertex_count is None:
            raise ValueError(f"{path} PLY header has no element vertex row")
        required = ("x", "y") if n_dims == 2 else ("x", "y", "z")
        missing = [name for name in required if name not in property_names]
        if missing:
            raise ValueError(f"{path} PLY vertex properties missing required coordinates: {missing}")
        coordinate_indices = [property_names.index(name) for name in required]
    return vertex_count, coordinate_indices, header_lines


def _read_ply_vertex_header(path: Path, *, n_dims: int) -> tuple[str, int, list[tuple[str, str]], int]:
    if n_dims not in {2, 3}:
        raise ValueError("PLY loader supports only 2D or 3D point coordinates")

    fmt: str | None = None
    vertex_count: int | None = None
    vertex_properties: list[tuple[str, str]] = []
    in_vertex_properties = False
    with path.open("rb") as fh:
        first = fh.readline()
        if first.strip() != b"ply":
            raise ValueError(f"{path} is not a PLY file")
        while True:
            line = fh.readline()
            if not line:
                raise ValueError(f"{path} PLY header has no end_header")
            try:
                text = line.decode("ascii").strip()
            except UnicodeDecodeError as exc:
                raise ValueError(f"{path} PLY header is not ASCII-decodable") from exc
            if text.startswith("format "):
                fmt = text.replace("format ", "", 1)
                continue
            if text.startswith("element vertex "):
                vertex_count = int(text.split()[-1])
                in_vertex_properties = True
                continue
            if text.startswith("element ") and not text.startswith("element vertex "):
                in_vertex_properties = False
            if in_vertex_properties and text.startswith("property "):
                parts = text.split()
                if len(parts) >= 3 and parts[1] == "list":
                    raise ValueError(f"{path} list-valued vertex properties are not supported")
                if len(parts) != 3:
                    raise ValueError(f"{path} unsupported PLY vertex property row: {text}")
                vertex_properties.append((parts[2], parts[1]))
            if text == "end_header":
                header_bytes = int(fh.tell())
                break

    if fmt is None:
        raise ValueError(f"{path} PLY header has no format row")
    if vertex_count is None:
        raise ValueError(f"{path} PLY header has no element vertex row")
    required = ("x", "y") if n_dims == 2 else ("x", "y", "z")
    property_names = [name for name, _ in vertex_properties]
    missing = [name for name in required if name not in property_names]
    if missing:
        raise ValueError(f"{path} PLY vertex properties missing required coordinates: {missing}")
    return fmt, vertex_count, vertex_properties, header_bytes


def load_ascii_ply_vertices(path: Path, *, n_dims: int) -> list[tuple[float, ...]]:
    """Load ASCII PLY vertex coordinates for bounded paper-app gates.

    This is intentionally app-owned input handling. It does not add a core RTDL
    primitive and does not try to consume faces or mesh topology.
    """

    return point_matrix_to_rows(load_ascii_ply_vertex_matrix(path, n_dims=n_dims))


def load_ascii_ply_vertex_matrix(path: Path, *, n_dims: int) -> np.ndarray:
    """Load ASCII PLY vertex coordinates directly into a NumPy matrix.

    This app-owned bridge keeps the high-volume public X-HD route from first
    materializing Python tuple rows and then repacking them into columns.
    """

    vertex_count, coordinate_indices, header_lines = _read_ascii_ply_vertex_header(path, n_dims=n_dims)
    if vertex_count <= 0:
        raise ValueError(f"{path} contains no PLY vertices")
    try:
        coords = np.loadtxt(
            path,
            dtype=np.float64,
            skiprows=header_lines,
            max_rows=vertex_count,
            usecols=coordinate_indices,
            ndmin=2,
        )
    except ValueError as exc:
        raise ValueError(f"{path} could not be parsed as ASCII PLY vertex coordinates: {exc}") from exc
    if coords.shape != (vertex_count, n_dims):
        raise ValueError(
            f"{path} parsed PLY vertex matrix has shape {coords.shape}, expected {(vertex_count, n_dims)}"
        )
    return coords


def _binary_ply_dtype(path: Path, *, fmt: str, vertex_properties: list[tuple[str, str]]) -> np.dtype:
    if fmt == "binary_little_endian 1.0":
        endian = "<"
    elif fmt == "binary_big_endian 1.0":
        endian = ">"
    else:
        raise ValueError(f"{path} unsupported binary PLY format: {fmt}")
    fields: list[tuple[str, np.dtype]] = []
    for name, ply_type in vertex_properties:
        if ply_type not in _PLY_NUMPY_TYPES:
            raise ValueError(f"{path} unsupported PLY vertex property type: {ply_type}")
        dtype = np.dtype(_PLY_NUMPY_TYPES[ply_type])
        if dtype.itemsize > 1:
            dtype = dtype.newbyteorder(endian)
        fields.append((name, dtype))
    return np.dtype(fields)


def load_binary_ply_vertex_matrix(path: Path, *, n_dims: int) -> np.ndarray:
    """Load binary PLY vertex coordinates into a NumPy matrix.

    This remains app-owned input handling for the X-HD paper app. It exists so
    public Stanford binary PLY assets can feed the same numeric route as ASCII
    PLY without teaching RTDL core any mesh-file semantics.
    """

    fmt, vertex_count, vertex_properties, header_bytes = _read_ply_vertex_header(path, n_dims=n_dims)
    if not fmt.startswith("binary_"):
        raise ValueError(f"{path} must be binary PLY, got: {fmt}")
    if vertex_count <= 0:
        raise ValueError(f"{path} contains no PLY vertices")
    dtype = _binary_ply_dtype(path, fmt=fmt, vertex_properties=vertex_properties)
    with path.open("rb") as fh:
        fh.seek(header_bytes)
        rows = np.fromfile(fh, dtype=dtype, count=vertex_count)
    if rows.shape != (vertex_count,):
        raise ValueError(f"{path} ended before all {vertex_count} binary PLY vertices were read")
    required = ("x", "y") if n_dims == 2 else ("x", "y", "z")
    coords = np.empty((vertex_count, n_dims), dtype=np.float64)
    for index, name in enumerate(required):
        coords[:, index] = rows[name].astype(np.float64, copy=False)
    return coords


def load_ply_vertex_matrix(path: Path, *, n_dims: int) -> np.ndarray:
    fmt, _, _, _ = _read_ply_vertex_header(path, n_dims=n_dims)
    if fmt == "format ascii 1.0":
        raise ValueError(f"{path} unsupported PLY format row: {fmt}")
    if fmt == "ascii 1.0":
        return load_ascii_ply_vertex_matrix(path, n_dims=n_dims)
    if fmt in {"binary_little_endian 1.0", "binary_big_endian 1.0"}:
        return load_binary_ply_vertex_matrix(path, n_dims=n_dims)
    raise ValueError(f"{path} unsupported PLY format: {fmt}")


def _non_comment_off_lines(path: Path) -> list[str]:
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="strict").splitlines():
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        lines.append(text)
    return lines


def load_ascii_off_vertex_matrix(path: Path, *, n_dims: int) -> np.ndarray:
    """Load ASCII OFF vertex coordinates for X-HD paper-app gates.

    OFF parsing remains app-owned input handling. RTDL core still receives a
    plain coordinate matrix and does not learn any X-HD or mesh-file semantics.
    Faces are intentionally ignored because the author HD executable consumes
    point coordinates from mesh vertices for this paper route.
    """

    if n_dims not in {2, 3}:
        raise ValueError("OFF loader supports only 2D or 3D point coordinates")
    lines = _non_comment_off_lines(path)
    if not lines:
        raise ValueError(f"{path} is empty")
    first = lines[0]
    if first == "OFF":
        if len(lines) < 2:
            raise ValueError(f"{path} OFF header has no counts row")
        counts = lines[1].split()
        vertex_start = 2
    elif first.startswith("OFF"):
        counts = first[3:].strip().split()
        vertex_start = 1
    else:
        raise ValueError(f"{path} is not an OFF file")
    if len(counts) < 2:
        raise ValueError(f"{path} OFF counts row must include vertex and face counts")
    vertex_count = int(counts[0])
    if vertex_count <= 0:
        raise ValueError(f"{path} contains no OFF vertices")
    if len(lines) < vertex_start + vertex_count:
        raise ValueError(f"{path} OFF file ended before all vertices were read")
    coords = np.empty((vertex_count, n_dims), dtype=np.float64)
    for row_index, text in enumerate(lines[vertex_start : vertex_start + vertex_count]):
        parts = text.split()
        if len(parts) < n_dims:
            raise ValueError(f"{path} OFF vertex row {row_index} has too few coordinates: {text}")
        coords[row_index, :] = [float(value) for value in parts[:n_dims]]
    return coords


def load_points_matrix(path: Path, *, n_dims: int, input_type: str) -> np.ndarray:
    normalized = input_type.lower()
    if normalized == "wkt":
        return load_wkt_point_matrix(path, n_dims=n_dims)
    if normalized == "ply":
        return load_ply_vertex_matrix(path, n_dims=n_dims)
    if normalized == "off":
        return load_ascii_off_vertex_matrix(path, n_dims=n_dims)
    raise ValueError(f"unsupported X-HD app input_type: {input_type}")


def load_points(path: Path, *, n_dims: int, input_type: str) -> list[tuple[float, ...]]:
    return point_matrix_to_rows(load_points_matrix(path, n_dims=n_dims, input_type=input_type))


def translate_point_matrix_to_min_bound(matrix: np.ndarray, *, copy: bool = False) -> np.ndarray:
    """Translate each coordinate axis so the point-set minimum is zero."""

    coords = np.asarray(matrix, dtype=np.float64)
    if coords.ndim != 2 or coords.shape[0] == 0:
        raise ValueError("cannot translate an empty or non-2D point matrix")
    if copy or not coords.flags.writeable:
        coords = coords.copy()
    coords -= coords.min(axis=0)
    return coords


def normalize_point_matrix_to_author_unit_box(matrix: np.ndarray, *, copy: bool = False) -> np.ndarray:
    """Apply the author X-HD `NormalizePoints` transform to one point matrix.

    The author subtracts the per-axis lower bound and divides every coordinate
    by the largest axis extent for that same input. This is an app-owned input
    provenance transform; RTDL core remains unaware of paper file formats.
    """

    coords = np.asarray(matrix, dtype=np.float64)
    if coords.ndim != 2 or coords.shape[0] == 0:
        raise ValueError("cannot normalize an empty or non-2D point matrix")
    if copy or not coords.flags.writeable:
        coords = coords.copy()
    lower = coords.min(axis=0)
    upper = coords.max(axis=0)
    max_extent = float(np.max(upper - lower))
    if max_extent == 0.0:
        max_extent = 1.0
    coords -= lower
    coords /= max_extent
    return coords


def normalize_point_matrix_to_author_float32_unit_box(matrix: np.ndarray, *, copy: bool = False) -> np.ndarray:
    """Apply the author normalize transform with float32 coordinate semantics.

    The paper-branch author executable used for ModelNet40 dispatches
    `RunHausdorffDistanceImpl<float, 3>` by default. This helper mirrors that
    app-level contract by rounding the input coordinates to float32 before the
    lower-bound / max-extent normalization arithmetic, then returning a float64
    matrix for the generic RTDL route. RTDL core still receives plain numeric
    columns and remains unaware of X-HD, OFF, or ModelNet40.
    """

    coords = np.asarray(matrix, dtype=np.float32)
    if coords.ndim != 2 or coords.shape[0] == 0:
        raise ValueError("cannot normalize an empty or non-2D point matrix")
    if copy or not coords.flags.writeable:
        coords = coords.copy()
    lower = coords.min(axis=0)
    upper = coords.max(axis=0)
    max_extent = np.float32(np.max(upper - lower))
    if float(max_extent) == 0.0:
        max_extent = np.float32(1.0)
    coords -= lower
    coords /= max_extent
    return coords.astype(np.float64, copy=False)


def translate_points_to_min_bound(points: list[tuple[float, ...]]) -> list[tuple[float, ...]]:
    """Translate each coordinate axis so the point-set minimum is zero."""

    if not points:
        raise ValueError("cannot translate an empty point set")
    n_dims = len(points[0])
    mins = tuple(min(point[axis] for point in points) for axis in range(n_dims))
    return [tuple(point[axis] - mins[axis] for axis in range(n_dims)) for point in points]
