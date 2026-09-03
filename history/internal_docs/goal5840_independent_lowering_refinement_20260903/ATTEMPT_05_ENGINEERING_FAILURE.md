# Goal5840 Formal Attempt 05 Engineering Failure

Date: 2026-09-03

## Classification

`SPHERE_RUNTIME_NATIVE_LIBRARY_ENV_BINDING_ENGINEERING_FAILURE`

This was a formal-runner environment-binding defect after three successful
public-route executions, three successful raw evidence captures, and three
independently accepted five-property reports. It is not a scientific failure,
a lowering counterexample, a mutation-suite result, or an accepted complete
Goal5840 result.

The fourth frozen mode entered the route but failed in `prepare()` before its
first OptiX launch. The runner therefore stopped before the fourth output,
fourth bundle, runtime trust-root publication, mutation execution, or
`RESULT.json` publication.

## Immutable Execution Identity

- Formal attempt number: `5`
- Source commit:
  `16fb9523e3688e792ff4083a6600434c75d8c9e6`
- Source tree:
  `8914c23fe4ba8d181bf201b6faf7dd706b10359e`
- Post-Attempt-04 repair-authority internal seal:
  `bf611d0ae15416f8d056c50097aedcb530b1c2b6f2cd004cf431bc2f4b66e3ab`
- Pod endpoint used: `root@213.173.108.100:12943`
- GPU: `NVIDIA RTX 2000 Ada Generation`
- GPU UUID: `GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`
- Driver: `580.159.04`
- Compute capability: `8.9`
- CUDA toolkit: `12.8`
- OptiX SDK: `9.0.0`
- Detached source checkout:
  `/workspace/rtdl-goal5840-attempt05-16fb952`
- Native DSO path:
  `/workspace/goal5840-build-attempt05-16fb952/librtdl_optix_goal5840.so`
- Native DSO bytes: `7,181,936`
- Native DSO SHA-256:
  `0a82915b7b2c3afcb5d19e4c634d1c17a27e3ce7a9d65a02b6d0fe3fda8e20bb`
- Native build manifest path:
  `/workspace/goal5840-build-attempt05-16fb952/NATIVE_BUILD.json`
- Native build manifest file SHA-256:
  `b44ac91529383563e3b48b6396fb26e88f903253bed35c03e7b044637175fd8b`
- Native build manifest internal result seal:
  `2931e0ad68ec24c8e7eceb87141ecd28a2c6efc31e8ea0df5d3b9d9234b746ea`
- Output directory:
  `/workspace/goal5840-evidence-attempt05-16fb952`

The exact detached checkout was clean before the native build, before the
formal runner, and during the post-failure read-only inventory. The fresh
build exported all 17 required Goal5840 symbols.

## Published Failure Artifacts

The formal runner published exactly six files before stopping fail closed:

| Artifact | Bytes | File SHA-256 | UTC mtime |
|---|---:|---|---|
| `mode_01_capacity_fail_closed_collection_bundle.json` | 1,364,072 | `944f4dd717af365e31ad5d624dbd7ed5a8b71a8e5d6c6304c5336c348b6242c3` | `2026-09-03T11:08:28Z` |
| `mode_01_capacity_fail_closed_collection_independent_check.json` | 3,967 | `246a867b35a793439926e65e9791d4874525ba937bb793d9b737b215094439da` | `2026-09-03T11:08:29Z` |
| `mode_02_all_hit_count_bundle.json` | 806,033 | `84645793be976b021bea510365d6936a67df056dbc837ed710093ea8ac191645` | `2026-09-03T11:08:33Z` |
| `mode_02_all_hit_count_independent_check.json` | 3,917 | `423e6f61672cf91110089c38409e1befee4fb26d506104214580d5d577fe1431` | `2026-09-03T11:08:33Z` |
| `mode_03_weighted_hit_count_bundle.json` | 806,393 | `990eb99867984d959afdd2d65ba804d4813620e74108b3531bd0e8de192b64a4` | `2026-09-03T11:08:37Z` |
| `mode_03_weighted_hit_count_independent_check.json` | 3,917 | `8c2ee19cfea08ab192f9c0bab89dda9d35383f0044bdcd101785e932753213db` | `2026-09-03T11:08:37Z` |

The three bundle internal seals are respectively:

- `1f93c9f763f28b72247b88e048ca50a2d62f1431e32da732dfb59662f8a55531`
- `1818eaa45162b94215060e688639d32e9f0ffde2c521354f955abe6f586e67c7`
- `14de9b974fb0f873899aaa782a4febc9118661a5b6ec0513402bd4149f3203c5`

The three independent reports each have verdict `ACCEPT`, five passes, and
zero rejects. Their internal report seals are respectively:

- `aba46744b907f16c44700cd39c14c67b3de3c048217a9c9b02c1bb2a05596b90`
- `40d760e5932e6e7e66f0e4618a29a32d620c2b8a4b743192065842447c0bb8b7`
- `449af0f81b8e434f1fd525ac50bcd485bbe58afe96245397112cb4ea08b3dc87`

