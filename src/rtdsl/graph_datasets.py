from __future__ import annotations

from dataclasses import dataclass
import gzip
from pathlib import Path

from .graph_reference import csr_graph
from .graph_reference import CSRGraph


@dataclass(frozen=True)
class GraphDatasetSpec:
    name: str
    source: str
    source_url: str
    directed: bool
    download_url: str | None = None
    vertex_count_hint: int | None = None
    edge_count_hint: int | None = None
    notes: str = ""


def graph_dataset_candidates() -> tuple[GraphDatasetSpec, ...]:
    return (
        GraphDatasetSpec(
            name="snap_wiki_talk",
            source="SNAP",
            source_url="https://snap.stanford.edu/data/wiki-Talk.html",
            download_url="https://snap.stanford.edu/data/wiki-Talk.txt.gz",
            directed=True,
            vertex_count_hint=2_394_385,
            edge_count_hint=5_021_410,
            notes="real directed communication graph; useful bounded BFS anchor",
        ),
        GraphDatasetSpec(
            name="graphalytics_wiki_talk",
            source="Graphalytics",
            source_url="https://ldbcouncil.org/benchmarks/graphalytics/datasets/",
            download_url="https://snap.stanford.edu/data/wiki-Talk.txt.gz",
            directed=True,
            vertex_count_hint=2_394_385,
            edge_count_hint=5_021_410,
            notes="benchmark-oriented packaging of wiki-Talk family; raw edge list fetched from SNAP",
        ),
        GraphDatasetSpec(
            name="graphalytics_cit_patents",
            source="Graphalytics",
            source_url="https://ldbcouncil.org/benchmarks/graphalytics/datasets/",
            download_url="https://snap.stanford.edu/data/cit-Patents.txt.gz",
            directed=True,
            vertex_count_hint=3_774_768,
            edge_count_hint=16_518_947,
            notes="large directed citation graph; useful bounded RT graph anchor",
        ),
    )


def graph_dataset_spec(name: str) -> GraphDatasetSpec:
    for candidate in graph_dataset_candidates():
        if candidate.name == name:
            return candidate
    raise KeyError(f"unknown graph dataset: {name}")


def load_snap_edge_list_graph(
    path: str | Path,
    *,
    directed: bool = True,
    max_edges: int | None = None,
    expected_vertex_count: int | None = None,
) -> CSRGraph:
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    edges: list[tuple[int, int]] = []
    max_vertex_id = -1
    opener = gzip.open if source_path.suffix == ".gz" else open
    with opener(source_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            fields = stripped.split()
            if len(fields) < 2:
                raise ValueError(f"invalid edge-list line: {stripped!r}")
            src = int(fields[0])
            dst = int(fields[1])
            if src < 0 or dst < 0:
                raise ValueError("graph edge IDs must be non-negative")
            edges.append((src, dst))
            max_vertex_id = max(max_vertex_id, src, dst)
            if max_edges is not None and len(edges) >= max_edges:
                break

    if max_vertex_id < 0:
        vertex_count = expected_vertex_count or 0
        return csr_graph(
            row_offsets=(0,) * (vertex_count + 1),
            column_indices=(),
            vertex_count=vertex_count,
        )

    vertex_count = max(max_vertex_id + 1, expected_vertex_count or 0)
    neighbors: list[list[int]] = [[] for _ in range(vertex_count)]
    for src, dst in edges:
        neighbors[src].append(dst)
        if not directed and src != dst:
            neighbors[dst].append(src)

    row_offsets = [0]
    column_indices: list[int] = []
    for row in neighbors:
        normalized = tuple(sorted(set(int(value) for value in row)))
        column_indices.extend(normalized)
        row_offsets.append(len(column_indices))
    return csr_graph(
        row_offsets=tuple(row_offsets),
        column_indices=tuple(column_indices),
        vertex_count=vertex_count,
    )


def load_snap_simple_undirected_graph(
    path: str | Path,
    *,
    max_edges: int | None = None,
    expected_vertex_count: int | None = None,
) -> CSRGraph:
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    canonical_edges: set[tuple[int, int]] = set()
    max_vertex_id = -1
    opener = gzip.open if source_path.suffix == ".gz" else open
    with opener(source_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            fields = stripped.split()
            if len(fields) < 2:
                raise ValueError(f"invalid edge-list line: {stripped!r}")
            src = int(fields[0])
            dst = int(fields[1])
            if src < 0 or dst < 0:
                raise ValueError("graph edge IDs must be non-negative")
            max_vertex_id = max(max_vertex_id, src, dst)
            if src == dst:
                continue
            canonical_edges.add((min(src, dst), max(src, dst)))
            if max_edges is not None and len(canonical_edges) >= max_edges:
                break

    if max_vertex_id < 0:
        vertex_count = expected_vertex_count or 0
        return csr_graph(
            row_offsets=(0,) * (vertex_count + 1),
            column_indices=(),
            vertex_count=vertex_count,
        )

    vertex_count = max(max_vertex_id + 1, expected_vertex_count or 0)
    neighbors: list[list[int]] = [[] for _ in range(vertex_count)]
    for left, right in sorted(canonical_edges):
        neighbors[left].append(right)
        neighbors[right].append(left)

    row_offsets = [0]
    column_indices: list[int] = []
    for row in neighbors:
        normalized = tuple(sorted(int(value) for value in row))
        column_indices.extend(normalized)
        row_offsets.append(len(column_indices))
    return csr_graph(
        row_offsets=tuple(row_offsets),
        column_indices=tuple(column_indices),
        vertex_count=vertex_count,
    )
