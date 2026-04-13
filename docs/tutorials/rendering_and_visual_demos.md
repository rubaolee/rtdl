# Tutorial: RTDL Plus Python Rendering

RTDL is not a rendering engine. But it can act as the accelerated compute/query core
inside one:

- RTDL handles ray/triangle-style query work
- Python handles scene setup, shading, animation, and output

This tutorial shows what that composition looks like in practice.

Command convention used below:

- use `python`
- if your shell only provides `python3`, substitute `python3`
- Windows PowerShell uses:
  - `$env:PYTHONPATH = "src;."`
  - then `python ...`

---

## First demo: lit ball

This is the best small demonstration of the RTDL-plus-Python split.

Run:

```bash
PYTHONPATH=src:. python examples/visual_demo/rtdl_lit_ball_demo.py \
    --backend cpu_python_reference --compare-backend none \
    --width 48 --height 24 --triangles 128 --output /dev/null
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\visual_demo\rtdl_lit_ball_demo.py ^
    --backend cpu_python_reference --compare-backend none ^
    --width 48 --height 24 --triangles 128 --output NUL
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/visual_demo/rtdl_lit_ball_demo.py `
    --backend cpu_python_reference --compare-backend none `
    --width 48 --height 24 --triangles 128 --output NUL
```

Expected output excerpt:

```text
            @@%%##*+=--:.
         @@@@@@@%%##*+=-:.
       @@@@@@@@@@%##*+=-:.
```

### The RTDL kernel

RTDL does one core thing in this demo: count how many sphere triangles each
ray intersects.

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_hitcount_demo():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

### What Python does with the rows

Python receives the rows and then handles:

- hit-span reconstruction
- surface normal estimation
- brightness calculation
- ASCII character lookup
- frame assembly
- file writing

That is the honest boundary: RTDL is the accelerated core; Python is the application
layer.

Source file:

- [examples/visual_demo/rtdl_lit_ball_demo.py](../../examples/visual_demo/rtdl_lit_ball_demo.py)

---

## Main 3D demo: hidden star stable ball

This larger demo adds shadow queries and multi-step scene logic.

Run a small sanity check:

```bash
PYTHONPATH=src:. python examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py \
    --backend cpu_python_reference --compare-backend none \
    --width 48 --height 24 \
    --latitude-bands 6 --longitude-bands 12 \
    --frames 1 --jobs 1 \
    --shadow-mode rtdl_light_to_surface \
    --output-dir build/quick_hidden_star_demo
```

What RTDL handles:

1. primary visibility queries
2. shadow-ray queries

What Python handles:

- mesh generation
- scanline construction
- shading
- animation control
- frame packaging

Source file:

- [examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py](../../examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)
- [examples/visual_demo/render_hidden_star_chunked_video.py](../../examples/visual_demo/render_hidden_star_chunked_video.py)
- [Hidden-Star 4K Render Work Report](../reports/hidden_star_4k_render_work_report_2026-04-11.md)
- [RTDL 4K demo video](https://youtu.be/d3yJB7AmCLM)

---

## Other visual demos

These follow the same pattern:

- `rtdl_orbiting_star_ball_demo.py`
- `rtdl_orbit_lights_ball_demo.py`
- `rtdl_smooth_camera_orbit_demo.py`
- `rtdl_spinning_ball_3d_demo.py`

All of them use RTDL for geometric queries and Python for the surrounding
application.

---

## The model to remember

```text
Python application
  -> scene, light, camera, animation
  -> calls rt.run_*(...)
  -> receives rows
  -> shading, output, packaging

RTDL kernel
  -> traversal
  -> predicate/refine
  -> emitted rows
```

RTDL is not a renderer. The demos still belong in the repo because they show
RTDL acting as a real accelerated compute/query core inside larger Python applications.

---

## Next

- [Segment And Polygon Workloads](segment_polygon_workloads.md)
- [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
- [Tutorial Index](README.md)
