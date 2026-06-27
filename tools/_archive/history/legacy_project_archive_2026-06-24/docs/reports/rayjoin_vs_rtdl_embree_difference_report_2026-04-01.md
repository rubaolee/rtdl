# RayJoin Paper vs. Current RTDL-on-Embree Experiments

_Prepared on 2026-04-01 for external discussion with the RayJoin first author._

## Purpose

This report explains, as clearly as possible, the difference between:

- the **original RayJoin paper experiments**, and
- the **current RTDL experiments running on the local Embree backend**

The goal is to avoid overclaiming. The current RTDL results are useful and real, but they are **not yet a paper-identical RayJoin reproduction**.

The most accurate summary is:

**RTDL currently reproduces a bounded, Embree-based, locally executable analogue of part of the RayJoin evaluation structure. It does not yet reproduce the original GPU-based RayJoin results.**

## Short Version

If you need a very short explanation for a conversation, use this:

1. RayJoin’s original paper evaluates workloads on a GPU RT hardware path; RTDL currently runs on **Intel Embree on CPU only**.
2. RTDL currently reproduces the **experiment structure** for several RayJoin artifacts, but many cases are still **bounded analogues**, **fixture subsets**, **derived inputs**, or **synthetic inputs** rather than the original prepared paper datasets.
3. RTDL has implemented and executed:
   - bounded Figure 13 analogue,
   - bounded Figure 14 analogue,
   - partial Table 3 analogue,
   - bounded Table 4 / Figure 15 overlay-seed analogue.
4. RTDL has **not yet** completed:
   - full paper-scale dataset reproduction,
   - full original overlay fidelity,
   - NVIDIA / OptiX execution,
   - exact paper-scale timing comparability.

## 1. What the Original RayJoin Paper Is Doing

At the level relevant to this comparison, the RayJoin paper evaluates:

- ray-tracing-based spatial workloads,
- on a GPU-oriented execution path,
- using the paper’s own prepared datasets and experiment scripts,
- with performance figures and tables tied to that hardware/runtime setting.

The paper’s experiment structure includes:

- **Table 3**
  workload results over named dataset pairs such as:
  - `County ⊲⊳ Zipcode`
  - `Block ⊲⊳ Water`
  - continent-level `Lakes ⊲⊳ Parks` pairs
- **Figure 13**
  LSI scalability
- **Figure 14**
  PIP scalability
- **Table 4**
  overlay-related evaluation
- **Figure 15**
  overlay speedup figure

The original RayJoin results should be understood as:

- using the paper’s intended backend/runtime,
- using the paper’s intended prepared datasets,
- and reporting the paper’s actual evaluation numbers.

## 2. What RTDL Currently Does

RTDL is currently in a **pre-NVIDIA Embree phase**.

The current local system is:

- a Python-hosted DSL,
- lowered to RTDL IR and a RayJoin-shaped backend plan,
- executed through:
  - `run_cpu(...)` for semantic reference,
  - `run_embree(...)` for native local execution.

The current best-performing local path is:

- **prepared raw Embree execution**

and **not** the older dict-return path.

Current RTDL work relevant to RayJoin has already produced:

- a bounded local reproduction report (`goal23_embree_reproduction_report_2026-04-01.md`)
- a paper-style PDF (`goal23_embree_reproduction_report_2026-04-01.pdf`)
- an explicit dataset provenance and fidelity note (`rayjoin_paper_dataset_provenance.md`)

## 3. High-Level Difference Table

| Category | Original RayJoin Paper | Current RTDL-on-Embree | Implication |
| --- | --- | --- | --- |
| Execution backend | GPU-oriented RayJoin path | Intel Embree, CPU only | Current results are not GPU-comparable to the paper |
| Language model | Paper implementation | Python-hosted DSL compiled to RTDL runtime | Current work validates language/runtime expression, not just low-level execution |
| Hardware target | RT hardware setting from paper | Local Mac CPU environment | Performance numbers are not directly comparable |
| Dataset status | Paper’s prepared datasets | Mix of fixture-subset, derived-input, synthetic-input, and source-identified-but-missing families | Many current runs are analogues, not exact-input reproductions |
| Figure 13 / 14 | Original paper scale and backend | Bounded local analogue under 5-10 minute policy using synthetic-input geometry | Same structure, different scale, data type, and environment |
| Table 3 | Full named paper dataset families | Partial executed analogue rows only | Table is incomplete in current RTDL report |
| Table 4 / Figure 15 | Paper overlay evaluation | Overlay-seed analogue only | Overlay fidelity is still lower than paper intent |
| Precision claim | Paper-specific implementation | `float_approx` only | No exact/robust geometry claim |

