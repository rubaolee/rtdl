# Graph Triangle Counting Lowering

Triangle counting looks like a graph problem, but the RTDL lesson is about
turning graph structure into witness rows.

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/triangle_counting_graph_lowering.py --mode both
```

## Relation Shape

The tutorial program builds these rows:

1. directed edge rows,
2. two-hop rows such as `src -> mid -> dst`,
3. ray rows derived from the graph geometry,
4. primitive rows for possible closing edges,
5. witness rows for closed triangles,
6. grouped count rows.

The important point is the separation: graph logic creates candidate rows, RTDL
tests the closing-edge witness shape, and a continuation groups counts.

Small graph:

```text
1 -> 2
1 -> 3
2 -> 3
2 -> 4
3 -> 4
```

The two-hop rows include:

| src | mid | dst | question |
| ---: | ---: | ---: | --- |
| 1 | 2 | 3 | does edge 1 -> 3 exist? |
| 1 | 2 | 4 | does edge 1 -> 4 exist? |
| 1 | 3 | 4 | does edge 1 -> 4 exist? |
| 2 | 3 | 4 | does edge 2 -> 4 exist? |

The witness rows are the closed triangles:

| src | mid | dst | triangle |
| ---: | ---: | ---: | --- |
| 1 | 2 | 3 | `(1, 2, 3)` |
| 2 | 3 | 4 | `(2, 3, 4)` |

Grouped counts then become:

| source_vertex | triangle_count |
| ---: | ---: |
| 1 | 1 |
| 2 | 1 |
| 3 | 0 |
| 4 | 0 |

## V4 Mapping

The V4 part names the generic surfaces:

- `any_hit` for witness tests,
- `primitive_grouped_i64` for grouped integer count/sum output.

The engine is not a special triangle-counting app. It is reusing hit rows and
grouped reduction.

Next: [Robot Collision Lowering](18_robot_collision_lowering.md)
