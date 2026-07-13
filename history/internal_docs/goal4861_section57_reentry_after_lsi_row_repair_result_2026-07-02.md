# Goal4861 Result: Section 5.7 Re-Entry After LSI Row Repair

Date: 2026-07-02

## Purpose

Goal4861 re-entered RayJoin Section 5.7 County x Zipcode after Goal4860 fixed
public planar-map LSI row materialization.

The question was whether the exposed Section 5.7 failure could be sent back to
the single-stage tests:

- Section 5.2 LSI;
- Section 5.3 PIP / point-location;
- or whether the remaining defect belongs to the Section 5.7 overlay assembly
  layer.

## Short Answer

The original row-count failure was correctly sent back to **Section 5.2 LSI row
materialization**, and Goal4860 repaired that gate.

After that repair, the current Section 5.7 failure is **not** an LSI or PIP
single-stage failure.  The first remaining mismatch is in **output-chain face-id
assignment / overlay assembly**.

## Re-Entry Gate: Public Generic Route

Evidence file:

- `history/internal_docs/goal4861_section57_public_route_reentry_gate_summary.json`

Route label:

- `generic_public_primitives_plus_app_layer`

### LSI Gate

The LSI gate passed:

| pair | expected | count | rows | pass |
| --- | ---: | ---: | ---: | --- |
| County x Zipcode | 961165 | 961165 | 961165 | true |
| Australia Lakes x Parks representative | 13622 | 13622 | 13622 | true |

Public row keys:

- `left_id`
- `right_id`
- `intersection_point_x`
- `intersection_point_y`

The row surface still does not expose scaled/rational intersection-coordinate
fields.

### PIP Gate

The County x Zipcode PIP consistency gate passed:

| field | value |
| --- | ---: |
| author query points | 47862092 |
| RTDL total points | 47862092 |
| author positive count | 47327744 |
| RTDL segment-found count | 47327744 |
| author closest-eids FNV64 | 17585803063680255704 |
| RTDL normalized segment hash FNV64 | 17585803063680255704 |

This means the current failure should not be blamed on the already-tested PIP
stage unless a later localized diagnostic proves a new PIP-specific defect.

### Public Route Status

Public exports:

| public symbol | available |
| --- | --- |
| `prepare_planar_map_lsi_2d_optix` | true |
| `prepare_planar_map_point_location_2d_optix` | true |
| `assemble_output_chains` | false |
| `write_output_chains` | false |

The preferred public route is therefore blocked after public LSI and PIP:

- `preferred_route_status`: `blocked_after_public_lsi_and_pip`
- `exit_label`: `blocked_by_output_chain_app_logic_gap`

Reason:

Public LSI rows and County x Zipcode PIP consistency are available, but the
public user surface does not expose an output-chain assembler and the public
LSI row surface does not expose scaled/rational intersection coordinates needed
for an author-compatible byte-equality output-chain implementation.

## Fallback Route: Bounded Bundled Helper Compare

Because the preferred public route is blocked, Goal4861 ran the explicitly
labeled fallback route:

- `bounded_bundled_helper_reproduction`

This route is allowed only as a shipped-helper diagnostic.  It must not be
presented as a generic public-language Section 5.7 reproduction.

### AuthorPatch Baseline

Dataset:

- base: `/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb`
- query: `/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb`

Author output:

- `/workspace/goal4861_author_intended_baseline/author_intended_county_zipcode_overlay.txt`

Author output facts:

| field | value |
| --- | --- |
| bytes | 2390763754 |
| sha256 | `02fcae3f53a8486134412564c438a19d7d999d1948742e7f115a5d13f94836ef` |

### Streaming Compare Result

Evidence file:

- `history/internal_docs/goal4861_bundled_helper_streaming_compare_summary.json`

Result:

```json
{
  "elapsed_sec": 481.4263310432434,
  "first_diff": {
    "author": "41230 2 42104 42105 280 290",
    "line": 123678,
    "rtdl": "41230 2 42104 42105 294 295"
  },
  "result": null,
  "stream_match": false
}
```

Author context around the first difference:

```text
41228 2 42102 42103 280 290
-86.685242 34.079858
-86.684974 34.080090
41229 2 42103 42104 280 290
-86.684974 34.080090
-86.684939 34.080122
41230 2 42104 42105 280 290
-86.684939 34.080122
-86.684939 34.080122
41231 2 42105 42106 280 290
-86.684939 34.080122
```

The first mismatch has:

- same chain id: `41230`;
- same point ids: `42104 42105`;
- same chain length: `2`;
- different face ids:
  - AuthorPatch: `280 290`;
  - RTDL fallback helper: `294 295`.

This classifies the remaining bug as output-chain face assignment / overlay
assembly, not as missing LSI rows and not as a first-order PIP count/hash
failure.

## Claim Boundary

Authorized:

- Section 5.2 LSI row-materialization repair was successfully re-used as a
  Section 5.7 precondition.
- Section 5.3 County x Zipcode PIP consistency remains clean at the count and
  normalized segment-hash level.
- The preferred generic route is honestly blocked at the output-chain app layer.
- The fallback bundled-helper route was tested and failed byte equality at a
  localized face-id assignment mismatch.

Not authorized:

- Section 5.7 byte-equal correctness;
- Section 5.7 topology-equivalent correctness;
- Section 5.7 performance;
- broad RayJoin paper reproduction;
- presenting the bundled-helper route as a generic RTDL public-language app.

## Recommended Next Goal

The next goal should be a localized diagnostic, not another blind full overlay
run.

Recommended next goal:

- **Goal4862: chain 41230 output-chain face-id assignment diagnostic**

Purpose:

- determine whether the face-id mismatch comes from midpoint point-location,
  face-id numbering/order, output-chain polygon-id propagation, or scaled
  coordinate/rational midpoint handling.

Required discipline:

- use chain 41230 and surrounding local data first;
- use synthetic or sliced cases where possible;
- do not run performance;
- do not edit public docs/tutorials;
- do not relabel fallback helper results as generic language evidence.
