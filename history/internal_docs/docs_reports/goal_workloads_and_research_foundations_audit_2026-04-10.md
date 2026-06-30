# Workloads And Research Foundations Audit

Date: 2026-04-10

Scope:

- `/Users/rl2025/rtdl_python_only/docs/workloads_and_research_foundations.md`

What was checked:

- workload status wording against the current repo state
- paper metadata consistency
- redundant/repeated sections
- link style consistency
- obvious dead or stale content

Findings:

- The RTNN entry previously had a high-severity citation error:
  - wrong author list
  - wrong title wording
  - wrong venue
- The page also repeated the same RayJoin citation across multiple adjacent
  sections, which made it look copied rather than maintained.
- DOI/link style was inconsistent:
  - some entries used `doi.org`
  - some used direct `dl.acm.org` links

Changes made:

- corrected the RTNN citation to:
  - Yuhao Zhu
  - *RTNN: Accelerating Neighbor Search Using Hardware Ray Tracing*
  - PPoPP '22
  - DOI `10.1145/3503221.3508409`
- collapsed the duplicated RayJoin sections into one
  `RayJoin-centered spatial workloads` section
- standardized the RayJoin and LibRTS links to `doi.org`
- added a narrow scope note near the top so the page does not overclaim that it
  is a full project-history bibliography

Verification notes:

- The RTNN correction was checked against the local paper file:
  - `/Users/rl2025/Downloads/3503221.3508409.pdf`
- Shell-based HTTP checks against ACM/DOI URLs were blocked by Cloudflare-style
  anti-bot responses, so link verification here is limited to:
  - URL syntax correctness
  - DOI formatting correctness
  - consistency of link targets

Current judgment:

- the page is now materially cleaner and no longer contains the known RTNN
  citation error
- no obvious dead internal references remain in this page
- remaining residual risk is bibliographic, not structural:
  - some papers other than RTNN were not re-verified from local PDFs in this
    slice
