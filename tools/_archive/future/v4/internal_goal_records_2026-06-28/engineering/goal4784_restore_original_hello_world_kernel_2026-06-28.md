# Goal4784 Restore Original Hello-World Kernel Model

Status: `implemented_pending_antigravity_review`

Goal4784 corrects the previous Goal4783 mistake. The earlier Goal4783 rewrite
turned hello world into a fixed-radius relation lesson. That was the wrong
placement. The original RTDL hello-world idea was better: a tiny ray/triangle
kernel that prints `hello, world`.

## Decision

Keep the original teaching model:

```text
input geometry -> traverse -> refine -> emit rows -> Python program result
```

Do not teach hello world as:

```text
planner/catalog lookup
```

Do not teach hello world as:

```text
fixed-radius candidate-row lesson
```

Those are later lessons. Hello world should be the first RTDL kernel.

## Files Changed

| File | Action |
| --- | --- |
| `examples/tutorial_programs/hello_world.py` | Restored the original RTDL kernel structure using `rt.kernel`, `rt.input`, `rt.traverse`, `rt.refine`, `rt.emit`, and `rt.run_cpu_python_reference`. |
| `tutorials/current/01_first_run.md` | Replaced fixed-radius mental model with the first kernel model: input geometry, traverse, refine, emit rows, Python result. |
| `tutorials/current/02_hello_world.md` | Rewrote the page as a true hello-world lesson: command, expected `hello, world`, kernel, line-by-line interpretation, and V4 front-door follow-up. |
| `examples/tutorial_programs/README.md` | Corrected the hello-world row from planner request to first RTDL kernel. |
| `docs/engineering/tutorial_programs_structure_and_content_plan_2026-06-28.md` | Corrected the planned lesson from first operator request to first RTDL kernel. |

## What The Program Now Does

The program builds a tiny scene:

- one horizontal ray;
- three rectangles;
- only the middle rectangle intersects the ray;
- the middle rectangle carries the label `hello, world`;
- rectangles are encoded as two triangles each because this RTDL path uses
  ray/triangle hits.

The kernel is:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def hello_world_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

Python runs the portable reference path:

```python
rows = rt.run_cpu_python_reference(hello_world_kernel, rays=rays, triangles=triangles)
```

Then Python maps the emitted row back to the visible rectangle label and prints:

```text
hello, world
```

## Why This Is Needed

The original hello-world program had the correct educational core:

- it was a real RTDL kernel;
- it showed RTDL's DSL verbs;
- it produced the normal hello-world output;
- it did not hide the logic behind a one-line wrapper.

The only real problems were old path/version framing and public-surface drift.
The right fix was to modernize and re-place it, not to replace it with a
planner/fixed-radius demo.

## Linux Verification

Validation ran on local Linux `192.168.1.20`, in the temporary checkout:

```text
/tmp/rtdl_goal4783_check
```

Commands:

```bash
cd /tmp/rtdl_goal4783_check
PYTHONPATH=src:. python3 examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python3 -m py_compile examples/tutorial_programs/hello_world.py
grep -R -n 'input geometry\|traverse\|refine\|emit\|first RTDL kernel\|hello, world' \
  tutorials/current/01_first_run.md \
  tutorials/current/02_hello_world.md \
  examples/tutorial_programs/hello_world.py \
  examples/tutorial_programs/README.md
```

Observed output:

```text
hello, world
```

`py_compile` passed. The grep check confirmed the changed tutorial and index
now teach the RTDL kernel model rather than planner/fixed-radius material.

## Goal-Level Decision Check

1. Did I make a stupid decision?
   - Yes. Goal4783 incorrectly moved a fixed-radius relation lesson into hello
     world and treated that as an improvement.
2. What action made it stupid?
   - I failed to check the original archived hello-world program before writing
     the new first lesson.
3. Was there another path?
   - Yes: compare the old hello world first, preserve its good kernel model,
     and only modernize the public path and wording.
4. Did I switch to the better path?
   - Yes. Goal4784 restores the original kernel teaching model and validates it
     on Linux.

## Non-Authorization

This does not authorize:

- claiming the entire tutorial ladder is done;
- accepting sorting/ranking tutorials;
- publishing a new tag;
- skipping remaining tutorial goals.

Goal4783's fixed-radius hello-world approval should be considered superseded by
this correction if Antigravity approves Goal4784.
