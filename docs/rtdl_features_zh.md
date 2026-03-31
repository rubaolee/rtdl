# RTDL 当前功能说明（中文，本地草稿）

本文档用中文说明当前 RTDL 已支持的语言能力、运行方式和典型示例。  
这是一个本地说明文档，当前不作为正式对外发布材料。

## 1. RTDL 目前是什么

RTDL 是一个 Python-hosted DSL。用户仍然在 Python 里写程序，但描述的是“射线追踪查询”而不是直接写底层 Embree / OptiX 细节。

当前版本已经具备三层能力：

- 语言层：用户可以用 `@rt.kernel(...)`、`rt.input(...)`、`rt.traverse(...)`、`rt.refine(...)`、`rt.emit(...)` 写 RTDL 程序。
- 编译层：RTDL 可以把 Python DSL 编译成内部 IR，再 lower 成 RayJoin 风格的 backend plan，并生成 OptiX/CUDA skeleton。
- 运行层：RTDL 现在已经可以真的运行程序。
  - `rt.run_cpu(...)`：Python 参考执行器
  - `rt.run_embree(...)`：基于 Intel Embree 的本地原生后端

因此，当前 RTDL 不再只是“代码生成器”，而是已经有：

- 可写的 DSL
- 可检查的 IR / plan
- 可运行的 CPU backend
- 可运行的 Embree backend

## 2. 当前 DSL 支持哪些功能

当前已经支持 6 类 workload：

1. `lsi`
   线段与线段求交（segment-segment intersection）

2. `pip`
   点在多边形内测试（point-in-polygon）

3. `overlay`
   多边形 overlay 的组合种子生成

4. `ray_tri_hitcount`
   有限 2D ray 对随机三角形集合的 hit count

5. `segment_polygon_hitcount`
   每条线段与多少个多边形相交

6. `point_nearest_segment`
   每个点找到最近线段，并输出最近线段 id 和距离

当前支持的几何类型包括：

- `rt.Points`
- `rt.Segments`
- `rt.Polygons`
- `rt.Triangles`
- `rt.Rays`

当前支持的主要 predicate / refine 操作包括：

- `rt.segment_intersection(exact=False)`
- `rt.point_in_polygon(exact=False)`
- `rt.overlay_compose()`
- `rt.ray_triangle_hit_count(exact=False)`
- `rt.segment_polygon_hitcount(exact=False)`
- `rt.point_nearest_segment(exact=False)`

## 3. RTDL 程序的基本写法

一个 RTDL kernel 的基本结构如下：

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def some_query():
    left = rt.input("left", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right = rt.input("right", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])
```

这 5 个步骤的语义是：

1. `@rt.kernel(...)`
   声明这是一个 RTDL kernel。

2. `rt.input(...)`
   声明输入数据是什么几何类型、采用什么 layout、在查询中扮演什么角色。

3. `rt.traverse(...)`
   声明候选对如何生成。当前常见写法是通过 `bvh` 做遍历。

4. `rt.refine(...)`
   声明对候选对执行什么几何谓词或精化逻辑。

5. `rt.emit(...)`
   声明最终输出哪些字段。

## 4. 示例一：线段求交 `lsi`

下面是一个最典型的 RTDL 例子：

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def county_zip_join():
    left = rt.input("left", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right = rt.input("right", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )
```

### 4.1 代码解释

`@rt.kernel(backend="rayjoin", precision="float_approx")`

- `backend="rayjoin"` 表示当前 lower 的目标语义仍然以 RayJoin 风格为主。
- `precision="float_approx"` 表示现在走的是浮点近似路径，不是 exact arithmetic。

`left = rt.input(...)` 和 `right = rt.input(...)`

- 这里声明输入是两组线段。
- `role="probe"` 和 `role="build"` 表示一边用于 probe，一边用于 build acceleration structure。

`candidates = rt.traverse(left, right, accel="bvh")`

- 这一步并不是马上求交。
- 它先定义“候选对是通过 BVH 遍历得到的”。

`hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))`

- 在候选对上执行真正的 segment intersection 检查。

`rt.emit(...)`

- 输出左线段 id、右线段 id，以及交点坐标。

### 4.2 运行方式

这个 kernel 现在可以用两种方式跑：

```python
rows_cpu = rt.run_cpu(county_zip_join, left=left_segments, right=right_segments)
rows_embree = rt.run_embree(county_zip_join, left=left_segments, right=right_segments)
```

其中：

- `run_cpu(...)` 是 Python 参考语义
- `run_embree(...)` 是 Embree 原生后端

## 5. 示例二：点在多边形内 `pip`

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def point_in_counties():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False))
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

### 5.1 代码解释

- 输入是点集和多边形集。
- `traverse(...)` 先产生点-多边形候选对。
- `point_in_polygon(...)` 判断点是否在多边形内部。
- 输出为：
  - `point_id`
  - `polygon_id`
  - `contains`

如果 `contains=1`，表示点在多边形内；`0` 表示不在内。

## 6. 示例三：从中心发射射线，统计打中多少三角形

