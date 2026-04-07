from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScalarType:
    name: str
    c_type: str
    cuda_type: str
    size: int


@dataclass(frozen=True)
class Field:
    name: str
    dtype: ScalarType

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "scalar_type": self.dtype.name,
            "c_type": self.dtype.c_type,
            "cuda_type": self.dtype.cuda_type,
            "size": self.dtype.size,
        }


@dataclass(frozen=True)
class Layout:
    name: str
    fields: tuple[Field, ...]

    def field_names(self) -> tuple[str, ...]:
        return tuple(field.name for field in self.fields)

    def require_fields(self, names: tuple[str, ...]) -> None:
        available = set(self.field_names())
        missing = [name for name in names if name not in available]
        if missing:
            missing_text = ", ".join(missing)
            raise ValueError(f"layout `{self.name}` is missing required fields: {missing_text}")


@dataclass(frozen=True)
class GeometryType:
    name: str
    dimension: int
    default_layout: Layout
    required_fields: tuple[str, ...] = ()


def field(name: str, dtype: ScalarType) -> Field:
    return Field(name=name, dtype=dtype)


def layout(name: str, *fields_in_order: Field) -> Layout:
    if not fields_in_order:
        raise ValueError("layout must define at least one field")
    return Layout(name=name, fields=tuple(fields_in_order))


f32 = ScalarType(name="f32", c_type="float", cuda_type="float", size=4)
u32 = ScalarType(name="u32", c_type="uint32_t", cuda_type="uint32_t", size=4)

Segment2DLayout = layout(
    "Segment2D",
    field("x0", f32),
    field("y0", f32),
    field("x1", f32),
    field("y1", f32),
    field("id", u32),
)

Point2DLayout = layout(
    "Point2D",
    field("x", f32),
    field("y", f32),
    field("id", u32),
)

Polygon2DLayout = layout(
    "Polygon2DRef",
    field("vertex_offset", u32),
    field("vertex_count", u32),
    field("id", u32),
)

Triangle2DLayout = layout(
    "Triangle2D",
    field("x0", f32),
    field("y0", f32),
    field("x1", f32),
    field("y1", f32),
    field("x2", f32),
    field("y2", f32),
    field("id", u32),
)

Triangle3DLayout = layout(
    "Triangle3D",
    field("x0", f32),
    field("y0", f32),
    field("z0", f32),
    field("x1", f32),
    field("y1", f32),
    field("z1", f32),
    field("x2", f32),
    field("y2", f32),
    field("z2", f32),
    field("id", u32),
)

Ray2DLayout = layout(
    "Ray2D",
    field("ox", f32),
    field("oy", f32),
    field("dx", f32),
    field("dy", f32),
    field("tmax", f32),
    field("id", u32),
)

Ray3DLayout = layout(
    "Ray3D",
    field("ox", f32),
    field("oy", f32),
    field("oz", f32),
    field("dx", f32),
    field("dy", f32),
    field("dz", f32),
    field("tmax", f32),
    field("id", u32),
)

Segments = GeometryType(
    name="segments",
    dimension=1,
    default_layout=Segment2DLayout,
    required_fields=("x0", "y0", "x1", "y1", "id"),
)
Points = GeometryType(
    name="points",
    dimension=0,
    default_layout=Point2DLayout,
    required_fields=("x", "y", "id"),
)
Polygons = GeometryType(
    name="polygons",
    dimension=2,
    default_layout=Polygon2DLayout,
    required_fields=("vertex_offset", "vertex_count", "id"),
)
Triangles = GeometryType(
    name="triangles",
    dimension=2,
    default_layout=Triangle2DLayout,
    required_fields=("x0", "y0", "x1", "y1", "x2", "y2", "id"),
)
Triangles3D = GeometryType(
    name="triangles",
    dimension=2,
    default_layout=Triangle3DLayout,
    required_fields=("x0", "y0", "z0", "x1", "y1", "z1", "x2", "y2", "z2", "id"),
)
Rays = GeometryType(
    name="rays",
    dimension=1,
    default_layout=Ray2DLayout,
    required_fields=("ox", "oy", "dx", "dy", "tmax", "id"),
)
Rays3D = GeometryType(
    name="rays",
    dimension=1,
    default_layout=Ray3DLayout,
    required_fields=("ox", "oy", "oz", "dx", "dy", "dz", "tmax", "id"),
)
