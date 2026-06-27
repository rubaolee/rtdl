# Goal 29 Spec (Codex)

Date: 2026-04-02
Round: Goal 29 LSI Mismatch Diagnosis

Intent:
- investigate the larger-slice `lsi` mismatch discovered in Goal 28D
- do not guess about precision or backend behavior without evidence
- close only on a demonstrated diagnosis, and on a fix only if the fix is proven by regression

Initial plan:
1. inspect the Python `lsi_cpu` reference path and the native Embree `segment_intersection` path side by side
2. reproduce one mismatching larger slice and enumerate the pair differences
3. classify the mismatch pattern (endpoint-only, collinear, ring-closure duplication, bbox candidate omission, etc.)
4. implement the smallest correct fix if the root cause is clear
5. run regression locally and on the Linux host
