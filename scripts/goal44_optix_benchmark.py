import rtdsl as rt
import time
import json
import os
import sys
from rtdsl import datasets

def run_benchmark():
    dataset_dir = "build/datasets/uscounty_zipcode/uscounty_feature_layer"
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory {dataset_dir} not found.")
        sys.exit(1)

    print(f"--- Goal 44: OptiX vs Embree Performance Benchmark ---")
    print(f"Dataset: US County Feature Layer (Staged)")

    # Load US County Polygons
    print(f"Step: Loading ArcGIS pages into CDB (max_features=250)...")
    cdb = datasets.arcgis_pages_to_cdb(dataset_dir, name="uscounty", max_features=250)
    print(f"Step: Converting CDB chains to polygons...")
    poly_list = datasets.chains_to_polygons(cdb)
    print(f"Step: Packing {len(poly_list)} polygons for RTDL...")
    poly_ids = []
    v_offsets = []
    v_counts = []
    v_xy = []
    current_offset = 0
    for p in poly_list:
        poly_ids.append(p["id"])
        v_offsets.append(current_offset)
        v_counts.append(len(p["vertices"]))
        for x, y in p["vertices"]:
            v_xy.extend([float(x), float(y)])
        current_offset += len(p["vertices"])
    
    polys = rt.pack_polygons(ids=poly_ids, vertex_offsets=v_offsets, vertex_counts=v_counts, vertices_xy=v_xy)
    print(f"Loaded {polys.polygon_count} polygons.")

    # Create synthetic points (10,000 random points within US bounds)
    # Approx US bounds: x in [-125, -66], y in [24, 49]
    import random
    n_points = 10000
    p_ids = list(range(n_points))
    px = [random.uniform(-125, -66) for _ in range(n_points)]
    py = [random.uniform(24, 49) for _ in range(n_points)]
    points = rt.pack_points(ids=p_ids, x=px, y=py)
    print(f"Generated {n_points} synthetic points.")

    @rt.kernel(backend="rtdl", precision="float_approx")
    def point_in_county():
        polys = rt.input("polys", rt.Polygons)
        points = rt.input("points", rt.Points)
        candidates = rt.traverse(points, polys, accel="bvh")
        hits = rt.refine(candidates, predicate=rt.point_in_polygon())
        return rt.emit(hits, fields=["point_id", "poly_id"])

    # 1. Embree (CPU)
    print("\nRunning Embree (CPU) benchmark...")
    start_cpu = time.perf_counter()
    cpu_result = rt.run_embree(point_in_county, polys=polys, points=points, result_mode="raw")
    end_cpu = time.perf_counter()
    cpu_time = end_cpu - start_cpu
    print(f"Embree Time: {cpu_time:.4f}s (Raw results: {cpu_result.row_count})")

    # 2. OptiX (GPU)
    # Set fallback environment variables for this host
    os.environ["RTDL_OPTIX_PTX_COMPILER"] = "nvcc"
    os.environ["RTDL_NVCC"] = "/usr/bin/nvcc"
    
    print("\nRunning OptiX (GPU) benchmark...")
    # First call includes JIT overhead
    start_optix_jit = time.perf_counter()
    optix_result = rt.run_optix(point_in_county, polys=polys, points=points, result_mode="raw")
    end_optix_jit = time.perf_counter()
    optix_jit_time = end_optix_jit - start_optix_jit
    print(f"OptiX Time (with JIT): {optix_jit_time:.4f}s (Raw results: {optix_result.row_count})")

    # Second call for "warm" performance
    start_optix_warm = time.perf_counter()
    optix_result_warm = rt.run_optix(point_in_county, polys=polys, points=points, result_mode="raw")
    end_optix_warm = time.perf_counter()
    optix_warm_time = end_optix_warm - start_optix_warm
    print(f"OptiX Time (Warm): {optix_warm_time:.4f}s")

    # Summary
    speedup = cpu_time / optix_warm_time if optix_warm_time > 0 else 0
    print(f"\n--- Summary ---")
    print(f"CPU (Embree): {cpu_time:.4f}s")
    print(f"GPU (OptiX):  {optix_warm_time:.4f}s (Warm)")
    print(f"Speedup:      {speedup:.2f}x")

    # Save results
    results = {
        "dataset": "uscounty_zipcode",
        "n_polygons": polys.polygon_count,
        "n_points": n_points,
        "embree_sec": cpu_time,
        "optix_jit_sec": optix_jit_time,
        "optix_warm_sec": optix_warm_time,
        "speedup": speedup,
        "parity": cpu_result.row_count == optix_result.row_count
    }
    with open("build/goal44_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to build/goal44_results.json")

if __name__ == "__main__":
    run_benchmark()
