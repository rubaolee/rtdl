const pptxgen = require("pptxgenjs");
const {
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require("./pptxgenjs_helpers/layout");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "OpenAI Codex";
pptx.company = "OpenAI";
pptx.subject = "RTDL status summary";
pptx.title = "RTDL Status Summary";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};

const COLORS = {
  ink: "132033",
  slate: "2F4F60",
  teal: "1B7F8C",
  mint: "CFE8E3",
  sand: "F4EBD8",
  gold: "E1A948",
  coral: "D96C4A",
  pale: "FAF8F3",
  white: "FFFFFF",
  gray: "61707D",
};

function addBackground(slide, accent = COLORS.teal) {
  slide.background = { color: COLORS.pale };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.4,
    line: { color: accent, transparency: 100 },
    fill: { color: accent },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 7.1,
    w: 13.333,
    h: 0.4,
    line: { color: COLORS.ink, transparency: 100 },
    fill: { color: COLORS.ink },
  });
}

function addTitle(slide, title, subtitle) {
  slide.addText(title, {
    x: 0.7,
    y: 0.55,
    w: 8.6,
    h: 0.55,
    fontFace: "Aptos Display",
    fontSize: 24,
    bold: true,
    color: COLORS.ink,
    margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.72,
      y: 1.12,
      w: 8.8,
      h: 0.34,
      fontFace: "Aptos",
      fontSize: 10.5,
      color: COLORS.gray,
      margin: 0,
    });
  }
}

function addBullets(slide, items, opts = {}) {
  const x = opts.x ?? 0.9;
  const y = opts.y ?? 1.7;
  const w = opts.w ?? 5.5;
  const h = opts.h ?? 4.8;
  const fontSize = opts.fontSize ?? 17;
  const color = opts.color ?? COLORS.ink;
  const runs = items.map((text) => ({
    text,
    options: { bullet: { indent: 14 } },
  }));
  slide.addText(runs, {
    x,
    y,
    w,
    h,
    fontFace: "Aptos",
    fontSize,
    color,
    valign: "top",
    breakLine: true,
    margin: 0.05,
    paraSpaceAfterPt: 14,
  });
}

function addPanel(slide, x, y, w, h, title, body, fill, titleColor = COLORS.ink) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    line: { color: fill, transparency: 100 },
    fill: { color: fill },
  });
  slide.addText(title, {
    x: x + 0.18,
    y: y + 0.15,
    w: w - 0.36,
    h: 0.28,
    fontFace: "Aptos Display",
    fontSize: 16,
    bold: true,
    color: titleColor,
    margin: 0,
  });
  slide.addText(body, {
    x: x + 0.18,
    y: y + 0.5,
    w: w - 0.36,
    h: h - 0.65,
    fontFace: "Aptos",
    fontSize: 11.5,
    color: COLORS.ink,
    margin: 0,
    valign: "top",
  });
}

function addCodeBox(slide, text, x, y, w, h) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.05,
    line: { color: COLORS.slate, pt: 1.2 },
    fill: { color: "F6F8FB" },
  });
  slide.addText(text, {
    x: x + 0.15,
    y: y + 0.12,
    w: w - 0.3,
    h: h - 0.24,
    fontFace: "Courier New",
    fontSize: 10.5,
    color: COLORS.ink,
    margin: 0,
    breakLine: false,
    valign: "top",
  });
}

function addFooter(slide, page) {
  slide.addText(`RTDL status · slide ${page}/10`, {
    x: 10.8,
    y: 7.17,
    w: 1.8,
    h: 0.18,
    align: "right",
    fontFace: "Aptos",
    fontSize: 8.5,
    color: "C8D2DA",
    margin: 0,
  });
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

// 1. Title
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.teal);
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.75,
    y: 1.15,
    w: 4.1,
    h: 0.42,
    rectRadius: 0.04,
    line: { color: COLORS.mint, transparency: 100 },
    fill: { color: COLORS.mint },
  });
  slide.addText("RTDL STATUS SUMMARY", {
    x: 0.95,
    y: 1.24,
    w: 3.5,
    h: 0.2,
    fontFace: "Aptos",
    fontSize: 11,
    bold: true,
    color: COLORS.teal,
    margin: 0,
  });
  slide.addText("Python-Hosted Ray Tracing DSL", {
    x: 0.72,
    y: 1.72,
    w: 6.3,
    h: 0.7,
    fontFace: "Aptos Display",
    fontSize: 26,
    bold: true,
    color: COLORS.ink,
    margin: 0,
  });
  slide.addText("Current capabilities, usage, architecture, and the path to a fully functional backend", {
    x: 0.75,
    y: 2.5,
    w: 5.9,
    h: 0.45,
    fontFace: "Aptos",
    fontSize: 15,
    color: COLORS.gray,
    margin: 0,
  });
  addPanel(slide, 7.85, 1.25, 4.45, 2.65, "Project Snapshot",
    "Target: lower the difficulty of non-graphics ray tracing programming by ~10x.\n\nCurrent narrow path:\nPython kernel -> RT IR -> RayJoin backend plan -> OptiX/CUDA skeleton.\n\nFocused workload today:\nexact segment-vs-segment join with explicit layouts and roles.",
    COLORS.sand);
  addPanel(slide, 0.8, 4.35, 2.5, 1.05, "Workspace", "/Users/rl2025/rtdl_python_only", COLORS.white);
  addPanel(slide, 3.55, 4.35, 1.8, 1.05, "Tests", "4 passing", COLORS.white);
  addPanel(slide, 5.6, 4.35, 2.0, 1.05, "Backend", "RayJoin-only", COLORS.white);
  addPanel(slide, 7.85, 4.35, 2.25, 1.05, "Artifacts", "plan.json\n.cu\n.cpp", COLORS.white);
  addFooter(slide, 1);
}

