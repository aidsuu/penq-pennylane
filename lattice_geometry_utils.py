"""Square-lattice geometry helpers for mapped-wire TFIM workflows.

Mapping used in this module is row-major:
`s(x, y) = x + Lx * y`
for coordinates `x in [0, Lx-1]`, `y in [0, Ly-1]`.
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
