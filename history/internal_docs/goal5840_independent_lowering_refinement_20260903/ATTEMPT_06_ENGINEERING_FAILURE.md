# Goal5840 Formal Attempt 06 Engineering Failure

Date: 2026-09-03

## Classification

`SPHERE_TWO_LEVEL_PHYSICAL_PLAN_REFINEMENT_CHECKER_ENGINEERING_FAILURE`

Formal Attempt06 executed all four frozen public-route modes and each route
returned its frozen expected output. It published four raw target-evidence
bundles and four independent reports. The first three reports were accepted at
five of five properties. The fourth report rejected CP005 after one successful
true-OptiX built-in-sphere launch because the independent checker incorrectly
required the sphere executable's provider-internal physical-plan SHA-256 to
equal the outer generic family-plan SHA-256.

The two hashes name different canonical plan levels. This is not a scientific
failure, a frozen-core counterexample, a mutation-suite result, or an accepted
complete Goal5840 result. The run stopped fail closed before publishing
`RUNTIME_TRUST_ROOTS.json`, `EXACT_BUNDLE_MUTATION_RESULT.json`, or
`RESULT.json`.

## Immutable Execution Identity

- Formal attempt number: `6`
- Source commit:
  `593a514637ab2075653bbd4e499c36860519bf31`
- Source tree:
  `3bdaa192a4d9975506fe4925ed4f1ed8fd21afc1`
- Post-Attempt-05 repair-authority internal seal:
  `57e986a79bffeeeb6505ca0cc4ee331ad253d4d5c426f59704ff93db31dbe64b`
- Pod endpoint used: `root@213.173.108.100:12943`
- GPU: `NVIDIA RTX 2000 Ada Generation`
- GPU UUID: `GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`
- Driver: `580.159.04`
- Compute capability: `8.9`
- CUDA toolkit: `12.8`
- OptiX SDK: `9.0.0`
- Detached source checkout:
  `/workspace/rtdl-goal5840-attempt06-593a514`
- Native DSO path:
  `/workspace/goal5840-build-attempt06-593a514/librtdl_optix_goal5840.so`
- Native DSO bytes: `7,181,936`
- Native DSO SHA-256:
  `00166cc28348982bff8c44c9a3c6859d1fb997698dc065ef2a926024a4590dd5`
- Native build manifest path:
  `/workspace/goal5840-build-attempt06-593a514/NATIVE_BUILD.json`
- Native build manifest file SHA-256:
  `77400be3b9e6a228ade69057dfbd31fe108e957ef730fd37d7bfad2ee10234cb`
- Native build manifest internal result seal:
  `ddb19d559abcc13249603c5ca140aab82a2709d6a2f6b83e49633698a6ca7597`
- Output directory:
  `/workspace/goal5840-evidence-attempt06-593a514`

The detached checkout was clean before the fresh native build, before the
formal runner, and during the post-failure read-only inventory. The exact DSO
binding introduced after Attempt05 worked: the sphere receipt names the exact
absolute DSO path and SHA-256 above.

## Published Failure Artifacts

The formal runner published exactly eight files before stopping fail closed:

