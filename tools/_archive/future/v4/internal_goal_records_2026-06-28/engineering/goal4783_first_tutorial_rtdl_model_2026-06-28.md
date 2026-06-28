# Goal4783 First Tutorial Rewrite: RTDL Programming Model

Status: `implemented_pending_antigravity_review`

Goal4783 rewrites the first tutorial step so it teaches RTDL's programming
model instead of presenting a catalog dump or a black-box helper call.

## Files Changed

| File | Change |
| --- | --- |
| `tutorials/current/01_first_run.md` | Reframed RTDL as `user data -> candidate relation rows -> RTDL operator -> continuation -> result`. |
| `tutorials/current/02_hello_world.md` | Replaced the planner-only explanation with a concrete fixed-radius relation lesson. |
| `examples/tutorial_programs/hello_world.py` | Replaced JSON status output with a runnable teaching program that prints candidate rows, neighbor rows, a count continuation, and the V4 operator request. |

## What Was Written

The first lesson now uses a tiny fixed-radius problem:

```text
queries:    q1=(0,0), q2=(2,0)
references: r10=(0.1,0.1), r11=(0.8,0), r12=(2.2,0)
radius:     0.5
```

The program shows the lowering explicitly:

```text
query points + reference points -> candidate relation rows
candidate rows -> inside-radius neighbor rows
neighbor rows -> count continuation
```

It then asks the V4 front door for the corresponding operator surface:

```python
plan = rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
```

The tutorial states that the tiny Python loop is only a teaching mirror. It is
not presented as the implementation strategy for real workloads. Later lessons
replace the mirror with prepared RTDL operators and device-array surfaces.

## Why This Is Needed

The previous first lesson proved only that the planner could be called. That is
not enough for a language tutorial. A new user needs to see the central RTDL
idea immediately:

1. start from ordinary program data;
2. lower the problem into relation rows;
3. use an RTDL operator for the RT-shaped relation;
4. use a continuation to turn rows into an application result.

Without this lesson, later examples such as nearest neighbor, sorting/ranking,
spatial join, triangle counting, and RayJoin look like unrelated wrappers. With
this lesson, they become variations of the same model.

## Linux Verification

The user directed that tutorial validation be run on local Linux. I created a
temporary Linux copy from:

```text
~/work/rtdl_v4_release_final_20260627
```

Then I copied the three Goal4783 files into:

```text
/tmp/rtdl_goal4783_check
```

Commands run on `192.168.1.20`:

```bash
cd /tmp/rtdl_goal4783_check
PYTHONPATH=src:. python3 examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python3 -m py_compile examples/tutorial_programs/hello_world.py
grep -R -n 'candidate relation rows\|count continuation\|fixed_radius' \
  tutorials/current/01_first_run.md \
  tutorials/current/02_hello_world.md \
  examples/tutorial_programs/hello_world.py
```

Result:

```text
RTDL hello world: fixed-radius relation
...
Candidate relation rows:
  query=1 ref=10 distance_sq=0.0200 inside=yes
  query=1 ref=11 distance_sq=0.6400 inside=no
  query=1 ref=12 distance_sq=4.8400 inside=no
  query=2 ref=10 distance_sq=3.6200 inside=no
  query=2 ref=11 distance_sq=1.4400 inside=no
  query=2 ref=12 distance_sq=0.0400 inside=yes
...
Continuation result:
  query=1 neighbor_count=1
  query=2 neighbor_count=1
...
api_surface=v4_fixed_radius_count_threshold_2d_device_arrays
generic_primitive=FIXED_RADIUS_COUNT_THRESHOLD_2D
```

`py_compile` passed. The grep check found the required concepts in the changed
tutorial files.

## Goal-Level Decision Check

1. Did I make a stupid decision?
   - I initially validated on Windows even though the user had already directed
     Linux-style validation. That was wrong for this project context.
2. If yes, what actions made it stupid?
   - Treating the noisy Windows `py -3` environment as acceptable first
     validation instead of immediately using `192.168.1.20`.
3. Was there another path?
   - Yes: create a Linux temporary checkout first, copy the changed files, and
     run the exact tutorial command there.
4. Did I switch to the better path?
   - Yes. Linux validation is now the recorded evidence for this goal.

## Effect Assessment

Current effect: the first tutorial now teaches one real RTDL mental model:
relation rows plus continuation, connected to a V4 operator request.

What this does well:
- removes the old "planner status JSON" feeling;
- shows the data transformation a user must understand;
- keeps the first lesson runnable without GPU hardware;
- names the V4 operator surface without making it a magic app wrapper.

What it does not yet solve:
- it does not teach sorting, nearest neighbor, partners, or callbacks;
- it does not make the entire tutorial surface release-quality;
- it does not close Goal4786's blocked `sorting_rows.py` problem.

## Non-Authorization

This goal does not authorize:
- claiming all tutorials are fixed;
- accepting `sorting_rows.py`;
- publishing a tutorial release tag;
- skipping the remaining tutorial goals.
