# Internal hostile self-review: Goal5836 A0 source acquisition

Date: 2026-09-01  
Review type: internal self-review, not external review  
Reviewed stage: A0 acquisition and hashing only  
Product/case-study source mutation: none  
Author/RTDL execution: none  
GPU/POD/timing: none

## 1. Verdict

```text
P0 = 0
P1 = 0
P2 = 3
P3 = 1

A0 VERDICT:
PASS__A0_COMPLETE__OWNER_MAY_AUTHORIZE_A1_CLASSIFICATION_ONLY
```

The exact planned Git commit exists, its complete tree identity reconstructs,
the planned MIT license matches exact bytes, and one exact official arXiv v2
paper PDF is preserved. A0 is complete at its declared provenance scope.

This verdict does not authorize A1. It does not start Goal5836 execution or
permit input selection, author build/run, RTDL execution, product mutation,
POD/GPU use, performance, Paper-App promotion, external review, or public
claims.

## 2. Acceptance checks

### 2.1 Owner and predecessor binding

Pass. The owner instruction was received after preaction commit
`92923035...d0ad` and is recorded as A0-only authorization. The exact
preaction bytes rehash to `7e021a...c7f40`. Later stages remain false in the
authority and a coordinated re-seal cannot enable A1.

### 2.2 Paper identity

Pass at explicit arXiv-v2 scope. The preserved 34,726,851-byte PDF hashes to
`9a0003...c9c0`, is a complete ten-page unencrypted PDF, and is bound to the
versioned official arXiv page carrying the exact title, authors, v2 identity,
and related ICRA DOI. It is not called the IEEE publisher PDF.

### 2.3 Git commit and complete tree

Pass. Exact fetch returned `bacbf77...0ac7`; the raw commit object recomputes
that OID and names root tree `3e5e1c...e496f`. All 269 blobs recompute their
Git OIDs, carry separate SHA-256 values, total 132,303,954 bytes, and rederive
the same root tree from paths/modes/OIDs. There are no submodules.

### 2.4 License

Pass. The exact 1,066-byte license is canonical MIT text naming Sizhe Sui,
with Git blob OID `0ec3c9...a5` and SHA-256 `12978f...2862`.

### 2.5 Portable source custody

Pass with disclosed limitation. The complete tree identity is portable and
path-independent. A deterministic 203-file source/build/document capsule is
preserved and exactly verified. Omitted binary assets are not silently
treated as present; they require reacquisition of the same commit and full
inventory match.

### 2.6 Stage and claim boundary

Pass. Author-source semantic inspection and source-fidelity classification are
false. Build, execution, workers, timing, performance, Paper App, complete
RT-CCD, and public claims are all zero/false. Goal5835 remains
`NOT_A_PAPER_APP` and
`SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES`.

## 3. Findings

### P2-1: IEEE publisher PDF is not acquired

The versioned official arXiv v2 PDF is exact and linked to the ICRA DOI, but it
is not the IEEE-hosted publisher byte stream. The IEEE page presented an
anti-automation gate in this environment. A0 must therefore claim exact arXiv
v2 provenance only. A1 may compare paper/source semantics using these exact
bytes. Any later assertion about publisher-byte identity requires a separate
publisher acquisition or a justified statement that such identity is not
needed.

This does not block A1 because the research mapping names the author paper and
source, and an exact author-submitted revision is present. It does block the
stronger sentence “the IEEE publisher PDF bytes were acquired.”

### P2-2: Full author-tree bytes are not vendored

The repository tree is 132 MB, mostly because of large images, GIFs, meshes,
and data. Duplicating it in RTDL Git would create substantial unrelated
payload. A0 instead preserves a complete independently rederived tree identity
plus every blob's OID/size/SHA-256 and a 203-file source capsule.

This is sufficient for A1 code-fidelity inspection. It creates a future
availability dependency for omitted assets: if A2 needs one and the author
repository can no longer provide the exact commit, A2 must stop rather than
substitute a file. The authority states this directly.

### P2-3: Metadata discovery exposed paper method text before A1

The web tool used to confirm the official arXiv version returned substantial
paper text, not only metadata. This exposure is irreversible and must not be
misreported as “no semantic text seen.” However, no author source file was
opened for semantics, no source-fidelity classification was made, no common
input was selected, and no author/RTDL output exists.

A1 remains scientifically usable only if every conclusion is tied to exact
preserved author-source lines and paper bytes, with predetermined classification
branches. It may not cite the model's prior memory as evidence. The authority
and tests now disclose and enforce this distinction.

### P3-1: Two local tool/test failures occurred before final freeze

The first acquisition build failed before creating output because the local
tree encoder did not distinguish directory dictionaries from blob-row
dictionaries. The repair introduced an explicit blob marker, after which the
rederived root matched Git. A later hostile test expected an obsolete error
label after authorization validation had been strengthened; the attack was
already rejected, and only the expected label was corrected.

Both events occurred before the final authority. Every output was rebuilt
create-only after source/test changes. They are evidence of fail-closed tooling,
not source drift or hidden result replacement.

## 4. Hostile counterfactuals

| Attack or failure | Result |
|---|---|
| Planned commit unavailable | Terminal A0 failure; no pin replacement |
| First fetch connection reset | Recorded infrastructure failure; exact retry only |
| Commit or root tree differs | Acquisition rejected |
| Blob/path/mode inventory changes | Root-tree or authority verification fails |
| Selected capsule gains/removes a file | Selection/path-set verification fails |
| PDF byte or version changes | Fixed length/SHA/version checks fail |
| License differs from planned MIT bytes | Blob/text checks fail |
| Re-sealed authority enables A1 | Exact authorization document rejects it |
| Paper text exposure is hidden | Hostile test rejects the authority |
| Worker or timing becomes nonzero | Policy validation rejects it |
| Omitted asset cannot be reacquired | Later stage stops; no substitute |

## 5. Strongest current claim

> RTDL has acquired and independently byte-bound the official arXiv v2 paper,
> the exact planned author Git commit, its complete 269-file tree identity, and
> the exact MIT license. A compact mechanically selected author-source capsule
> is preserved for later fidelity inspection. No author-source fidelity result,
> same-input fixture, author/RTDL execution, Paper-App result, complete RT-CCD
> result, modern-RTX result, or performance result exists yet.

## 6. Next decision

The only scientifically valid next owner decision is:

```text
AUTHORIZE_STAGE_A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION_ONLY
```

No POD is needed for A1. This review does not provide that authorization.
