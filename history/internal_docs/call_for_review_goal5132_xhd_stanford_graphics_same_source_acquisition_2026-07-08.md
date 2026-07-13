# Call For Review - Goal5132 X-HD Stanford Graphics Same-Source Acquisition

Please strictly review Goal5132.

## Files To Review

```text
history/internal_docs/goal5132_xhd_stanford_graphics_same_source_acquisition_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_stanford_graphics_acquisition_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/external/README.md
Paper-reproduction-apps/x-hd-paper/data/external/stanford/README.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Review Questions

1. Does the acquisition evidence correctly identify public Stanford Dragon and
   HappyBuddha source archives and record URL, byte size, and SHA256?
2. Do the PLY header counts support a Level B same-source graphics selection
   without being misrepresented as Level C exact paper dataset evidence?
3. Does the report correctly state that count/scale matching is useful but not
   sufficient for exact paper reproduction?
4. Does the report avoid claiming author `hd_exec` or RTDL route success on
   these PLY files?
5. Does the report correctly identify the current input bridge gap: existing
   gate scripts are WKT-only while the acquired data is PLY?
6. Does the report correctly identify that the current RTDL exact pairwise route
   is not scalable to full-resolution Dragon x HappyBuddha?
7. Is the next proposed step appropriate: app-owned PLY loader + parameterized
   author gate + bounded reduced-resolution/sampled Level B gate?
8. Does the acquisition keep RTDL core clean and avoid adding a Hausdorff/X-HD
   primitive or app-specific system API?
9. Should Goal5132 be closed as source acquisition only, with correctness and
   performance gates still open?

## Expected Answer Shape

```text
Verdict: approve | approve_with_required_amendments | block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to 9 review questions:
1. ...
...
9. ...
```

## Requested Verdict Label

If acceptable:

```text
approve_goal5132_xhd_stanford_graphics_same_source_acquisition__gate_not_yet_run
```
