#!/usr/bin/env python3
"""
Approximate stronghold / End portal locations near a player
for Minecraft Java 1.9+ style stronghold rings.

Usage (terminal):
    python strongholds_near_me.py

Then follow the prompts.
"""

import math
import sys

# --- Stronghold ring layout for Java 1.9+ ---
# Distances are from (0,0) in OVERWORLD blocks.
# From community analysis: 8 rings, 128 strongholds total. :contentReference[oaicite:0]{index=0}
RING_STRONGHOLDS = [3, 6, 10, 15, 21, 28, 36, 9]

# Inner / outer radius for each ring (in blocks).
RING_RADII = [
    (1408, 2688),   # ring 0
    (4480, 5760),   # ring 1
    (7552, 8832),   # ring 2
    (10624, 11904), # ring 3
    (13696, 14976), # ring 4
    (16768, 18048), # ring 5
    (19840, 21120), # ring 6
    (22912, 24192), # ring 7
]

def java_like_seed_from_string(s: str) -> int:
    """
    Very rough stand-in for how Minecraft converts non-numeric seeds.
    If the user enters a number, we keep it. If not, we hash the string.

    This will NOT match Minecraft exactly for text seeds,
    but it lets this script work with them in a consistent way.
    """
    try:
        return int(s)
    except ValueError:
        # simple deterministic hash into 64-bit signed range
        h = 1125899906842597  # large prime
        for ch in s:
            h = (31 * h + ord(ch)) & 0xFFFFFFFFFFFFFFFF
        if h >= 2**63:
            h -= 2**63 * 2
        return h

def rng_next(seed: int) -> int:
    """
    Very small custom linear congruential generator (LCG),
    just to make per-seed angles deterministic.

    NOTE: This is NOT Mojang's exact Java Random implementation;
    it only exists so angles depend on the seed in a repeatable way.
    """
    a = 25214903917
    c = 11
    m = 2**48
    return (a * (seed & (m - 1)) + c) % m

def rng_double(seed: int) -> (float, int):
    """
    Use the LCG above to get a float in [0,1) and the next seed.
    """
    new_seed = rng_next(seed)
    # Take the high 26 bits-ish to make a 0–1 float
    value = (new_seed >> 22) / float(1 << 26)
    return value, new_seed

def generate_strongholds(seed_input: str):
    """
    Generate approximate stronghold positions for Java 1.9+ worlds.

    Returns a list of dicts:
        { "ring": int, "index": int, "x": float, "z": float, "radius": float }
    """
    base_seed = java_like_seed_from_string(seed_input)

    strongholds = []
    # Start an internal RNG seed derived from the world seed to vary angles
    internal_seed = (base_seed ^ 0x5DEECE66D) & ((1 << 48) - 1)

    for ring_index, (count, (r_min, r_max)) in enumerate(zip(RING_STRONGHOLDS, RING_RADII)):
        # pick a radius in the ring for this ring (approximate)
        frac, internal_seed = rng_double(internal_seed)
        radius = r_min + frac * (r_max - r_min)

        # base rotation per ring, depends on seed so worlds differ
        base_angle_frac, internal_seed = rng_double(internal_seed)
        base_angle = base_angle_frac * 2.0 * math.pi

        # distribute strongholds roughly evenly around the ring
        for i in range(count):
            # Slight per-stronghold angle jitter depending on seed
            jitter_frac, internal_seed = rng_double(internal_seed)
            jitter = (jitter_frac - 0.5) * (2 * math.pi / count * 0.4)  # ±20% of spacing

            angle = base_angle + (2.0 * math.pi * i / count) + jitter

            x = radius * math.cos(angle)
            z = radius * math.sin(angle)

            strongholds.append({
                "ring": ring_index,
                "index": i,
                "x": x,
                "z": z,
                "radius": radius,
            })

    return strongholds

def distance(x1, z1, x2, z2) -> float:
    dx = x2 - x1
    dz = z2 - z1
    return math.sqrt(dx*dx + dz*dz)

def find_nearby_strongholds(strongholds, player_x, player_z, max_distance):
    results = []
    for sh in strongholds:
        d = distance(player_x, player_z, sh["x"], sh["z"])
        if d <= max_distance:
            entry = dict(sh)
            entry["distance"] = d
            results.append(entry)
    # sort by distance ascending
    results.sort(key=lambda s: s["distance"])
    return results

def pretty_print_results(results):
    if not results:
        print("No strongholds found in that radius (with this approximation).")
        return

    print("\nApproximate strongholds near you:")
    print("-" * 60)
    for sh in results:
        print(
            f"Ring {sh['ring']}  |  Stronghold #{sh['index']:2d}  "
            f"|  X: {sh['x']:.1f}  Z: {sh['z']:.1f}  "
            f"|  Dist: {sh['distance']:.1f} blocks"
        )
    print("-" * 60)
    print("Remember: these are *approximate* locations. Use Eyes of Ender")
    print("or /locate structure stronghold in-game to confirm and dig down.")

def main():
    print("=== Minecraft Stronghold (End Portal) Approx Locator ===")
    print("Java 1.9+ style stronghold rings (approximate, not exact Mojang code)\n")

    seed_input = input("Enter world seed (number or text): ").strip()
    if not seed_input:
        print("Seed is required.")
        sys.exit(1)

    try:
        player_x = float(input("Your X coordinate: ").strip())
        player_z = float(input("Your Z coordinate: ").strip())
    except ValueError:
        print("X and Z must be numbers.")
        sys.exit(1)

    try:
        max_distance = float(input("Search radius (blocks, e.g. 5000): ").strip())
    except ValueError:
        print("Search radius must be a number.")
        sys.exit(1)

    strongholds = generate_strongholds(seed_input)
    nearby = find_nearby_strongholds(strongholds, player_x, player_z, max_distance)
    pretty_print_results(nearby)


if __name__ == "__main__":
    main()
