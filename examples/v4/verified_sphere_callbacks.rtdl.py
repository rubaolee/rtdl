@optix.intersection
def sphere_intersection(ox: f32, oy: f32, oz: f32, dx: f32, dy: f32, dz: f32,
                        tmin: f32, tmax: f32, cx: f32, cy: f32, cz: f32,
                        radius: f32, item_id: u32):
    ocx = ox - cx
    ocy = oy - cy
    ocz = oz - cz
    b = ocx * dx + ocy * dy + ocz * dz
    c = ocx * ocx + ocy * ocy + ocz * ocz - radius * radius
    disc = b * b - c
    if disc >= 0.0:
        root = optix.sqrt(disc)
        near_t = -b - root
        far_t = -b + root
        t = near_t if near_t >= tmin else far_t
        if t >= tmin and t <= tmax:
            return optix.hit(t=t, item_id=item_id)
        else:
            return optix.no_hit()
    else:
        return optix.no_hit()

@optix.any_hit
def nearest_any_hit(hit_t: f32, hit_id: u32, best_t: f32, best_id: u32):
    if hit_t < best_t or (hit_t == best_t and hit_id < best_id):
        return optix.accept_continue(best_t=hit_t, best_id=hit_id)
    else:
        return optix.accept_continue(best_t=best_t, best_id=best_id)

@optix.miss
def preserve_miss(best_t: f32, best_id: u32):
    return optix.payload(best_t=best_t, best_id=best_id)
