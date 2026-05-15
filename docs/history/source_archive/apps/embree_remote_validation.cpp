#include <embree4/rtcore.h>
#include <embree4/rtcore_scene.h>

#include <cmath>
#include <cstdint>
#include <iostream>

namespace {

struct Vec3f {
  float x;
  float y;
  float z;
};

bool approx_equal(float lhs, float rhs, float eps = 1e-5f) {
  return std::fabs(lhs - rhs) <= eps;
}

}  // namespace

int main() {
  RTCDevice device = rtcNewDevice(nullptr);
  if (!device) {
    std::cerr << "failed: rtcNewDevice returned null\n";
    return 1;
  }

  RTCScene scene = rtcNewScene(device);
  RTCGeometry geometry = rtcNewGeometry(device, RTC_GEOMETRY_TYPE_TRIANGLE);

  auto* vertices = static_cast<Vec3f*>(
      rtcSetNewGeometryBuffer(
          geometry,
          RTC_BUFFER_TYPE_VERTEX,
          0,
          RTC_FORMAT_FLOAT3,
          sizeof(Vec3f),
          3));
  if (!vertices) {
    std::cerr << "failed: vertex buffer allocation returned null\n";
    rtcReleaseGeometry(geometry);
    rtcReleaseScene(scene);
    rtcReleaseDevice(device);
    return 2;
  }
  vertices[0] = {0.0f, 0.0f, 0.0f};
  vertices[1] = {1.0f, 0.0f, 0.0f};
  vertices[2] = {0.0f, 1.0f, 0.0f};

  auto* indices = static_cast<std::uint32_t*>(
      rtcSetNewGeometryBuffer(
          geometry,
          RTC_BUFFER_TYPE_INDEX,
          0,
          RTC_FORMAT_UINT3,
          3 * sizeof(std::uint32_t),
          1));
  if (!indices) {
    std::cerr << "failed: index buffer allocation returned null\n";
    rtcReleaseGeometry(geometry);
    rtcReleaseScene(scene);
    rtcReleaseDevice(device);
    return 3;
  }
  indices[0] = 0;
  indices[1] = 1;
  indices[2] = 2;

  rtcCommitGeometry(geometry);
  rtcAttachGeometry(scene, geometry);
  rtcReleaseGeometry(geometry);
  rtcCommitScene(scene);

  RTCRayHit rayhit{};
  rayhit.ray.org_x = 0.25f;
  rayhit.ray.org_y = 0.25f;
  rayhit.ray.org_z = 1.0f;
  rayhit.ray.dir_x = 0.0f;
  rayhit.ray.dir_y = 0.0f;
  rayhit.ray.dir_z = -1.0f;
  rayhit.ray.tnear = 0.0f;
  rayhit.ray.tfar = 1000.0f;
  rayhit.ray.flags = 0u;
  rayhit.hit.geomID = RTC_INVALID_GEOMETRY_ID;
  rayhit.hit.primID = RTC_INVALID_GEOMETRY_ID;
  rayhit.hit.instID[0] = RTC_INVALID_GEOMETRY_ID;

  RTCIntersectArguments arguments;
  rtcInitIntersectArguments(&arguments);
  rtcIntersect1(scene, &rayhit, &arguments);

  const bool ok =
      rayhit.hit.geomID == 0 &&
      rayhit.hit.primID == 0 &&
      approx_equal(rayhit.ray.tfar, 1.0f) &&
      approx_equal(rayhit.hit.u, 0.25f) &&
      approx_equal(rayhit.hit.v, 0.25f);

  if (!ok) {
    std::cerr << "failed: unexpected intersection result"
              << " geomID=" << rayhit.hit.geomID
              << " tfar=" << rayhit.ray.tfar
              << " u=" << rayhit.hit.u
              << " v=" << rayhit.hit.v << "\n";
    rtcReleaseScene(scene);
    rtcReleaseDevice(device);
    return 2;
  }

  std::cout << "embree_validation_ok "
            << "geomID=" << rayhit.hit.geomID
            << " primID=" << rayhit.hit.primID
            << " tfar=" << rayhit.ray.tfar
            << " u=" << rayhit.hit.u
            << " v=" << rayhit.hit.v << "\n";

  rtcReleaseScene(scene);
  rtcReleaseDevice(device);
  return 0;
}
