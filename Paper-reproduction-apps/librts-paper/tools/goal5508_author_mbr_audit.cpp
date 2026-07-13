#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>

#include "wkt_loader.h"

namespace {

std::uint64_t fnv1a_mix(std::uint64_t hash, std::uint32_t word) {
  for (int byte = 0; byte < 4; ++byte) {
    hash ^= static_cast<std::uint8_t>((word >> (byte * 8)) & 0xffu);
    hash *= 1099511628211ull;
  }
  return hash;
}

std::uint32_t float_bits(float value) {
  std::uint32_t bits = 0;
  std::memcpy(&bits, &value, sizeof(bits));
  return bits;
}

std::uint64_t hash_boxes(const std::vector<box_t>& boxes) {
  std::uint64_t hash = 1469598103934665603ull;
  for (const auto& box : boxes) {
    hash = fnv1a_mix(hash, float_bits(static_cast<float>(box.min_corner().x())));
    hash = fnv1a_mix(hash, float_bits(static_cast<float>(box.min_corner().y())));
    hash = fnv1a_mix(hash, float_bits(static_cast<float>(box.max_corner().x())));
    hash = fnv1a_mix(hash, float_bits(static_cast<float>(box.max_corner().y())));
  }
  return hash;
}

void print_box(const char* label, std::size_t index, const box_t& box) {
  const float values[] = {
      static_cast<float>(box.min_corner().x()),
      static_cast<float>(box.min_corner().y()),
      static_cast<float>(box.max_corner().x()),
      static_cast<float>(box.max_corner().y()),
  };
  std::cout << label << "_" << index << "=" << std::setprecision(9)
            << values[0] << "," << values[1] << "," << values[2] << ","
            << values[3] << " bits=" << std::hex << float_bits(values[0])
            << "," << float_bits(values[1]) << "," << float_bits(values[2])
            << "," << float_bits(values[3]) << std::dec << "\n";
}

void audit(const char* label, const std::string& path) {
  const auto polygons = LoadPolygons(path);
  const auto boxes = PolygonsToBoxes(polygons);
  std::cout << label << "_polygon_count=" << polygons.size() << "\n";
  std::cout << label << "_box_count=" << boxes.size() << "\n";
  std::cout << label << "_float32_mbr_fnv1a=" << std::hex << hash_boxes(boxes)
            << std::dec << "\n";
  if (!boxes.empty()) {
    print_box(label, 0, boxes.front());
    print_box(label, boxes.size() / 2, boxes[boxes.size() / 2]);
    print_box(label, boxes.size() - 1, boxes.back());
  }
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 5) {
    std::cerr << "usage: goal5508_author_mbr_audit geom query geom_label query_label\n";
    return 2;
  }
  audit(argv[3], argv[1]);
  audit(argv[4], argv[2]);
  return 0;
}
