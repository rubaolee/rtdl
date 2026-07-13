#!/usr/bin/env python3
"""Apply the RTDL-defined duplicate-half-edge contract patch to RayJoin source.

The public patch file in author_patches documents the intended source changes.
This helper applies the same changes programmatically because that historical
patch is stored in the repository's apply_patch transcript format rather than
plain git-diff format.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_map_h(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "BuildCanonicalDuplicateHalfEdges" in text:
        print(f"[patch] duplicate-half-edge contract already present in {path}")
        return

    text = _replace_once(
        text,
        '#include <thrust/device_vector.h>\n',
        '#include <algorithm>\n#include <vector>\n\n#include <thrust/device_vector.h>\n',
        label="map.h include",
    )
    text = _replace_once(
        text,
        """  DEV_HOST Map(char id, ArrayView<point_t> points, ArrayView<edge_t> edges)
      : id_(id), points_(points), edges_(edges) {}
""",
        """  DEV_HOST Map(char id, ArrayView<point_t> points, ArrayView<edge_t> edges,
               ArrayView<index_t> canonical_edge_ids = ArrayView<index_t>())
      : id_(id), points_(points), edges_(edges),
        canonical_edge_ids_(canonical_edge_ids) {}
""",
        label="device map constructor",
    )
    text = _replace_once(
        text,
        """  DEV_HOST_INLINE ArrayView<edge_t> get_edges() const { return edges_; }

  DEV_HOST_INLINE polygon_id_t get_face_id(const edge_t& e) const {
""",
        """  DEV_HOST_INLINE ArrayView<edge_t> get_edges() const { return edges_; }

  DEV_INLINE index_t canonical_edge_id(index_t eid) const {
    if (!canonical_edge_ids_.empty() && eid < canonical_edge_ids_.size()) {
      return canonical_edge_ids_[eid];
    }
    return eid;
  }

  DEV_INLINE polygon_id_t get_face_id_for_edge_id(index_t eid) const {
    return get_face_id(get_edge(canonical_edge_id(eid)));
  }

  DEV_HOST_INLINE polygon_id_t get_face_id(const edge_t& e) const {
""",
        label="device map canonical methods",
    )
    text = _replace_once(
        text,
        """  ArrayView<point_t> points_;
  ArrayView<edge_t> edges_;
};
""",
        """  ArrayView<point_t> points_;
  ArrayView<edge_t> edges_;
  ArrayView<index_t> canonical_edge_ids_;
};
""",
        label="device map canonical field",
    )
    text = _replace_once(
        text,
        """    stream.Sync();
  }

  template <typename SRC_COORD_T>
""",
        """    stream.Sync();
    BuildCanonicalDuplicateHalfEdges();
  }

  template <typename SRC_COORD_T>
