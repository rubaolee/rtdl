# Goal4856 - Section 5.3 PIP Result Consistency Check

Date: 2026-07-01

## Purpose

Goal4855 reproduced the RayJoin paper Section 5.3 PIP workload shape on three datasets, but its first report compared the wrong RTDL metric against the author program.  The RTDL `face_positive_count` means "non-exterior face id", while the author PIP route exposes `closest_eids != DONTKNOW`.  Goal4856 corrects that mistake by comparing the same result object:

- AuthorPatch metric: `closest_eids[i] != DONTKNOW`, plus an FNV64 hash over the full `closest_eids` array.
- RTDL metric: raw point-location `segment_id[i] != DONTKNOW`, plus an FNV64 hash over `segment_id - 1` for found hits.  RTDL segment ids are 1-based in this route; author `closest_eids` are 0-based.

This is a correctness/consistency goal, not a performance-win goal.

## Boundary

- No broad RayJoin claim.
- No Section 5.7 overlay claim.
- No all-eight workload claim.
- No Embree claim.
- No RTDL runtime/native change was required for this result-consistency check.
- AuthorPatch was changed only to emit a diagnostic line after the measured `Query` timer; the diagnostic does not change the author algorithm.

## Artifacts

- Local artifact directory: `history/internal_docs/goal4856_section53_pip_consistency/`
- RTDL diagnostic script: `history/internal_docs/goal4856_rtdl_section53_pip_raw_diagnostic.py`
- Author diagnostic source snapshot: `history/internal_docs/tmp_goal4856_author_run_query.cu`

## Diagnostic Method

The author `query_exec -query=pip` path records closest segment ids internally but normally prints only timing.  I added a bounded diagnostic after the query loop:

```text
AUTHORPATCH_PIP_DIAG query_points=<N> positive_count=<closest_eids != DONTKNOW> closest_eids_fnv64=<hash> dontknow_value=4294967295
```

The RTDL diagnostic calls the public directed point-location raw route and streams query points in chunks, producing:

- `segment_found_count`
- `segment_hash_raw_fnv64`
- `segment_hash_minus1_fnv64`
- `face_positive_count`

Only `segment_found_count` and `segment_hash_minus1_fnv64` are comparable to AuthorPatch Section 5.3 PIP.

## Results

| Dataset | Query points | Author `positive_count` | RTDL `segment_found_count` | Count match | Author `closest_eids` hash | RTDL normalized segment hash | Hash match | Interpretation |
|---|---:|---:|---:|---|---:|---:|---|---|
| County x Zipcode | 47,862,092 | 47,327,744 | 47,327,744 | yes | 17,585,803,063,680,255,704 | 17,585,803,063,680,255,704 | yes | Exact per-point closest-edge consistency. |
| Block x Water | 44,863,618 | 44,841,020 | 44,841,020 | yes | 13,878,963,590,670,293,968 | 13,878,963,590,670,293,968 | yes | Exact per-point closest-edge consistency. |
| Australia Lakes x Parks representative | 992,505 | 958,981 | 958,981 | yes | 1,436,797,974,851,078,734 | 11,266,624,325,209,482,800 | no | Count-consistent only; per-point edge-id hash differs on this same-source representative. |

## Timing Context

The RTDL raw diagnostic is intentionally slower than the Goal4855 count-only hot path because it downloads raw per-point result rows and hashes every returned segment id.  These timings are diagnostic costs, not the user-facing Section 5.3 performance number.

| Dataset | RTDL scan sec | RTDL pack-base sec | RTDL raw query/download sec |
|---|---:|---:|---:|
| County x Zipcode | 169.0468 | 53.0509 | 245.5018 |
| Block x Water | 264.0372 | 176.1000 | 234.7401 |
| Australia Lakes x Parks representative | 22.5913 | 42.3684 | 7.8640 |

AuthorPatch diagnostic output was recorded after the measured query timer.  The diagnostic line adds host-side copy/hash work and should not be mixed into the author `Query` timer.

## Conclusion

Goal4856 corrects the metric mistake from Goal4855.

For the two serious recovered Section 5.3 US workloads, County x Zipcode and Block x Water, RTDL agrees with AuthorPatch not only in count but in the full per-point closest-edge hash after the documented 1-based to 0-based segment-id normalization.

For the Australia representative dataset, RTDL agrees with AuthorPatch on the found/not-found count, but not on the full closest-edge hash.  This row must remain bounded as count-consistent representative evidence, not exact per-point author-equivalent evidence.

Recommended exit label:

`completed_section53_pip_two_serious_exact_one_representative_count_only`