// 2. What can we do now
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.gold);
  addTitle(slide, "What We Can Do Today", "The prototype is already useful as a compiler skeleton and backend planner.");
  addPanel(slide, 0.8, 1.7, 3.0, 2.15, "Frontend", "Define a kernel in Python with explicit geometry inputs, layouts, roles, traversal, refinement, and emit schema.", COLORS.white);
  addPanel(slide, 4.15, 1.7, 3.0, 2.15, "Compiler IR", "Compile the Python kernel into a structured RT IR that captures the workload, not raw OptiX details.", COLORS.white);
  addPanel(slide, 7.5, 1.7, 2.95, 2.15, "Backend Plan", "Lower the IR into a RayJoin-shaped plan with build/probe policy, payload registers, launch params, and output record schema.", COLORS.white);
  addPanel(slide, 10.75, 1.7, 1.75, 2.15, "Codegen", "Generate OptiX/CUDA skeleton files for inspection and future backend work.", COLORS.white);
  addBullets(slide, [
    "Supported narrow workload: exact segment-vs-segment join on the RayJoin backend path",
    "Generated artifacts: plan.json, device_kernels.cu, host_launcher.cpp, README.md",
    "Generated device code now includes optixTrace(...), payload mapping, and a concrete 2D segment intersection routine",
    "Validation in place: regression tests plus manual inspection of generated backend artifacts",
  ], { x: 0.9, y: 4.3, w: 11.8, h: 2.1, fontSize: 16 });
  addFooter(slide, 2);
}

// 3. What it cannot do yet
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.coral);
  addTitle(slide, "What It Cannot Do Yet", "The current system is a strong backend prototype, not a finished runtime.");
  addBullets(slide, [
    "It does not yet build or run a real OptiX pipeline end to end",
    "The generated code is structurally correct for the narrow path, but still a skeleton around runtime integration",
    "The current segment intersection uses float math; it is not exact in the robust computational-geometry sense",
    "The DSL does not yet support richer predicates, custom kernels, scheduling controls, or alternate backends",
    "There is no direct data integration yet with NumPy, Arrow, GPU memory allocators, or a real RayJoin codebase bridge",
  ], { x: 0.95, y: 1.8, w: 7.0, h: 4.9, fontSize: 16, color: COLORS.ink });
  addPanel(slide, 8.5, 1.9, 3.8, 1.5, "Current Boundary", "Compiler/backend milestone reached.\nRuntime replacement milestone not reached.", COLORS.sand);
  addPanel(slide, 8.5, 3.7, 3.8, 1.5, "Highest Risk", "Numerical robustness and exactness policy are still open research/engineering work.", COLORS.sand);
  addPanel(slide, 8.5, 5.5, 3.8, 1.0, "Takeaway", "Good architecture now.\nReal system next.", COLORS.white);
  addFooter(slide, 3);
}

