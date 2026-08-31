# Goal5831 — public GPU surface, terminology, and denominator report

## Result

**PASS at exact current-scope factual-repair scope.** Goal5831 answers the
previously ambiguous question “there are two of what?” and removes the false
statement that caller-authored source cannot reach the public GPU path. It ran
zero GPU work, zero formal workers, and zero registered performance timings;
no product source was changed and no external review was requested.

The number **two** has two exact current meanings:

1. RTDL implements two physical geometry kinds: custom primitives represented
   by custom AABBs, and built-in triangles.
2. RTDL provides two fixed protocol constructors:
   `custom_aabb_bounded_relation_v1` and
   `builtin_triangle_reduction_v1`.

It does **not** mean that RTDL covers two out of all application protocols, and
it does **not** enumerate the complete public GPU surface. That surface also
contains one bounded caller-authored built-in-triangle `u32x3` Callback-IR
template. Particle strict-interior is one public specialization of that
template, not a third generic geometry or protocol constructor.

## Exact denominators

| Layer | Platform/current fact | RTDL coverage |
| --- | ---: | ---: |
| OptiX 9 build-input kinds | 6 | routes instantiate 2/6 kinds |
| OptiX 9 leaf-primitive kinds | 4 | routes instantiate 2/4 kinds |
| RTDL physical geometry kinds | 2 | 2 |
| Fixed protocol constructors | 2 | 2 |
| Bounded caller-authored GPU templates | 1 | 1 |
| Public application specializations | 1 | 1 (Particle) |
| Composition batches | 6 | M1–M6; not protocol families |
| Project-authored systems / selected lanes | 9 / 13 | reuse evidence only |
| Prospective frozen-core new-shape exams | — | 0 |
| External human authors | — | 0 |
| Application-semantic protocol shapes | open set | no finite denominator |

The six pinned OptiX 9 build-input kinds are triangles, custom primitives,
instances, instance pointers, curves, and spheres. The four leaf-primitive
kinds are triangles, custom primitives, curves, and spheres; instances and
instance pointers are scene-graph inputs.

The numerator is **kind-presence**, not category closure: current public routes
instantiate `TRIANGLES` and `CUSTOM_PRIMITIVES`. It does not mean that every
flag, update/refit, motion, SBT, multi-build-input, or instancing configuration
inside those kinds is supported.

## Why the implementation began with these two

The two were author-selected because they span two materially different hit
production boundaries and fit the project’s applications:

- built-in triangles obtain intersection and core hit facts from OptiX;
- custom primitives execute an application intersection callback and produce
  explicit hit attributes.

This is a useful mechanism contrast. It is **not** a prospective draw, a
representative sample, or evidence that the open protocol-shape universe is
covered.

## What was corrected

- The manuscript, README, API reference, tutorial, and nine-app coverage page
  now separate build-input kind, leaf primitive, physical geometry,
  constructor, bounded authoring template, application specialization,
  composition batch, protocol shape, instance, and deployment.
- The public caller-authored triangle path is now disclosed. Its exact ceiling
  is a static built-in-triangle GAS, `u32x3` payload/output, two primitive
  metadata views, trace depth one, and callable depth zero.
- The paper no longer turns nine applications, thirteen lanes, or M1–M6 into a
  family denominator.
- The paper states both finite platform coverage ratios and the absence of a
  finite application-semantic denominator.

## Scientific claim ceiling after Goal5831

The strongest accurate statement is:

> RTDL currently provides two fixed protocol constructors over two physical
> geometry kinds plus one bounded caller-authored built-in-triangle `u32x3`
> template. Its current routes instantiate two of six OptiX 9 build-input enum
> kinds and two of four leaf-primitive kinds (kind-presence only, not
> feature-complete category support). The application-semantic protocol universe is open;
> prospective frozen-core new-shape exams remain zero.

Goal5831 repairs the measurement language. It does not itself add a new
geometry kind, generic compiler, user study, or generalization result.