| Artifact | Bytes | File SHA-256 | Internal seal | Verdict | UTC mtime |
|---|---:|---|---|---|---|
| `mode_01_capacity_fail_closed_collection_bundle.json` | 1,364,075 | `f259c779347b945229ac545fbe9765adfeff8e2fea9d27f9acc5a6c9251824ca` | `eba236fdc8b946392e6e45c1eb47d7b5e963278b8cdf0f7918b2b88c0b01ef0e` | bundle | `2026-09-03T11:33:20Z` |
| `mode_01_capacity_fail_closed_collection_independent_check.json` | 3,967 | `737cecffb9ccaf95a639e3a815bebec7e581af3ea80ac257714e4e3c67384c45` | `d76ef08ae8bae5a3c07c919c03238229138402d257a7fc1ede3a027cebac5a77` | ACCEPT 5/5 | `2026-09-03T11:33:21Z` |
| `mode_02_all_hit_count_bundle.json` | 806,032 | `9e6cf9440ddb77724378a5dc3af7182dbc76cc8b8f801be299a197ec96f95712` | `3420e8f467d2fb18e3a1db6512a882a60ffc83df41ff202a5cfc76bd443c25f9` | bundle | `2026-09-03T11:33:24Z` |
| `mode_02_all_hit_count_independent_check.json` | 3,917 | `16173ef87f0db27f3e326bbf612eb59d7f21bace48a22c72172d846cecfd4795` | `4cd4c21b89d668c206c45e98e6f4a92bc636e93680bf08ad9019b2dd628a0a91` | ACCEPT 5/5 | `2026-09-03T11:33:25Z` |
| `mode_03_weighted_hit_count_bundle.json` | 806,395 | `9190d49385a1be87c2a7c27c7c01bfc64b79db841e27f17f348704d4f29bebde` | `33da537ebb69235d876b82928c573947a2c621e5c36ad26616c46e7a43472095` | bundle | `2026-09-03T11:33:29Z` |
| `mode_03_weighted_hit_count_independent_check.json` | 3,917 | `e802c7de5d924956e8c5ae0489e12f244bc0e205e38822b86d0ab7b4b337ce7d` | `6402cad30d6968734cb35909cf5914e62cdc34bd180249785c6b0edd0ef6acd8` | ACCEPT 5/5 | `2026-09-03T11:33:29Z` |
| `mode_04_accept_every_hit_and_continue_bundle.json` | 779,946 | `275b474bb0f94c55e84cebcf9743daad6c4d80e19418099abbafa59bdcf97319` | `9aa0a5d6f85a82bda860b11b377e48f4c576cc87727e0462456f1625dda6e3f4` | bundle | `2026-09-03T11:33:33Z` |
| `mode_04_accept_every_hit_and_continue_independent_check.json` | 3,552 | `edfc176172f213110da7422aa6eefa39d3acc4350d89688c86214aed7519c854` | `d5932d027e41d1041a3606497940b61bfa703e59cd46899fea014615c8d2da31` | REJECT 4/5 | `2026-09-03T11:33:33Z` |

The fourth report's sole rejection is:

- property: `CP005_EXECUTABLE_IDENTITY_CHAIN`
- reason: `TC005_EXECUTABLE_PREIMAGE_PLAN_MISMATCH`
- path: `generated.executable_metadata.identity_preimage.plan_sha256`
- observed provider-internal physical plan:
  `b4fb955309faacd0097be86494a7573ccf97945c7f4e8e6e0ccf4bbc0a0599bf`
- frozen outer family plan:
  `5a8f15a3941f10560ffecc6021cd4689c068f5ed39903014b1d5e99e98b3d669`

The four bundles and four reports remain Attempt06 partial evidence. Their
hashes identify the failed attempt; they are not substituted into a successor
result.

## Observed Formal-Runner Sequence

1. Repository, frozen-core, preregistration, five prior incidents, five prior
   repair authorities, exact DSO binding, fresh native build, exported-symbol,
   and machine preflight checks passed.
2. Frozen modes 1--3 each returned the preregistered expected output, emitted a
   true-OptiX target bundle, and passed CP001--CP005.
3. Frozen mode 4 returned the preregistered six-query count output, emitted a
   complete true-OptiX built-in-sphere bundle, and passed CP001--CP004.
4. Its traversal receipt records exactly one attempted, complete-context, and
   successful OptiX launch; zero failed or incomplete launches; six raygen
   invocations; the expected program bundle; and a nonzero traversable.
5. CP005 rejected the bundle before runtime trust-root publication or any
   mutation application. The runner then stopped fail closed.

## Root-Cause Diagnosis

The provider has two legitimate canonical plan levels:

1. The frozen generic `CanonicalFamilyCompilationPlan` describes the family
   shape, protocol instance, callback/ABI/behavior identities, generic result
   operator, and provider-independent route requirements. Its SHA-256 is
   `5a8f15...3d669`.
2. `SphereAnyHitCountCanonicalPlan` describes the selected sphere provider's
   physical schema, callback/effect identity, concrete target profile,
   authority nonce, and physical template. Its SHA-256 is
   `b4fb95...59bf` and is correctly bound into the raw executable preimage.