""",
        label="first load canonical build",
    )
    text = _replace_once(
        text,
        """    stream.Sync();
  }

  /**
   * Copy points and edges from device to host for debugging only
""",
        """    stream.Sync();
    BuildCanonicalDuplicateHalfEdges();
  }

  void BuildCanonicalDuplicateHalfEdges() {
    pinned_vector<point_t> host_points = points_;
    pinned_vector<edge_t> host_edges = edges_;
    thrust::host_vector<index_t> canonical(host_edges.size());
    for (size_t i = 0; i < canonical.size(); ++i) {
      canonical[i] = static_cast<index_t>(i);
    }
    struct DuplicateKey {
      coord_t ax;
      coord_t ay;
      coord_t bx;
      coord_t by;
    };
    struct DuplicateEntry {
      DuplicateKey key;
      size_t index;
    };
    auto key_less = [](const DuplicateKey& left, const DuplicateKey& right) {
      if (left.ax != right.ax) return left.ax < right.ax;
      if (left.ay != right.ay) return left.ay < right.ay;
      if (left.bx != right.bx) return left.bx < right.bx;
      return left.by < right.by;
    };
    auto key_equal = [](const DuplicateKey& left, const DuplicateKey& right) {
      return left.ax == right.ax && left.ay == right.ay &&
             left.bx == right.bx && left.by == right.by;
    };
    auto make_key = [&](const edge_t& edge) {
      const auto& p1 = host_points[edge.p1_idx];
      const auto& p2 = host_points[edge.p2_idx];
      coord_t ax = p1.x;
      coord_t ay = p1.y;
      coord_t bx = p2.x;
      coord_t by = p2.y;
      if (bx < ax || (bx == ax && by < ay)) {
        std::swap(ax, bx);
        std::swap(ay, by);
      }
      return DuplicateKey{ax, ay, bx, by};
    };
    std::vector<DuplicateEntry> entries;
    entries.reserve(host_edges.size());
    for (size_t i = 0; i < host_edges.size(); ++i) {
      entries.push_back({make_key(host_edges[i]), i});
    }
    std::sort(entries.begin(), entries.end(),
              [&](const DuplicateEntry& left, const DuplicateEntry& right) {
                if (!key_equal(left.key, right.key)) {
                  return key_less(left.key, right.key);
                }
                return left.index < right.index;
              });
    size_t group_begin = 0;
    while (group_begin < entries.size()) {
      size_t group_end = group_begin + 1;
      while (group_end < entries.size() &&
             key_equal(entries[group_begin].key, entries[group_end].key)) {
        ++group_end;
      }
      index_t canonical_eid = static_cast<index_t>(entries[group_begin].index);
      for (size_t i = group_begin + 1; i < group_end; ++i) {
        const index_t candidate = static_cast<index_t>(entries[i].index);
        if (candidate < canonical_eid) {
          canonical_eid = candidate;
        }
      }
      for (size_t i = group_begin; i < group_end; ++i) {
        canonical[entries[i].index] = canonical_eid;
      }
      group_begin = group_end;
    }
    canonical_edge_ids_ = canonical;
  }

  /**
   * Copy points and edges from device to host for debugging only
""",
        label="second load canonical build and method",
    )
    text = _replace_once(
        text,
        """  dev_map_t DeviceObject() const {
    return dev_map_t(id_, ArrayView<point_t>(points_),
                     ArrayView<edge_t>(edges_));
  }
""",
        """  dev_map_t DeviceObject() const {
    return dev_map_t(id_, ArrayView<point_t>(points_),
                     ArrayView<edge_t>(edges_),
                     ArrayView<index_t>(canonical_edge_ids_));
  }
""",
        label="device object canonical view",
    )
    text = _replace_once(
        text,
        """  thrust::device_vector<point_t> points_;
  thrust::device_vector<edge_t> edges_;
  pinned_vector<point_t> h_points_;  // For debugging
""",
        """  thrust::device_vector<point_t> points_;
  thrust::device_vector<edge_t> edges_;
  thrust::device_vector<index_t> canonical_edge_ids_;
  pinned_vector<point_t> h_points_;  // For debugging
""",
        label="host map canonical field",
    )
    path.write_text(text, encoding="utf-8")
    print(f"[patch] applied duplicate-half-edge contract to {path}")


def patch_map_overlay(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "get_face_id_for_edge_id" in text:
        print(f"[patch] duplicate-half-edge contract already present in {path}")
        return
    text = _replace_once(
        text,
        """                        const auto& e = d_base_map.get_edge(eid);

                        return d_base_map.get_face_id(e);
""",
        """                        return d_base_map.get_face_id_for_edge_id(eid);
""",
        label="map_overlay_rt midpoint lambda",
    )
    text = _replace_once(
        text,
        """              const auto& e = d_base_map.get_edge(eid);
              ipol = d_base_map.get_face_id(e);
""",
        """              ipol = d_base_map.get_face_id_for_edge_id(eid);
""",
        label="map_overlay_rt midpoint direct",
    )
    path.write_text(text, encoding="utf-8")
    print(f"[patch] applied duplicate-half-edge overlay calls to {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rayjoin_source", type=Path)
    args = parser.parse_args()
    root = args.rayjoin_source.resolve()
    patch_map_h(root / "src" / "map" / "map.h")
    patch_map_overlay(root / "src" / "app" / "map_overlay_rt.h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
