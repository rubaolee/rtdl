# Goal 132 Report: Gemini v0.2 Doc Draft Review

Date: 2026-04-06
Status: accepted

## Summary

Gemini produced a usable structural draft for a v0.2 user-facing document. The
sectioning was worth keeping:

- What Is New
- Workloads
- Generate-Only
- Platforms
- Backend Notes
- Quick Start
- Current Limits

But the raw draft was not acceptable without review.

## Main corrections applied

### Platform honesty

The final guide now states clearly:

- Linux is the primary v0.2 development and validation platform
- this Mac is only a limited local platform for Python reference, C/oracle, and
  Embree

### Backend honesty

The raw draft was too loose about OptiX and Vulkan.

The final guide now avoids overclaiming:

- OptiX current wins are described as the result of the accepted algorithmic
  candidate-index strategy, not as proof of universal RT-core-native maturity
- Vulkan is described as a correctness/portability backend that must work and
  must not be very slow, not as a fully optimized flagship path

### Scope discipline

The final guide is explicitly limited to the current real v0.2 surface:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- narrow generate-only support for both

It does not present deferred or still-immature ideas as current product
features.

## Result

The Gemini draft was useful as a first-pass structure and wording seed, but the
final accepted guide required Codex review and correction before publication.