## 4. Backend and Hardware Differences

This is the single most important difference.

### Original RayJoin

The original paper’s performance story is built around a GPU RT-style execution setting.

### Current RTDL

The current RTDL experiments are:

- **CPU reference path** for correctness
- **Embree CPU path** for native local execution

There is currently:

- **no real OptiX backend**
- **no NVIDIA GPU execution**
- **no RT-core measurement**

### Consequence

Even when the experiment names line up with the paper:

- the current RTDL numbers are **not** the same class of result as the original RayJoin performance numbers.

They are better understood as:

- a local Embree baseline,
- a language/runtime validation step,
- and a bounded pre-GPU reproduction effort.

## 5. Dataset Differences

Another major difference is the data.

### Original RayJoin

The paper uses named dataset families and prepared experiment inputs.

### Current RTDL

RTDL currently uses a mix of:

- `fixture-subset`
- `derived-input`
- `synthetic-input`
- `source-identified` dataset families that are **not yet executable locally**

The current provenance policy is documented in:

- the companion provenance note `rayjoin_paper_dataset_provenance.md`

### What is actually executed today

For Goal 23, the executed rows are limited.

#### Table 3 executed rows

Only the following local analogue rows are currently executed:

- `County ⊲⊳ Zipcode` / `lsi` / `fixture-subset`
- `County ⊲⊳ Zipcode` / `lsi` / `derived-input`
- `County ⊲⊳ Zipcode` / `pip` / `fixture-subset`
- `County ⊲⊳ Zipcode` / `pip` / `derived-input`

#### Table 3 still missing

The following paper families remain unexecuted locally:

- `Block ⊲⊳ Water` / `lsi`
- `Block ⊲⊳ Water` / `pip`
- `LKAF ⊲⊳ PKAF` / `lsi`
- `LKAF ⊲⊳ PKAF` / `pip`
- `LKAS ⊲⊳ PKAS` / `lsi`
- `LKAS ⊲⊳ PKAS` / `pip`
- `LKAU ⊲⊳ PKAU` / `lsi`
- `LKAU ⊲⊳ PKAU` / `pip`
- `LKEU ⊲⊳ PKEU` / `lsi`
- `LKEU ⊲⊳ PKEU` / `pip`
- `LKNA ⊲⊳ PKNA` / `lsi`
- `LKNA ⊲⊳ PKNA` / `pip`
- `LKSA ⊲⊳ PKSA` / `lsi`
- `LKSA ⊲⊳ PKSA` / `pip`

### Consequence

RTDL currently does **not** have a full paper-dataset reproduction.

What it does have is:

- a disciplined, explicit mapping from paper dataset families
- to current local execution status
- with substitutions clearly labeled.

## 6. Scale Differences

The current RTDL experiment policy intentionally keeps local runs bounded.

### Original RayJoin

The paper’s figures and tables reflect its original scale and hardware budget.

### Current RTDL

The current local policy is:

- keep each experiment package in about **5-10 minutes**
- so the work is practical on the current Mac

For Goal 23, the bounded local profiles are:

- Figure 13 / `lsi`
  - fixed `R = 100000`
  - varying `S = 100000, 200000, 300000, 400000, 500000`
- Figure 14 / `pip`
  - fixed `R = 100000`
  - varying `S = 2000, 4000, 6000, 8000, 10000`

These runs use **synthetic-input geometry** generated by the local RTDL scalability runner rather than exact-input or derived geographic datasets.

These are meaningful local scalability experiments, but they are **not the same scale regime or data-fidelity regime as the original paper**.

### Consequence

