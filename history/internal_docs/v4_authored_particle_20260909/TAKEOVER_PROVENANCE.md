# Authored Particle Isolated Takeover Provenance

Date: 2026-09-09

Status: implementation candidate under hostile self-review; no performance or
paper claim is authorized by this record.

The Particle implementation candidate was copied from the dirty concurrent
manuscript worktree into the clean performance worktree as one exact binary Git
patch before further edits.

- Source worktree HEAD: `354f89bf4b0c7440034464115536f65950267919`.
- Destination starting commit: `ebe5c0f6e61e9334d0e08c5c064997a421b37f6a`.
- Takeover patch SHA-256:
  `6b15e792aa3f09e191bb855fe55dfdb867cd03cfec2c68808a34ecc1fcb55699`.
- Takeover patch size: 89 KiB as reported by the local filesystem.
- Imported closure: 14 tracked files, exactly the Particle-relevant public
  source/runtime/native/test diff enumerated by the patch.
- Deliberately excluded: `paper/`, `memory/`, `AGENTS.md`, generated PDFs,
  output archives, temporary files, and every untracked lead report.
- The source worktree was read only for this takeover and retains its original
  concurrent modifications.

The imported changes add an explicit, identity-bound provider-native closest
triangle policy, prepared device query columns, packed U32x3 output, and compact
device lifecycle control. Particle face/cell semantics remain in
`experiments/v4_authored_particle/program.py`; no Particle identifier or rule is
introduced into `src/rtdsl` or `src/native`.

After takeover, the performance worktree separately updates
`scripts/v4_authored_particle_worker.py` to compare the public authored RTDL
path against the prevalidated exact-core public-PyOptiX endpoint. That edit is
not represented by the takeover patch hash and is tracked normally by the
destination Git commit.