// 4. How to use it
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.teal);
  addTitle(slide, "How To Use It", "Current workflow for the Python-only version.");
  addBullets(slide, [
    "1. Define a Python kernel with explicit layout and build/probe roles",
    "2. Compile it with rt.compile_kernel(...)",
    "3. Lower it with rt.lower_to_rayjoin(...)",
    "4. Generate backend artifacts with rt.generate_optix_project(...)",
    "5. Inspect plan.json and the emitted OptiX/CUDA skeleton files",
  ], { x: 0.85, y: 1.7, w: 5.1, h: 3.8, fontSize: 16 });
  addCodeBox(slide,
`import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def county_zip_join():
    segment_layout = rt.layout(
        "Segment2D",
        rt.field("x0", rt.f32), rt.field("y0", rt.f32),
        rt.field("x1", rt.f32), rt.field("y1", rt.f32),
        rt.field("id", rt.u32),
    )
    left = rt.input("left", rt.Segments, layout=segment_layout, role="probe")
    right = rt.input("right", rt.Segments, layout=segment_layout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=[
        "left_id", "right_id",
        "intersection_point_x", "intersection_point_y"
    ])`, 6.2, 1.75, 6.2, 3.95);
  addPanel(slide, 0.86, 6.1, 3.7, 0.56, "Run", "`make run-rtdsl-py`", COLORS.white);
  addPanel(slide, 4.85, 6.1, 3.1, 0.56, "Test", "`make test`", COLORS.white);
  addPanel(slide, 8.2, 6.1, 4.15, 0.56, "Generated output", "`generated/county_zip_join/`", COLORS.white);
  addFooter(slide, 4);
}

// 5. Main architecture
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.gold);
  addTitle(slide, "Main Architecture", "The project is now organized as a staged compiler pipeline.");
  const boxes = [
    { x: 0.8, y: 2.4, w: 2.2, h: 1.2, title: "Python DSL", body: "Kernel authoring API\ninputs · layouts · roles\ntraverse · refine · emit", fill: COLORS.white },
    { x: 3.35, y: 2.4, w: 2.2, h: 1.2, title: "RT IR", body: "CompiledKernel\nGeometryInput\nCandidateSet\nRefineOp · EmitOp", fill: COLORS.mint },
    { x: 5.9, y: 2.4, w: 2.3, h: 1.2, title: "RayJoin Plan", body: "build/probe policy\npayload registers\nlaunch params\noutput record", fill: COLORS.sand },
    { x: 8.6, y: 2.4, w: 2.1, h: 1.2, title: "Codegen", body: "plan.json\n.cu skeleton\nhost launcher", fill: COLORS.white },
    { x: 11.0, y: 2.4, w: 1.5, h: 1.2, title: "Future Runtime", body: "real OptiX\nintegration", fill: COLORS.mint },
  ];
  boxes.forEach((box) => addPanel(slide, box.x, box.y, box.w, box.h, box.title, box.body, box.fill));
  const arrowXs = [3.08, 5.63, 8.33, 10.83];
  for (const x of arrowXs) {
    slide.addShape(pptx.ShapeType.chevron, {
      x,
      y: 2.78,
      w: 0.14,
      h: 0.42,
      line: { color: COLORS.teal, transparency: 100 },
      fill: { color: COLORS.teal },
    });
  }
  addBullets(slide, [
    "Source language is Python; semantic core is the IR, not the surface syntax",
    "Backend-specific choices begin at lowering, not in the frontend",
    "Generated artifacts are meant to be inspectable and testable compiler outputs",
  ], { x: 1.0, y: 4.4, w: 11.2, h: 1.7, fontSize: 16 });
  addFooter(slide, 5);
}

// 6. Backend plan contract
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.teal);
  addTitle(slide, "Current Backend Contract", "What the RayJoin lowering decides before code generation.");
  addPanel(slide, 0.8, 1.7, 3.0, 1.55, "Input policy", "Build side: right\nProbe side: left\nLayouts: Segment2D / Segment2D\nBVH policy: build over right", COLORS.white);
  addPanel(slide, 4.05, 1.7, 3.05, 1.55, "Payload registers", "p0 probe_index\np1 build_primitive_index\np2 hit_t_bits\np3 hit_kind", COLORS.white);
  addPanel(slide, 7.35, 1.7, 2.55, 1.55, "Launch params", "traversable\nsegment buffers\noutput buffer\noutput counter\nprobe_count", COLORS.white);
  addPanel(slide, 10.15, 1.7, 2.35, 1.55, "Output schema", "IntersectionRecord\nleft_id\nright_id\nintersection_point_x\nintersection_point_y", COLORS.white);
  addCodeBox(slide,
`{
  "build_input": "right",
  "probe_input": "left",
  "payload_registers": ["probe_index", "build_primitive_index", "hit_t_bits", "hit_kind"],
  "launch_params": ["traversable", "right_segments", "left_segments", "output_records", "output_count", "probe_count"]
}`, 0.9, 3.7, 11.7, 2.1);
  addFooter(slide, 6);
}