The outer `FamilyExecutableIdentityV1` binds the outer family plan, provider
projection, concrete target, exact raw executable SHA-256, exact native DSO,
and composed PTX. The raw executable identity binds the inner physical plan.
The independent checker nevertheless compared the inner hash directly with
the outer hash, treating refinement as equality.

An RTDL-free reconstruction from the failed bundle proves that no product
change is needed. The behavior artifact and protocol authority agree on
physical-schema SHA-256
`b76c99505b1156a8eb7c23021c4fa9d86b64af84e365bcf9afbc85c8af109bb8`.
The outer plan supplies callback SHA-256 `72e1a9...f6ef08` and effect digest
`49c63a...3bf5c`; the executable identity and receipt agree on target SHA-256
`60a543...71fd9`. Canonically hashing these values with the fixed physical
authority kind reconstructs authority nonce `be462a...95d7`, which equals the
runtime physical receipt. Canonically hashing the resulting physical plan with
template `builtin_sphere_any_hit_count_u64_per_query_v1` and
`executable=false` reconstructs exactly `b4fb95...59bf`.

The missing work is therefore an independent two-level plan-refinement check:
verify every bridge input against already-bound bundle records, independently
rederive the physical authority nonce and plan hash, and compare that derived
hash with the raw executable preimage. Replacing this with direct equality or
trusting an emitted refinement receipt would weaken CP005 and is forbidden.

## Post-Failure Diagnostic Disclosure

After failure, pod commands only listed, statted, hashed, and parsed the eight
already-written JSON files; checked the absence of terminal result files;
hashed the preserved DSO/build manifest; checked Git custody; and downloaded
the mode-4 bundle/report for local read-only analysis. No route was rerun. No
additional OptiX launch, evidence capture, mutation application, or GPU
diagnostic process occurred.

## Counts At Failure Boundary

Formal Attempt06 alone:

- runner processes started: `1`
- frozen modes entered: `4`
- public route expected outputs returned: `4`
- published evidence bundles: `4`
- published independent property reports: `4`
- independently accepted per-mode reports: `3`
- independent property passes: `19`
- independent property rejects: `1`
- sphere OptiX launches: `1`
- published mutation applications: `0`
- accepted complete Goal5840 results: `0`

Cumulative through Attempts 01--06:

- formal runner processes started: `6`
- frozen modes entered: `13`
- public route expected outputs returned: `12`
- published evidence bundles: `10`
- published independent property reports: `10`
- independently accepted per-mode reports: `7`
- published mutation applications: `0`
- accepted complete Goal5840 results: `0`

The two post-Attempt-02 diagnostic launches remain separately classified and
unaccepted. Attempts 03--06 added zero post-failure GPU diagnostic launches.

## Permitted Repair Boundary

A successor authority may permit only:

- adding an RTDL-free independent derivation of the selected sphere physical
  schema authority, target-bound authority nonce, and inner physical-plan hash
  from existing bundle artifacts and outer family-plan commitments;
- replacing the incorrect inner-plan-equals-outer-plan assertion with exact
  derived-inner-plan equality;
- requiring exact behavior-artifact schema, callback, effect, physical schema,
  result operator, continuation, and output-count fields for this selected
  topology;
- requiring the behavior physical-schema hash to equal the one exact
  `physical_schema` protocol authority and the runtime authority nonce to equal
  the independently derived nonce;
- adding adversarial tests that mutate any bridge input or inner plan while
  recomputing attacker-controlled bundle-local hashes and still obtain
  rejection;
- appending this incident and a sixth repair authority; and
- extending capture and independent verification to bind all six incidents and
  repair authorities under a new formal Attempt07 schema.

It may not change any frozen route, fixture, expected output, declaration,
control-flow trust root, preregistered property or mutation; product provider,
runtime, compiler/codegen, native engine, or physical-schema semantics; or any
Goal5838 frozen-core byte. It may not remove CP005, equate the two plan levels,
or trust an unverified provider-emitted bridge assertion.

## Claim Boundary

- Independently accepted Attempt06 per-mode reports: `3`
- Accepted complete Goal5840 result: `false`
- Four-mode lowering/refinement preservation established: `false`
- General compiler soundness: `false`
- Application correctness: `false`
- Performance or speedup: `false`
- External review or consensus: `false`
