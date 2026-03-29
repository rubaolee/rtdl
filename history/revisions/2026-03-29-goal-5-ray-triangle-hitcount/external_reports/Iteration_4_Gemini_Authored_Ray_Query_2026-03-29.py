import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def ray_triangle_hit_counter():
    rays = rt.input("rays", rt.Rays, role="probe")
    triangles = rt.input("triangles", rt.Triangles, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])

GEMINI_RAY_QUERY_KERNELS = (ray_triangle_hit_counter,)
