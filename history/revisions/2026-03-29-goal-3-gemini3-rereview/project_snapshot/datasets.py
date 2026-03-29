from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen


RAYJOIN_SAMPLE_URLS = {
    "br_county": "https://raw.githubusercontent.com/pwrliang/RayJoin/main/test/dataset/br_county_clean_25_odyssey_final.txt",
    "br_soil": "https://raw.githubusercontent.com/pwrliang/RayJoin/main/test/dataset/br_soil_ascii_odyssey_final.txt",
    "br_overlay_answer": "https://raw.githubusercontent.com/pwrliang/RayJoin/main/test/dataset/br_countyXbr_soil_answer.txt",
}


@dataclass(frozen=True)
class CdbPoint:
    x: float
    y: float


@dataclass(frozen=True)
class CdbChain:
    chain_id: int
    point_count: int
    first_point_id: int
    last_point_id: int
    left_face_id: int
    right_face_id: int
    points: tuple[CdbPoint, ...]


@dataclass(frozen=True)
class CdbDataset:
    name: str
    chains: tuple[CdbChain, ...]

    def face_ids(self) -> tuple[int, ...]:
        face_ids = set()
        for chain in self.chains:
            if chain.left_face_id != 0:
                face_ids.add(chain.left_face_id)
            if chain.right_face_id != 0:
                face_ids.add(chain.right_face_id)
        return tuple(sorted(face_ids))


def download_rayjoin_sample(name: str, destination: str | Path) -> Path:
    url = RAYJOIN_SAMPLE_URLS.get(name)
    if url is None:
        raise ValueError(f"unknown RayJoin sample dataset: {name}")

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(urlopen(url, timeout=30).read())
    return destination


def load_cdb(path: str | Path) -> CdbDataset:
    path = Path(path)
    return parse_cdb_text(path.read_text(encoding="utf-8"), name=path.stem)


def parse_cdb_text(text: str, *, name: str) -> CdbDataset:
    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    chains = []
    index = 0

    while index < len(raw_lines):
        header = raw_lines[index].split()
        if len(header) != 6:
            raise ValueError(f"invalid CDB header at line {index + 1}: {raw_lines[index]}")

        chain_id, point_count, first_point_id, last_point_id, left_face_id, right_face_id = (
            int(value) for value in header
        )
        index += 1

        points = []
        for _ in range(point_count):
            if index >= len(raw_lines):
                raise ValueError(f"unexpected EOF while reading chain {chain_id}")
            point_fields = raw_lines[index].split()
            if len(point_fields) != 2:
                raise ValueError(f"invalid CDB point at line {index + 1}: {raw_lines[index]}")
            points.append(CdbPoint(x=float(point_fields[0]), y=float(point_fields[1])))
            index += 1

        chains.append(
            CdbChain(
                chain_id=chain_id,
                point_count=point_count,
                first_point_id=first_point_id,
                last_point_id=last_point_id,
                left_face_id=left_face_id,
                right_face_id=right_face_id,
                points=tuple(points),
            )
        )

    return CdbDataset(name=name, chains=tuple(chains))


def chains_to_segments(dataset: CdbDataset, *, limit_chains: int | None = None) -> tuple[dict[str, float | int], ...]:
    chains = dataset.chains if limit_chains is None else dataset.chains[:limit_chains]
    records = []
    next_id = 1
    for chain in chains:
        for start, end in zip(chain.points, chain.points[1:]):
            records.append(
                {
                    "id": next_id,
                    "x0": start.x,
                    "y0": start.y,
                    "x1": end.x,
                    "y1": end.y,
                    "chain_id": chain.chain_id,
                }
            )
            next_id += 1
    return tuple(records)


def chains_to_probe_points(dataset: CdbDataset, *, limit_chains: int | None = None) -> tuple[dict[str, float | int], ...]:
    chains = dataset.chains if limit_chains is None else dataset.chains[:limit_chains]
    records = []
    for chain in chains:
        point = chain.points[0]
        records.append(
            {
                "id": chain.chain_id,
                "x": point.x,
                "y": point.y,
                "source_chain_id": chain.chain_id,
            }
        )
    return tuple(records)


def chains_to_polygon_refs(dataset: CdbDataset) -> tuple[dict[str, int], ...]:
    faces = {}
    for chain in dataset.chains:
        if chain.left_face_id != 0:
            faces.setdefault(chain.left_face_id, 0)
            faces[chain.left_face_id] += 1
        if chain.right_face_id != 0:
            faces.setdefault(chain.right_face_id, 0)
            faces[chain.right_face_id] += 1

    refs = []
    for index, face_id in enumerate(sorted(faces), start=0):
        refs.append({"id": face_id, "vertex_offset": index, "vertex_count": faces[face_id]})
    return tuple(refs)
