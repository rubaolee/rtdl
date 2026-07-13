from __future__ import annotations

import argparse
from pathlib import Path
import re


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one {label}, found {count}")
    return text.replace(old, new, 1)


def patch_host_code(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []

    if "#include <iomanip>" not in text:
        text = replace_once(
            text,
            "#include <limits>\n",
            "#include <limits>\n#include <cstdlib>\n#include <iomanip>\n",
            label="hostCode include insertion point",
        )
        changes.append("added cstdlib/iomanip includes")

    if "RTBH_CUDA_DEVICE" not in text:
        text = replace_once(
            text,
            "int gpuDeviceID = 1;\nOWLContext context = owlContextCreate(&gpuDeviceID, 1);\n",
            (
                "int gpuDeviceID = [](){\n"
                "  const char *deviceEnv = std::getenv(\"RTBH_CUDA_DEVICE\");\n"
                "  return deviceEnv ? std::atoi(deviceEnv) : 0;\n"
                "}();\n"
                "OWLContext context = owlContextCreate(&gpuDeviceID, 1);\n"
            ),
            label="gpuDeviceID assignment",
        )
        changes.append("made CUDA device ordinal environment-controlled")

    old_new_mode_dump = 'fprintf(outFile, "%f %f %f %f %f %f %f\\n", p.mass, p.pos.x, p.pos.y, p.pos.z, nullptr, nullptr, nullptr);'
    if (
        'fprintf(outFile, "%.9g %.9g %.9g %.9g %.9g %.9g %.9g\\n"' not in text
        and old_new_mode_dump in text
    ):
        text = replace_once(
            text,
            old_new_mode_dump,
            'fprintf(outFile, "%.9g %.9g %.9g %.9g %.9g %.9g %.9g\\n", p.mass, p.pos.x, p.pos.y, p.pos.z, 0.0f, 0.0f, 0.0f);',
            label="new-mode precise same-input dump",
        )
        changes.append("made new-mode same-input dump float-roundtrip precise")

    if "RTBH_PREPARED_ARRAYS_OUT" not in text and "int main(int ac, char **av) {" in text:
        prepared_dump_helper = r'''
bool dumpPreparedArraysForRtdl(const char *preparedOutPath) {
  std::ofstream preparedOut(preparedOutPath);
  if (!preparedOut) {
    std::cerr << "Error opening RTBH_PREPARED_ARRAYS_OUT for writing: " << preparedOutPath << std::endl;
    return false;
  }
  preparedOut << std::setprecision(9);
  preparedOut << "{\n";
  preparedOut << "  \"schema\": \"generic_aggregate_frontier_inverse_square_scalar_sum_3d_prepared_arrays_v1\",\n";
  preparedOut << "  \"contract_source\": \"rt_barneshut_author_binary_prepared_state_v1\",\n";
  preparedOut << "  \"tree_summary\": {";
  preparedOut << "\"input_body_count\": " << points.size();
  preparedOut << ", \"sorted_body_count\": " << points.size();
  preparedOut << ", \"device_node_count\": " << deviceBhNodes.size();
  preparedOut << ", \"dfs_node_count\": " << dfsBHNodes.size();
  preparedOut << ", \"bucket_size\": " << BUCKET_SIZE;
  preparedOut << ", \"grid_size\": " << gridSize;
  preparedOut << ", \"has_author_device_state\": true";
  preparedOut << "},\n";

  preparedOut << "  \"points\": [\n";
  for (size_t i = 0; i < points.size(); ++i) {
    const Point &p = points[i];
    if (i != 0) preparedOut << ",\n";
    preparedOut << "    {\"id\": " << p.idX
                << ", \"mass\": " << p.mass
                << ", \"x\": " << p.pos.x
                << ", \"y\": " << p.pos.y
                << ", \"z\": " << p.pos.z
                << "}";
  }
  preparedOut << "\n  ],\n";

  preparedOut << "  \"nodes\": [\n";
  for (size_t i = 0; i < dfsBHNodes.size(); ++i) {
    Node *node = dfsBHNodes[i];
    const deviceBhNode &dev = deviceBhNodes[i];
    if (i != 0) preparedOut << ",\n";
    preparedOut << "    {\n";
    preparedOut << "      \"id\": " << (i + 1) << ",\n";
    preparedOut << "      \"cx\": " << dev.centerOfMassX << ",\n";
    preparedOut << "      \"cy\": " << dev.centerOfMassY << ",\n";
    preparedOut << "      \"cz\": " << dev.centerOfMassZ << ",\n";
    preparedOut << "      \"half_size\": " << node->s << ",\n";
    preparedOut << "      \"mass\": " << dev.mass << ",\n";
    preparedOut << "      \"member_ids\": [";
    for (size_t j = 0; j < node->particles.size(); ++j) {
      if (j != 0) preparedOut << ", ";
      preparedOut << node->particles[j];
    }
    preparedOut << "],\n";
    preparedOut << "      \"child_ids\": [";
    bool firstChild = true;
    for (int child = 0; child < 8; ++child) {
      if (node->children[child] != nullptr) {
        if (!firstChild) preparedOut << ", ";
        preparedOut << (node->children[child]->dfsIndex + 1);
        firstChild = false;
      }
    }
    preparedOut << "],\n";
    preparedOut << "      \"depth\": 0,\n";
    preparedOut << "      \"dfs_index\": " << i << ",\n";
    preparedOut << "      \"resume_index\": null,\n";
    preparedOut << "      \"cell_cx\": " << node->quadrantX << ",\n";
    preparedOut << "      \"cell_cy\": " << node->quadrantY << ",\n";
    preparedOut << "      \"cell_cz\": " << node->quadrantZ << ",\n";
    preparedOut << "      \"is_leaf\": " << (dev.isLeaf == 1 ? "true" : "false") << ",\n";
    preparedOut << "      \"author_device\": {";
    preparedOut << "\"next_ray_location_x\": " << dev.nextRayLocation_x;
    preparedOut << ", \"next_ray_location_y\": " << dev.nextRayLocation_y;
    preparedOut << ", \"next_prim_id\": " << dev.nextPrimId;
    preparedOut << ", \"auto_rope_ray_location_x\": " << dev.autoRopeRayLocation_x;
    preparedOut << ", \"auto_rope_ray_location_y\": " << dev.autoRopeRayLocation_y;
    preparedOut << ", \"auto_rope_prim_id\": " << dev.autoRopePrimId;
    preparedOut << ", \"num_particles\": " << dev.numParticles;
    preparedOut << "}\n";
    preparedOut << "    }";
  }
  preparedOut << "\n  ],\n";

  preparedOut << "  \"ordered_primary_launch_rays\": [\n";
  for (size_t i = 0; i < orderedPrimaryLaunchRays.size(); ++i) {
    const CustomRay &ray = orderedPrimaryLaunchRays[i];
    if (i != 0) preparedOut << ",\n";
    preparedOut << "    {\"launch_index\": " << i
                << ", \"point_id\": " << ray.pointID
                << ", \"prim_id\": " << ray.primID
                << ", \"origin_x\": " << ray.orgin.x
                << ", \"origin_y\": " << ray.orgin.y
                << ", \"origin_z\": " << ray.orgin.z
                << "}";
  }
  preparedOut << "\n  ]\n";
  preparedOut << "}\n";
  return true;
}

'''
        text = replace_once(
            text,
            "int main(int ac, char **av) {\n",
            prepared_dump_helper + "\nint main(int ac, char **av) {\n",
            label="prepared arrays dump helper insertion point",
        )
        changes.append("added RTBH_PREPARED_ARRAYS_OUT author prepared-state dump")

    if (
        "RTBH_PREPARED_ARRAYS_OUT" in text
        and "if (const char *preparedOutPath = std::getenv(\"RTBH_PREPARED_ARRAYS_OUT\"))" not in text
        and "installAutoRopes(root);\n  auto auto_ropes_end = chrono::steady_clock::now();\n  profileStats->installAutoRopesTime" in text
    ):
        text = replace_once(
            text,
            (
                "  installAutoRopes(root);\n"
                "  auto auto_ropes_end = chrono::steady_clock::now();\n"
                "  profileStats->installAutoRopesTime += chrono::duration_cast<chrono::microseconds>(auto_ropes_end - auto_ropes_start);\n"
            ),
            (
                "  installAutoRopes(root);\n"
                "  auto auto_ropes_end = chrono::steady_clock::now();\n"
                "  profileStats->installAutoRopesTime += chrono::duration_cast<chrono::microseconds>(auto_ropes_end - auto_ropes_start);\n"
                "\n"
                "  if (const char *preparedOutPath = std::getenv(\"RTBH_PREPARED_ARRAYS_OUT\")) {\n"
                "    if (!dumpPreparedArraysForRtdl(preparedOutPath)) {\n"
                "      return 2;\n"
                "    }\n"
                "  }\n"
            ),
            label="prepared arrays dump call insertion point",
        )
        changes.append("wired RTBH_PREPARED_ARRAYS_OUT after auto-rope installation")

    if "RTBH_FORCE_OUT" not in text:
        text = replace_once(
            text,
            (
                "  const float *rtComputedForces = (const float *)owlBufferGetPointer(ComputedForcesBuffer,0);\n"
                "  auto end1 = std::chrono::steady_clock::now();\n"
                "  profileStats->forceCalculationTime = std::chrono::duration_cast<std::chrono::microseconds>(end1 - start1);\n"
            ),
            (
                "  const float *rtComputedForces = (const float *)owlBufferGetPointer(ComputedForcesBuffer,0);\n"
                "  auto end1 = std::chrono::steady_clock::now();\n"
                "  profileStats->forceCalculationTime = std::chrono::duration_cast<std::chrono::microseconds>(end1 - start1);\n"
                "\n"
                "  if (const char *forceOutPath = std::getenv(\"RTBH_FORCE_OUT\")) {\n"
                "    std::ofstream forceOut(forceOutPath);\n"
                "    if (!forceOut) {\n"
                "      std::cerr << \"Error opening RTBH_FORCE_OUT for writing: \" << forceOutPath << std::endl;\n"
                "      return 2;\n"
                "    }\n"
                "    forceOut << std::setprecision(9);\n"
                "    for (size_t i = 0; i < points.size(); ++i) {\n"
                "      forceOut << i << \" \" << rtComputedForces[i] << \"\\n\";\n"
                "    }\n"
                "  }\n"
            ),
            label="force dump insertion point",
        )
        changes.append("added RTBH_FORCE_OUT per-body force dump")

    path.write_text(text, encoding="utf-8")
    return changes


def patch_geom_types(path: Path, *, body_count: int) -> list[str]:
    text = path.read_text(encoding="utf-8")
    pattern = r"(?m)^constexpr\s+int\s+NUM_POINTS\s*=\s*[0-9]+\s*;"
    replacement = f"constexpr int NUM_POINTS = {body_count};"
    text, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"expected exactly one NUM_POINTS definition, patched {count}")
    path.write_text(text, encoding="utf-8")
    return [f"set NUM_POINTS={body_count}"]


