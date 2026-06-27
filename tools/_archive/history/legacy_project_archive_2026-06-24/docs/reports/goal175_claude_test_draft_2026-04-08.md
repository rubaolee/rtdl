Claude drafted the following focused test additions for the Goal 175 two-light
scene change. Codex integrated the bounded subset that matched the actual code
surface and added the missing summary metadata in the implementation.

```python
def test_secondary_light_is_off_at_clip_start(self) -> None:
    light = _secondary_frame_light(0.0)
    self.assertAlmostEqual(float(light["intensity"]), 0.0, places=6)
    self.assertAlmostEqual(float(light["display_alpha"]), 0.0, places=6)

def test_secondary_light_activates_after_ramp(self) -> None:
    early = _secondary_frame_light(0.0)
    active = _secondary_frame_light(0.5)
    self.assertAlmostEqual(float(early["intensity"]), 0.0, places=6)
    self.assertGreater(float(active["intensity"]), 0.0)
    faded = _secondary_frame_light(0.99)
    self.assertLess(float(faded["intensity"]), float(active["intensity"]))

def test_secondary_light_moves_left_to_right(self) -> None:
    positions = [
        float(_secondary_frame_light(p)["position"][0])
        for p in (0.1, 0.4, 0.7, 0.9)
    ]
    for left, right in zip(positions, positions[1:]):
        self.assertLess(left, right)

def test_secondary_light_y_and_z_are_constant(self) -> None:
    for phase in (0.0, 0.25, 0.5, 0.75, 1.0):
        pos = _secondary_frame_light(phase)["position"]
        self.assertAlmostEqual(float(pos[1]), 9.6, places=6)
        self.assertAlmostEqual(float(pos[2]), 11.8, places=6)

def test_frame_lights_returns_exactly_two_lights(self) -> None:
    for phase in (0.0, 0.3, 0.7):
        with self.subTest(phase=phase):
            lights = _frame_lights(phase)
            self.assertEqual(len(lights), 2)

def test_frame_lights_primary_is_yellow_secondary_is_red(self) -> None:
    lights = _frame_lights(0.5)
    primary, secondary = lights
    self.assertGreater(float(primary["color"][1]), 0.5)
    self.assertLess(float(secondary["color"][1]), 0.4)

def test_frame_lights_primary_always_has_positive_intensity(self) -> None:
    for phase in (0.0, 0.25, 0.5, 0.75):
        with self.subTest(phase=phase):
            primary = _frame_lights(phase)[0]
            self.assertGreater(float(primary["intensity"]), 0.0)

def test_summary_light_count_matches_two_light_setup(self) -> None:
    output_dir = Path("build/goal166_orbiting_star_ball_demo_test/light_count")
    summary = render_orbiting_star_ball_frames(
        backend="cpu_python_reference",
        compare_backend=None,
        width=20,
        height=20,
        latitude_bands=6,
        longitude_bands=12,
        frame_count=1,
        output_dir=output_dir,
    )
    self.assertEqual(summary.get("light_count"), 2)
    persisted = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    self.assertEqual(persisted.get("light_count"), 2)
```
