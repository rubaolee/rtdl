# Robot Collision Lowering

Robot collision in this tutorial means sampled pose/link collision, not a full
motion-planning system. The RTDL idea is:

```text
poses + links + obstacles -> link segments -> candidate rows
  -> hit rows -> pose collision flags
```

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/robot_collision_lowering.py --mode both
```

## Relation Shape

The app lowers each pose to link segment rows. Candidate rows pair link segments
with obstacles. Hit rows record whether the link touches the obstacle. The
continuation reduces hit rows into one collision flag per pose.

This is the same model as ray/triangle any-hit, only grouped by pose.

Toy rows:

| pose_id | link_id | segment |
| ---: | ---: | --- |
| 1 | 0 | shoulder-to-elbow |
| 1 | 1 | elbow-to-hand |
| 2 | 0 | shoulder-to-elbow |
| 2 | 1 | elbow-to-hand |

Candidate and hit rows:

| pose_id | link_id | obstacle_id | hit |
| ---: | ---: | ---: | --- |
| 1 | 0 | 8 | `false` |
| 1 | 1 | 8 | `true` |
| 2 | 0 | 8 | `false` |
| 2 | 1 | 8 | `false` |

The continuation is grouped by `pose_id`:

| pose_id | collides |
| ---: | --- |
| 1 | `true` |
| 2 | `false` |

RTDL does not decide how poses are sampled or whether a robot is safe. It gives
the program a reusable way to produce and reduce collision rows.

## V4 Mapping

The V4 mapping uses `any_hit` with an explicit partner. The app still owns the
robot model, pose sampling, and collision contract.

Next: [RayDB Table To Ray](19_raydb_table_to_ray.md)