def apply_patch_to_source(source_root: Path, *, body_count: int) -> dict[str, object]:
    sample = source_root / "samples" / "cmdline" / "s01-rtbarneshut"
    host_code = sample / "hostCode.cu"
    geom_types = sample / "GeomTypes.h"
    if not host_code.exists():
        raise FileNotFoundError(host_code)
    if not geom_types.exists():
        raise FileNotFoundError(geom_types)
    changes = {
        "hostCode.cu": patch_host_code(host_code),
        "GeomTypes.h": patch_geom_types(geom_types, body_count=body_count),
    }
    return {
        "source_root": str(source_root),
        "body_count": body_count,
        "changes": changes,
        "comparator_effect": (
            "build/device/output instrumentation only; algorithmic tree traversal "
            "and force accumulation logic are not intentionally changed. The new-mode "
            "input dump uses float round-trip precision so treelogy same-input "
            "comparison uses the actual generated input rather than a six-decimal "
            "serialization. RTBH_PREPARED_ARRAYS_OUT is diagnostic instrumentation "
            "that dumps the author binary's sorted points, DFS aggregate tree, "
            "device node metadata, and launch order after auto-rope installation."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply RT-BarnesHut AuthorOfficial compatibility/comparator patch.")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--body-count", type=int, default=32768)
    args = parser.parse_args()
    payload = apply_patch_to_source(args.source_root.resolve(), body_count=args.body_count)
    import json

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