// 7. Generated backend artifacts
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.gold);
  addTitle(slide, "Generated Backend Artifacts", "The generator now emits artifacts that are specific enough to guide real runtime work.");
  addPanel(slide, 0.8, 1.72, 3.1, 1.8, "plan.json", "Compiler/backend contract\ninputs, layouts, roles\npayload mapping\nlaunch params\noutput schema", COLORS.white);
  addPanel(slide, 4.15, 1.72, 4.0, 1.8, "device_kernels.cu", "OptixTrace call\nsegment intersection helper\nintersection program\nclosest-hit refinement\noutput record writes", COLORS.white);
  addPanel(slide, 8.45, 1.72, 3.9, 1.8, "host_launcher.cpp", "Host-side contract summary\nlaunch parameter expectations\nruntime TODO path", COLORS.white);
  addCodeBox(slide,
`static __forceinline__ __device__ bool rtdl_intersect_segments(...)
optixTrace(params.traversable, origin, direction, ...)
if (!rtdl_intersect_segments(probe, build, &hit_t, &ix, &iy)) return;
rtdl_pack_payload(probe_index, primitive_index, hit_t, 1u);
optixReportIntersection(hit_t, 0u);`, 1.0, 4.1, 11.3, 1.9);
  addFooter(slide, 7);
}

// 8. Verification status
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.coral);
  addTitle(slide, "Verification Status", "What has been checked so far, and what still needs runtime proof.");
  addPanel(slide, 0.85, 1.7, 3.7, 2.2, "Automated checks", "4 Python tests passing\ncompile path\nplan richness\ncodegen structure\ninvalid layout rejection", COLORS.white);
  addPanel(slide, 4.85, 1.7, 3.6, 2.2, "Manual checks", "Generated .cu and plan.json inspected after regeneration\npayload contract verified\nduplicate struct bug fixed", COLORS.white);
  addPanel(slide, 8.75, 1.7, 3.6, 2.2, "Remaining proof", "No end-to-end OptiX build yet\nno live BVH launch\nno side-by-side comparison with handwritten RayJoin path yet", COLORS.white);
  addBullets(slide, [
    "The compiler/backend milestone is materially stronger now than the initial skeleton",
    "The highest unresolved technical risk is not architecture anymore; it is runtime integration and numerical robustness",
  ], { x: 0.95, y: 4.45, w: 11.2, h: 1.45, fontSize: 16 });
  addFooter(slide, 8);
}

// 9. What is needed for a fully functional DSL
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.teal);
  addTitle(slide, "What Is Needed For A Fully Functional DSL", "The remaining work is now concrete and staged.");
  addBullets(slide, [
    "Real OptiX runtime integration: module creation, program groups, SBT assembly, launch plumbing",
    "Robust precision policy: conservative predicates, exact refinement, and well-defined failure bounds",
    "Real data integration: NumPy/Arrow/GPU buffer ownership and layout binding",
    "Richer language model: more predicates, geometry kinds, scheduling hints, and reusable kernels",
    "Backend expansion: keep RayJoin first, then generalize the IR to more non-graphics RT workloads",
  ], { x: 0.9, y: 1.8, w: 7.0, h: 4.7, fontSize: 16 });
  addPanel(slide, 8.4, 2.0, 3.9, 1.2, "Immediate blocker", "Runtime integration with a real OptiX build path", COLORS.sand);
  addPanel(slide, 8.4, 3.45, 3.9, 1.2, "Research blocker", "Exactness and robustness strategy for non-graphics workloads", COLORS.sand);
  addPanel(slide, 8.4, 4.9, 3.9, 1.2, "Product blocker", "A cleaner, broader kernel model than a single hard-coded join path", COLORS.sand);
  addFooter(slide, 9);
}

// 10. Next plan
{
  const slide = pptx.addSlide();
  addBackground(slide, COLORS.gold);
  addTitle(slide, "Next Plan", "Recommended sequence to move from strong prototype to usable system.");
  addPanel(slide, 0.85, 1.75, 2.85, 2.3, "Phase 1", "Bind the generated skeleton to a real OptiX build and execute one end-to-end segment join case.", COLORS.white);
  addPanel(slide, 3.95, 1.75, 2.85, 2.3, "Phase 2", "Compare generated output and behavior against a narrow handwritten RayJoin implementation.", COLORS.white);
  addPanel(slide, 7.05, 1.75, 2.85, 2.3, "Phase 3", "Replace float-only exactness claims with a precise robustness policy and implementation.", COLORS.white);
  addPanel(slide, 10.15, 1.75, 2.35, 2.3, "Phase 4", "Broaden the DSL and IR beyond one join path.", COLORS.white);
  addBullets(slide, [
    "Best near-term success criterion: generated code launches and matches a known segment-join baseline on one dataset",
    "Best medium-term success criterion: the IR remains stable as more predicates and data layouts are added",
    "Best long-term success criterion: the user writes kernels in Python while the compiler owns the RT backend complexity",
  ], { x: 0.95, y: 4.55, w: 11.2, h: 1.65, fontSize: 15.5 });
  addFooter(slide, 10);
}

async function main() {
  await pptx.writeFile({ fileName: "/Users/rl2025/rtdl_python_only/deck_status/rtdl_status_summary.pptx" });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