The current Figure 13 / Figure 14 outputs should be described as:

- **bounded local analogues**

not:

- exact reproductions of the original scalability experiments.

## 7. Workload Fidelity Differences

Some workloads are closer to the paper than others.

### LSI and PIP

These are the strongest parts of the current RTDL reproduction effort.

Why:

- workload expression exists in the DSL
- CPU semantics exist
- Embree execution exists
- bounded Figure 13 / Figure 14 analogues exist
- performance and parity work have already been done on these paths

### Overlay

Overlay is currently weaker in fidelity.

The current report explicitly labels it as:

- `overlay-seed analogue`

That means:

- RTDL has a meaningful overlay-related execution path,
- but it is **not yet equivalent to a full paper-style polygon materialization overlay result**.

### Consequence

When speaking to the RayJoin first author, the most accurate statement is:

- `lsi` and `pip` are already in a serious bounded-reproduction state on Embree
- `overlay` is still an analogue rather than a full paper-equivalent reproduction

## 8. Performance Comparability Differences

There are two different performance questions, and they must not be mixed.

### Question A: RTDL vs pure C/C++ on Embree

This is something we **have** studied locally.

From Goal 19:

- RTDL `dict` path is still much slower than native
- RTDL `prepared raw` path is close to native for `lsi` and `pip`
- RTDL `raw` path is lower-overhead than `dict`, but the strongest near-native result is the prepared path

This comparison is useful for:

- validating the DSL/runtime architecture
- showing that the Python-hosted DSL does not have to destroy native performance

### Question B: RTDL current results vs RayJoin paper performance

This is something we **cannot** claim yet.

Why:

- different backend
- different hardware
- different dataset completeness
- different scale policy

### Consequence

We can currently say:

- RTDL can get close to pure C/C++ Embree on the local backend for measured workloads

We cannot currently say:

- RTDL has matched or reproduced the RayJoin paper’s original performance claims

## 9. What the Current RTDL Results *Do* Mean

The current RTDL experiments are still valuable.

They show that:

1. the DSL can express important RayJoin-style workloads
2. the runtime and IR stack can execute them on a real local backend
3. the experiment/report pipeline is now mature enough to generate:
   - tables,
   - figures,
   - provenance notes,
   - paper-style reports
4. the project now has an honest Embree-phase baseline before GPU bring-up

So the current work is not “just a mockup.”
But it is also not yet “the RayJoin paper fully reproduced.”

## 10. Best Honest Summary for the First Author

If you want to describe the current state in one careful paragraph, use this:

> We have built a Python-hosted DSL and runtime, RTDL, that can already express and execute a substantial subset of the RayJoin workload family on a local Embree backend. We have generated bounded local analogues of Figure 13 and Figure 14 on synthetic-input geometry, partial Table 3 rows, and overlay-seed analogues for Table 4 and Figure 15. However, this is still an Embree-phase bounded reproduction effort, not a paper-identical RayJoin reproduction: we do not yet have the original GPU backend, we do not yet have complete paper dataset coverage, and our current overlay fidelity remains below the original paper’s intended end-to-end overlay evaluation.

## 11. What Still Has To Happen Before We Can Claim a Stronger Reproduction

To get closer to the original RayJoin paper, RTDL still needs:

1. fuller acquisition and conversion of the named paper dataset families
2. more complete Table 3 coverage
3. stronger overlay fidelity
4. final NVIDIA / OptiX execution
5. paper-scale experiment reruns under the true GPU backend

Until then, the current results should be described as:

- **Embree-phase bounded analogues and partial reproductions**

not:

- full RayJoin-paper reproduction

## 12. Recommended Talking Points

When you speak to the RayJoin first author, the cleanest discussion points are:

- We intentionally separated **experiment structure reproduction** from **paper-identical result claims**.
- We already have real local execution for `lsi` and `pip`, including bounded Figure 13 / Figure 14 analogues.
- We are being explicit about missing dataset families rather than silently substituting them.
- Overlay is currently reported as an analogue, not as a claim of full equivalence.
- Our next real milestone is to complete more dataset coverage on Embree and later move to the NVIDIA backend.
