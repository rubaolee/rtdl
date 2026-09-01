# Goal5836 A0 exact source acquisition technical report

Date: 2026-09-01  
Stage: `A0_EXACT_SOURCE_ACQUISITION_AND_HASHING`  
Scope: provenance and byte custody only  
Author build/execution: 0  
RTDL Goal5836 execution: 0  
GPU/POD workers: 0  
Timings/performance results: 0  
External review: not requested or authorized

## 1. Authorization and result

The predecessor preaction is
`goal5836_sui_same_input_preaction_authority_20260901.json` at SHA-256
`7e021a874a13454488bf056c44402225bc1deadfc990cf2a8aeb48eaed9c7f40`.
The owner's continuation instruction is preserved in
`goal5836_a0_owner_authorization_20260901.md` and is interpreted fail-closed as:

```text
AUTHORIZE_STAGE_A0_SOURCE_ACQUISITION_AND_HASHING_ONLY
```

A0 completed with machine status:

```text
PASS__EXACT_SOURCE_BYTES_ACQUIRED_AND_HASHED__A1_LOCKED
```

The controlling authority is
`goal5836_a0_source_acquisition_20260901/SOURCE_ACQUISITION_AUTHORITY.json`:

```text
whole-file SHA-256:
5d18d5736be47288e6867d29df93a05bc2f7a81462101e563d65f88c5d236bef

internal authority seal:
e266b5376f075c0da96ae93fa5c44e20245a3583e6f122a56e1032035c1c7050
```

The A0 authorization is consumed. No later stage is authorized.

## 2. Exact paper identity

The acquired paper is the official, versioned author-submitted arXiv revision:

```text
identity: arXiv:2409.09918v2
URL: https://arxiv.org/pdf/2409.09918v2
title: Hardware-Accelerated Ray Tracing for Discrete and Continuous
       Collision Detection on GPUs
authors: Sizhe Sui; Luis Sentis; Andrew Bylard
related ICRA DOI: 10.1109/ICRA55743.2025.11128528
bytes: 34,726,851
pages: 10
SHA-256: 9a0003bda2ce176415389c99af0e91aea0fc1564a3bfb7388b8054760993c9c0
```

The PDF, versioned abstract HTML, exact HTTP response headers, and `pdfinfo`
receipt are preserved. The verifier checks PDF framing, length, SHA-256,
version/title/authors/DOI markers, HTTP 200/content length, page count, lack of
encryption, and lack of embedded JavaScript.

This is not represented as the IEEE publisher PDF. The IEEE document page was
not machine-accessible through the current anti-automation gate. The authority
therefore uses the exact class
`OFFICIAL_ARXIV_V2_AUTHOR_SUBMITTED_REVISION__NOT_IEEE_PUBLISHER_PDF`.

## 3. Exact author Git identity

The planned repository and commit were not changed:

```text
repository: https://github.com/Ssz990220/RTCollisionDetection.git
planned commit: bacbf77a612bba3e6e8f7a464fa0fa2c67298ac7
observed commit: bacbf77a612bba3e6e8f7a464fa0fa2c67298ac7
root tree: 3e5e1c3a2a128148eae61bc94a22eaae491e496f
commit date: 2025-04-17
commit subject: organizing readme
```

The first exact fetch ended in a connection-reset/early-EOF infrastructure
failure. No nonexistence inference or pin change was made. One retry of the
same commit through Git HTTP/1.1 succeeded. `git fsck --full --strict` found no
object error; the commit is dangling only because the minimal acquisition repo
retains it through `FETCH_HEAD` rather than a branch.

The acquisition tool read all 269 commit-tree blobs, recomputed every Git blob
OID from exact bytes, recorded every path/mode/OID/size/SHA-256, and rebuilt the
recursive Git tree encoding from the inventory. The rebuilt root equals
`3e5e1c3a...e496f`.

```text
complete file count: 269
complete blob bytes: 132,303,954
submodule count: 0
```

The complete 132 MB tree is not duplicated inside RTDL Git. Its full identity
is preserved in `AUTHOR_SOURCE_TREE_INVENTORY.json`; later access to omitted
large assets must refetch exactly the frozen commit and match this inventory.

## 4. Preserved source subset

To make A1 possible without another network transaction, A0 mechanically
selected source/build/document text by a frozen basename-or-suffix rule. No
function names, algorithms, outputs, or convenient result were used for this
selection.

```text
selected files: 203
selected source bytes: 1,441,191
deterministic gzip capsule bytes: 371,994
capsule SHA-256:
a09883fac899cffa3ac4273b207db75818c2155ab516653462806d1d439f1466
```

The selected capsule includes C/C++/CUDA headers and sources, CMake/build
files, shell/Python utilities, Markdown/text/configuration, and URDF files.
Images, GIFs, OBJ meshes, binary trajectory data, and notebooks are excluded
from the compact capsule but remain identity-bound by the complete inventory.

The verifier rejects path traversal, duplicate or unexpected members, member
size/hash drift, selection-rule drift, and root-tree mismatch.

## 5. License

The exact `LICENSE` blob is preserved:

```text
label: MIT
Git blob OID: 0ec3c9a8cb0bb8fe2de6ad03ca465ccd12e1c4a5
bytes: 1,066
SHA-256: 12978fa5561b51ce1cb0a785e7fda31ad67c5458928f61bbdaed0053db812862
copyright: Copyright (c) 2025 Sizhe Sui
```

The planned MIT label therefore matches the acquired license bytes.

## 6. Boundary disclosures

The registered acquisition count is four byte-acquisition actions: one failed
exact Git fetch, one successful exact retry, one arXiv v2 PDF fetch, and one
arXiv v2 abstract-page fetch. Earlier search/open operations used to identify
the official version are disclosed separately and are not falsely included in
that count.

The metadata discovery tool incidentally returned paper methodology text while
the arXiv version was being confirmed. This is explicitly recorded. No author
source file was semantically inspected, no paper-to-source fidelity
classification was made, no common input was selected, and no output was
observed. A1 must cite exact preserved source bytes rather than relying on
memory of discovery output.

The first local acquisition build also failed before output because its tree
rebuilder represented directory and blob nodes with the same Python type. The
tool was repaired to use an explicit blob marker and the output was created
from scratch. A later hostile-test label mismatch was likewise corrected and
the exact authority rebuilt; no generated authority was edited in place.

## 7. Verification

```text
python3 scripts/goal5836_a0_build_source_acquisition.py --verify-stored
python3 -m unittest tests.goal5836_a0_source_acquisition_test -v
```

The stored verifier passes and all 15 A0 hostile tests pass. They cover exact
authority reconstruction, later-stage authorization attacks, hidden paper-text
exposure, author semantic-inspection claims, nonzero workers/timings, root-tree
mutation, selected-capsule custody, commit/license identity, and the unchanged
Goal5835 claim ceiling.

## 8. Next gate

No POD is needed. The only next requested owner decision is:

```text
AUTHORIZE_STAGE_A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION_ONLY
```

Even if A1 is authorized, input selection, route materialization, author build
or execution, product mutation, POD/GPU use, timing, Paper-App promotion,
external review, and public claims remain locked.
