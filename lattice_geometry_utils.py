"""Mapped-wire lattice geometry helpers used by TFIM workflows.

Mappings used in this module:

- 2D square row-major:
    `s(x, y) = x + Lx * y`
- 3D cubic row-major-by-plane:
    `s(x, y, z) = x + Lx * y + Lx * Ly * z`
"""


def square_site_count(Lx, Ly):
    if Lx < 1 or Ly < 1:
        raise ValueError("Lx and Ly must be positive integers.")
    return int(Lx * Ly)


def square_site_index(Lx, x, y):
    if Lx < 1:
        raise ValueError("Lx must be positive.")
    if x < 0 or y < 0 or x >= Lx:
        raise ValueError("square_site_index received out-of-range coordinates.")
    return int(x + Lx * y)


def square_horizontal_pairs(Lx, Ly):
    if Lx < 1 or Ly < 1:
        raise ValueError("Lx and Ly must be positive integers.")
    pairs = []
    for y in range(Ly):
        for x in range(Lx - 1):
            left = square_site_index(Lx, x, y)
            right = square_site_index(Lx, x + 1, y)
            pairs.append((left, right))
    return pairs


def square_vertical_pairs(Lx, Ly):
    if Lx < 1 or Ly < 1:
        raise ValueError("Lx and Ly must be positive integers.")
    pairs = []
    for y in range(Ly - 1):
        for x in range(Lx):
            bottom = square_site_index(Lx, x, y)
            top = square_site_index(Lx, x, y + 1)
            pairs.append((bottom, top))
    return pairs


def cubic_site_count(Lx, Ly, Lz):
    if Lx < 1 or Ly < 1 or Lz < 1:
        raise ValueError("Lx, Ly, and Lz must be positive integers.")
    return int(Lx * Ly * Lz)


def cubic_site_index(x, y, z, Lx, Ly, Lz):
    if Lx < 1 or Ly < 1 or Lz < 1:
        raise ValueError("Lx, Ly, and Lz must be positive integers.")
    if x < 0 or y < 0 or z < 0 or x >= Lx or y >= Ly or z >= Lz:
        raise ValueError("cubic_site_index received out-of-range coordinates.")
    return int(x + Lx * y + Lx * Ly * z)


def cubic_x_pairs(Lx, Ly, Lz):
    if Lx < 1 or Ly < 1 or Lz < 1:
        raise ValueError("Lx, Ly, and Lz must be positive integers.")
    pairs = []
    for z in range(Lz):
        for y in range(Ly):
            for x in range(Lx - 1):
                left = cubic_site_index(x, y, z, Lx, Ly, Lz)
                right = cubic_site_index(x + 1, y, z, Lx, Ly, Lz)
                pairs.append((left, right))
    return pairs


def cubic_y_pairs(Lx, Ly, Lz):
    if Lx < 1 or Ly < 1 or Lz < 1:
        raise ValueError("Lx, Ly, and Lz must be positive integers.")
    pairs = []
    for z in range(Lz):
        for y in range(Ly - 1):
            for x in range(Lx):
                lower = cubic_site_index(x, y, z, Lx, Ly, Lz)
                upper = cubic_site_index(x, y + 1, z, Lx, Ly, Lz)
                pairs.append((lower, upper))
    return pairs


def cubic_z_pairs(Lx, Ly, Lz):
    if Lx < 1 or Ly < 1 or Lz < 1:
        raise ValueError("Lx, Ly, and Lz must be positive integers.")
    pairs = []
    for z in range(Lz - 1):
        for y in range(Ly):
            for x in range(Lx):
                lower = cubic_site_index(x, y, z, Lx, Ly, Lz)
                upper = cubic_site_index(x, y, z + 1, Lx, Ly, Lz)
                pairs.append((lower, upper))
    return pairs