`RUNTIME_TRUST_ROOTS.json`, `EXACT_BUNDLE_MUTATION_RESULT.json`, and
`RESULT.json` do not exist in the Attempt05 directory. These six files remain
Attempt05 partial evidence. They are identified here by content hash; they are
not substituted into a successor result.

## Observed Formal-Runner Sequence

1. Repository, frozen-core, preregistration, four prior incidents, four prior
   repair authorities, fresh native build, exported-symbol, and machine
   preflight checks passed.
2. Frozen mode 1,
   `stable::bounded_relation::canonical_bounded_pair_collection::capacity_fail_closed_collection`,
   returned its frozen expected output, produced true-OptiX traversal evidence,
   and passed all five independent properties.
3. Frozen mode 2,
   `stable::triangle_reduction::checked_u64_reduction::all_hit_count`, returned
   its frozen expected output, produced true-OptiX traversal evidence, and
   passed all five independent properties.
4. Frozen mode 3,
   `stable::triangle_reduction::checked_u64_reduction::weighted_hit_count`,
   returned its frozen expected output, produced true-OptiX traversal evidence,
   and passed all five independent properties.
5. Frozen mode 4,
   `prospective::builtin_sphere::any_hit_count_continue_u64_per_query::accept_every_hit_and_continue`,
   compiled and materialized its route, then failed while preparing static
   input. `optix_runtime._find_optix_library()` raised `FileNotFoundError`
   because `RTDL_OPTIX_LIB` was absent.
6. The fourth mode performed zero OptiX launches and returned no output. The
   runner stopped before publishing its bundle or checker report.

## Root-Cause Diagnosis

The formal runner accepted one exact DSO through `--native`. Stable bounded and
triangle targets propagated that path through their explicit native target.
The prospective sphere prepared runtime independently resolves its provider
through `optix_runtime._load_optix_library()`, whose supported exact-path entry
is the `RTDL_OPTIX_LIB` environment variable. The runner neither set that
variable from `--native` nor rejected a missing or conflicting value during
preflight.

The same fresh DSO was present, valid, driver-compatible, hash-bound to the
source commit, and exported the sphere ABI. The failure therefore does not
require a provider, runtime, route, compiler, fixture, oracle, checker,
mutation, or frozen semantic-core change. The evidence harness must bind the
already-authoritative `--native` path to `RTDL_OPTIX_LIB` before any route is
materialized and reject a pre-existing different binding.

## Post-Failure Diagnostic Disclosure

After failure, pod commands only listed, statted, hashed, and parsed the six
already-written JSON files, checked absence of the three terminal result files,
hashed the preserved DSO/build manifest, and checked Git custody. No route was
rerun. No additional OptiX launch, evidence capture, mutation application, or
GPU diagnostic process occurred.

## Counts At Failure Boundary

Formal Attempt05 alone:

- runner processes started: `1`
- frozen modes entered: `4`
- public route expected outputs returned: `3`
- published evidence bundles: `3`
- published independent property reports: `3`
- independently accepted per-mode reports: `3`
- independent property passes: `15`
- sphere OptiX launches: `0`
- published mutation applications: `0`
- accepted complete Goal5840 results: `0`

Cumulative through Attempts 01--05:

- formal runner processes started: `5`
- frozen modes entered: `9`
- public route expected outputs returned: `8`
- published evidence bundles: `6`
- published independent property reports: `6`
- independently accepted per-mode reports: `4`
- published mutation applications: `0`
- accepted complete Goal5840 results: `0`

The two post-Attempt-02 diagnostic launches remain separately classified and
unaccepted. Attempts 03--05 added zero post-failure GPU diagnostic launches.

## Permitted Repair Boundary

A successor authority may permit only:

- adding a fail-closed runner helper that binds the exact resolved `--native`
  path to `RTDL_OPTIX_LIB` before route materialization;
- rejecting a pre-existing `RTDL_OPTIX_LIB` that resolves to any other file;
- recording the exact runtime-library binding in the final summary;
- adding tests for absent, matching, and conflicting environment bindings;
- appending this incident and a fifth repair authority; and
- extending capture and independent verification to bind all five incidents
  and repair authorities under a new formal Attempt06 schema.

It may not change routes, fixtures, expected outputs, declarations,
control-flow trust roots, properties, mutation selectors or replacements,
provider/native-engine code, prepared-runtime code, compiler/codegen code, the
independent target checker, or any Goal5838 frozen-core byte.

## Claim Boundary

- Independently accepted Attempt05 per-mode reports: `3`
- Accepted complete Goal5840 result: `false`
- Four-mode lowering/refinement preservation established: `false`
- General compiler soundness: `false`
- Application correctness: `false`
- Performance or speedup: `false`
- External review or consensus: `false`
