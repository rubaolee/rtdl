from __future__ import annotations

import argparse
import gzip
import json
import struct
import time
import urllib.request
from pathlib import Path


DATASETS: dict[str, dict[str, object]] = {
    "com_dblp": {
        "snap_name": "com-dblp",
        "url": "https://snap.stanford.edu/data/bigdata/communities/com-dblp.ungraph.txt.gz",
        "expected_nodes": 317_080,
        "expected_edges": 1_049_866,
        "expected_triangles": 2_224_385,
    },
    "com_youtube": {
        "snap_name": "com-youtube",
        "url": "https://snap.stanford.edu/data/bigdata/communities/com-youtube.ungraph.txt.gz",
        "expected_nodes": 1_134_890,
        "expected_edges": 2_987_624,
        "expected_triangles": 3_056_386,
    },
    "cit_patents": {
        "snap_name": "cit-Patents",
        "url": "https://snap.stanford.edu/data/cit-Patents.txt.gz",
        "expected_nodes": 3_774_768,
        "expected_edges": 16_518_948,
        "expected_triangles": 7_515_023,
    },
    "wiki_talk": {
        "snap_name": "wiki-Talk",
        "url": "https://snap.stanford.edu/data/wiki-Talk.txt.gz",
        "expected_nodes": 2_394_385,
        "expected_edges": 5_021_410,
        "expected_triangles": 9_203_519,
    },
    "com_lj": {
        "snap_name": "com-lj",
        "url": "https://snap.stanford.edu/data/bigdata/communities/com-lj.ungraph.txt.gz",
        "expected_nodes": 3_997_962,
        "expected_edges": 34_681_189,
        "expected_triangles": 177_820_130,
    },
    "soc_livejournal1": {
        "snap_name": "soc-LiveJournal1",
        "url": "https://snap.stanford.edu/data/soc-LiveJournal1.txt.gz",
        "expected_nodes": 4_847_571,
        "expected_edges": 68_993_773,
        "expected_triangles": 285_730_264,
    },
    "com_orkut": {
        "snap_name": "com-orkut",
        "url": "https://snap.stanford.edu/data/bigdata/communities/com-orkut.ungraph.txt.gz",
        "expected_nodes": 3_072_441,
        "expected_edges": 117_185_083,
        "expected_triangles": 627_584_181,
    },
}


def _download(url: str, path: Path) -> dict[str, object]:
    if path.exists() and path.stat().st_size > 0:
        return {"status": "existing", "bytes": path.stat().st_size}
    path.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with urllib.request.urlopen(url, timeout=120) as response, path.open("wb") as output:
        while True:
            chunk = response.read(16 * 1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
    return {
        "status": "downloaded",
        "bytes": path.stat().st_size,
        "elapsed_ms": (time.perf_counter() - started) * 1000.0,
    }


def _convert_gzip_to_binary(gzip_path: Path, binary_path: Path) -> dict[str, object]:
    if binary_path.exists() and binary_path.stat().st_size > 0:
        return {
            "status": "existing",
            "bytes": binary_path.stat().st_size,
            "edge_count": binary_path.stat().st_size // 8,
        }
    binary_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    edge_count = 0
    comment_count = 0
    min_vertex: int | None = None
    max_vertex: int | None = None
    with gzip.open(gzip_path, "rt", encoding="utf-8", errors="replace") as source, binary_path.open("wb") as output:
        for line_number, raw_line in enumerate(source, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("%"):
                comment_count += 1
                continue
            parts = line.split()
            if len(parts) < 2:
                raise ValueError(f"{gzip_path}: line {line_number} has fewer than two columns")
            src = int(parts[0])
            dst = int(parts[1])
            output.write(struct.pack("<ii", src, dst))
            edge_count += 1
            local_min = src if src < dst else dst
            local_max = src if src > dst else dst
            min_vertex = local_min if min_vertex is None else min(min_vertex, local_min)
            max_vertex = local_max if max_vertex is None else max(max_vertex, local_max)
    return {
        "status": "converted",
        "bytes": binary_path.stat().st_size,
        "edge_count": edge_count,
        "comment_count": comment_count,
        "min_vertex": min_vertex,
        "max_vertex": max_vertex,
        "elapsed_ms": (time.perf_counter() - started) * 1000.0,
    }


def prepare_dataset(name: str, *, download_dir: Path, binary_dir: Path) -> dict[str, object]:
    metadata = DATASETS[name]
    gzip_path = download_dir / f"{metadata['snap_name']}.txt.gz"
    binary_path = binary_dir / f"{metadata['snap_name']}.edge"
    download = _download(str(metadata["url"]), gzip_path)
    convert = _convert_gzip_to_binary(gzip_path, binary_path)
    edge_count = int(convert["edge_count"])
    return {
        "name": name,
        "snap_name": metadata["snap_name"],
        "source_url": metadata["url"],
        "gzip_path": str(gzip_path),
        "binary_edge_path": str(binary_path),
        "expected_nodes": metadata["expected_nodes"],
        "expected_edges": metadata["expected_edges"],
        "expected_triangles": metadata["expected_triangles"],
        "download": download,
        "convert": convert,
        "edge_count_matches_snap": edge_count == metadata["expected_edges"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Download SNAP TC datasets and convert to RT-Graph binary edges.")
    parser.add_argument("--dataset", action="append", choices=sorted(DATASETS), help="Dataset key; defaults to all.")
    parser.add_argument("--download-dir", default="build/goal2593_snap_raw")
    parser.add_argument("--binary-dir", default="build/goal2593_snap_edges")
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    names = args.dataset or list(DATASETS)
    payload = {
        "source": "SNAP datasets used by RT-Graph SIGMETRICS 2025 TC section",
        "datasets": {
            name: prepare_dataset(name, download_dir=Path(args.download_dir), binary_dir=Path(args.binary_dir))
            for name in names
        },
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