这是一个比 RayJoin 原始 workload 更接近“通用 RT 查询语言”的例子。

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def central_ray_triangle_stats():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

### 6.1 代码解释

`rays = rt.input("rays", rt.Rays, ...)`

- 输入是一组二维有限 ray。
- 每条 ray 通常有：
  - 起点
  - 方向
  - 最大长度 `tmax`
  - `id`

`triangles = rt.input("triangles", rt.Triangles, ...)`

- 输入是一组三角形。

`rt.ray_triangle_hit_count(exact=False)`

- 对每条 ray，统计命中了多少个 triangle。

`rt.emit(hits, fields=["ray_id", "hit_count"])`

- 每条 ray 输出一行结果：
  - `ray_id`
  - `hit_count`

### 6.2 一个更直观的理解

如果用户的问题是：

“在一个二维空间里放很多随机三角形，然后从中心点向随机方向发射有限长度的 ray，统计每条 ray 打中了多少个三角形”

当前 RTDL 已经可以表达并执行这个程序。

## 7. 示例四：新增的 Goal 10 workload

### 7.1 `segment_polygon_hitcount`

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def segment_polygon_hitcount_reference():
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])
```

这段程序的含义是：

- 输入一组线段和一组多边形
- 对每条线段，统计它与多少个多边形发生命中/相交
- 输出：
  - `segment_id`
  - `hit_count`

### 7.2 `point_nearest_segment`

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def point_nearest_segment_reference():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(points, segments, accel="bvh")
    nearest = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
    return rt.emit(nearest, fields=["point_id", "segment_id", "distance"])
```

这段程序的含义是：

- 输入一组点和一组线段
- 对每个点，找到最近的线段
- 输出：
  - `point_id`
  - `segment_id`
  - `distance`

这里 `distance` 是点到最近线段的距离。

## 8. 当前程序如何真正运行

当前 RTDL 有三条不同层次的路径：

### 8.1 编译路径

```python
compiled = rt.compile_kernel(kernel_fn)
plan = rt.lower_to_rayjoin(compiled)
generated = rt.generate_optix_project(plan, output_dir)
```

这条路径做的是：

- 把 DSL 编译成 IR
- 再 lower 成 RayJoin 风格 backend plan
- 生成 OptiX/CUDA skeleton 文件

这部分主要服务于未来 NVIDIA/OptiX 后端。

### 8.2 CPU 路径

```python
rows = rt.run_cpu(kernel_fn, **inputs)
```

这条路径做的是：

- 用 Python 参考语义直接执行当前 workload
- 适合做 correctness baseline

### 8.3 Embree 路径

```python
rows = rt.run_embree(kernel_fn, **inputs)
```

这条路径做的是：

- 用当前 DSL 表达 workload
- 通过 RTDL runtime 映射到 Embree 原生后端
- 返回真实运行结果

也就是说，当前版本已经不是“只能生成 skeleton，看不能跑”的状态；在 Mac 上已经可以通过 Embree 真跑。

## 9. 当前 DSL 的边界

当前版本已经能表达和运行一些非图形 RT workload，但仍然有明显边界：

- 目前 precision 还是 `float_approx`
- 还不支持 exact / robust 几何精度
- 当前 workload 还是固定枚举式扩展，不是完全开放式通用几何语言
- OptiX/NVIDIA backend 还没有真正跑通
- 生成的 OptiX/CUDA 代码仍主要用于 backend plan 和 skeleton 验证

因此，当前阶段更准确的说法是：

- RTDL 已经是一个“可写、可编译、可本地执行”的 DSL 原型
- Embree backend 已经可用
- NVIDIA RT core 后端是下一阶段目标

## 10. 推荐阅读顺序

如果一个开发者第一次接触当前 RTDL，建议按下面顺序阅读：

1. [README.md](/Users/rl2025/rtdl_python_only/README.md)
2. [apps/rtdsl_python_demo.py](/Users/rl2025/rtdl_python_only/apps/rtdsl_python_demo.py)
3. [docs/rtdl/programming_guide.md](/Users/rl2025/rtdl_python_only/docs/rtdl/programming_guide.md)
4. [examples/rtdl_goal10_reference.py](/Users/rl2025/rtdl_python_only/examples/rtdl_goal10_reference.py)
5. [src/rtdsl/api.py](/Users/rl2025/rtdl_python_only/src/rtdsl/api.py)
6. [src/rtdsl/runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/runtime.py)
7. [src/rtdsl/embree_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py)

## 11. 小结

截至当前版本，RTDL 已经支持：

- 6 类 workload
- Python DSL 编写
- IR / lower / codegen
- CPU 参考执行
- Embree 原生执行
- 基准测试、表格与图生成

所以，当前项目的最好理解方式是：

RTDL 已经从“研究想法”进入“可运行的语言原型”阶段。  
它还没有完成最终的 NVIDIA RT core 目标，但已经完成了一个可工作的 Embree baseline，并且 DSL 本身已经具备继续扩展 workload 的基础。
