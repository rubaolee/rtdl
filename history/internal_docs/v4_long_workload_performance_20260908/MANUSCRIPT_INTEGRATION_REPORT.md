# Long-workload manuscript integration and local preflight

Date: 2026-09-08, America/New_York. Status: local preflight PASS; independent
final-byte review and submission authorization remain open.

## Integrated evidence

The manuscript now preserves the initial adverse public-PyOptiX transaction and
adds the separately identified successor. The replacement application table
reports all ten complete/prepared rows, successor/PyOptiX arm times, eight-block
paired ratios and ranges, same-machine successor/old-RTDL ratios, and exact
outputs. Text identifies cit-Patents/4M as the only multi-second prepared
natural computation and retains the six-unmeasured-application denominator.

The abstract, contribution summary, application evaluation, artifact scope,
threats, and conclusion were updated together. The draft does not claim broad
performance, arbitrary callback lowering, app-independent native execution,
CPU/clock invariance, easier authoring, or peak-memory evidence.

## Exact local bytes

| Object | Bytes | SHA-256 |
| --- | ---: | --- |
| `paper/cgo2027/main.tex` | 60,625 | `0d29d05d04a0919d0c5b26c98861b17647fbc2256298990f6ab5b52a8de3f7a0` |
| `paper/cgo2027/main.pdf` | 183,937 | `3887bf1abb21068be057d13b012eddd7b9977e06ce53daf75b0eca84af4874c0` |

The source byte count must be rechecked after the commit if metadata-only
documentation changes unexpectedly touch `main.tex`; its SHA-256 is the binding
identity.

## Build and rendering

The exact build command from `paper/cgo2027/` was:

```text
/opt/homebrew/bin/tectonic -X compile main.tex \
  --outdir '/tmp/RTDL CGO long perf.NrVlo2' \
  --keep-logs --keep-intermediates
```

Results:

- exit 0;
- 12 pages, each US Letter 612 x 792 pt;
- zero overfull log entries in the final pass;
- zero unresolved citation/reference or missing-character entries;
- inherited BibTeX completeness warnings remain nonfatal and are not described
  as a warning-free bibliography;
- all 12 pages rendered at 110 DPI and reviewed as a contact sheet;
- pages 10--12 were separately reviewed at full rendered resolution;
- the new Table 8 is legible and contained within its rules;
- no clipping, overlap, blank page, missing glyph, or broken reference page was
  observed.

A tested source/PDF scan found no local user path, username, pod endpoint, SSH
identity, goal ID, agent name, GPU UUID, or private source commit. PDF metadata
contains the anonymous title/subject and tool producer only.

## Numeric cross-check

A literal projection check required all 16 key table time/ratio strings and
found none missing. The authoritative numbers remain the independently
recounted JSON, not the rounded manuscript projection. In particular:

- all ten paired medians are `<= 1.20`;
- all 80 paired block ratios are `<= 1.35`;
- largest median: com-dblp prepared `1.0995118679`;
- largest block: LibRTS range prepared `1.2433325861`;
- long graph prepared: RTDL `9347.908622` ms, PyOptiX `8802.240058` ms,
  paired median `1.0573612349`.

## Local test record

The valid narrow regression command was:

```text
env PYTHONPATH=src:. \
  /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest discover -s tests -p 'v4_long_workload*_test.py'
```

It ran 39 tests in 0.356 seconds and returned `OK`. Earlier in the same session,
one command named three nonexistent test modules, and two discovery invocations
omitted `PYTHONPATH=src:.`; those attempts produced collection/import errors.
They are operator-environment failures, are not counted as passing tests, and
do not alter the earlier 84/84 registered regression or the valid 39/39 rerun.

## Remaining gates

This is a new manuscript byte identity and inherits no acceptance vote from
P-septuple-prime. Before any submission or public wording, the exact committed
source/PDF/evidence bytes require claim review, independent final-byte review,
artifact-scope reconciliation, and authorized submission preflight. No upload,
external sending, or submission occurred here.
