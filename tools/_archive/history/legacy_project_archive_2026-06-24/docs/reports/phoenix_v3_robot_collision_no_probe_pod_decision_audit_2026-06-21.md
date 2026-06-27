# Phoenix V3 Robot Collision No-Probe Pod Decision Audit - 2026-06-21

Decision: run the new robot-collision `collision_flag_stream` no-probe paired
evidence script on the RTX pod.

Reason: the current M7 blocker is not the hot flag-stream result; it is that the
current wall timing includes a CPU probe-reference oracle that dominates the
measurement. The app already supports `--no-probe-reference`, so the honest next
step is a paired evidence packet with validation and performance timing
separated, not a core rewrite or a public claim.

1. Was I foolish?

   No for this decision. The script is dry-run tested locally, keeps all public
   claim flags false, and preserves the same prepared grouped segment any-hit
   contract.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be to publish the existing 5.166x hot
   tail number as end-to-end speedup, or to run pod commands without a reusable
   evidence script and claim boundary.

3. Was there another path that would have avoided getting stuck on that idea?

   Yes. The other path is to close `collision_flag_stream` as no-go immediately.
   That is safer but leaves an existing generic no-probe mode untested under the
   exact M7 blocker.

4. Can I now try a different path that actually solves the problem?

   Yes. Run the paired evidence script on RTX, copy back the artifacts, and only
   then decide whether to request Claude review for M7 promotion or write a
   no-go closure.
