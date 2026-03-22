"""
Find all valid planetary gear configurations within constraints.
Outputs a table of configs that pass all validation rules.
"""

import math

def check_config(R, P, S, N):
    """
    Check if a planetary config is valid. Returns (valid, reason).
    """
    # Rule 1: Mesh constraint
    if R != S + 2 * P:
        return False, "mesh"

    # Rule 2: Assembly constraint
    if (R + S) % N != 0:
        return False, "assembly"

    # Rule 3: Planet non-interference
    carrier_factor = S + P
    planet_clearance_needed = P + 2
    planet_spacing = carrier_factor * math.sin(math.pi / N)
    if planet_spacing <= planet_clearance_needed:
        return False, "interference"

    # Rule 4: Minimum teeth
    if S < 6 or P < 6:
        return False, "min_teeth"

    # Rule 5: Planet count
    if N < 2 or N > 8:
        return False, "planet_count"

    return True, "ok"


def find_all_valid_configs(ratio_min=3.9, ratio_max=6.1, S_min=6, S_max=15, N_options=[3, 4, 5, 6]):
    """
    Find all valid configs within the specified constraints.
    """
    configs = []

    for S in range(S_min, S_max + 1):
        # ratio = (R + S) / S, so R = S * (ratio - 1)
        # P = (R - S) / 2

        # Iterate through possible R values that give ratios in range
        R_min = math.ceil(S * (ratio_min - 1))
        R_max = math.floor(S * (ratio_max - 1))

        for R in range(R_min, R_max + 1):
            # P must be integer
            if (R - S) % 2 != 0:
                continue
            P = (R - S) // 2

            if P < 6:
                continue

            ratio = (R + S) / S

            for N in N_options:
                valid, reason = check_config(R, P, S, N)
                if valid:
                    # Calculate clearance margin
                    spacing = (S + P) * math.sin(math.pi / N)
                    needed = P + 2
                    margin = spacing - needed

                    configs.append({
                        'R': R, 'P': P, 'S': S, 'N': N,
                        'ratio': ratio,
                        'margin': margin
                    })

    return configs


def main():
    print("=" * 80)
    print("VALID PLANETARY GEAR CONFIGURATIONS")
    print("Constraints: Ratio 3.9-6.1, S=6-15, N=3-6, all rules pass")
    print("=" * 80)
    print()

    configs = find_all_valid_configs(
        ratio_min=3.9,
        ratio_max=6.1,
        S_min=6,
        S_max=15,
        N_options=[3, 4, 5, 6]
    )

    # Sort by ratio, then by S
    configs.sort(key=lambda x: (x['ratio'], x['S']))

    # Group by ratio (rounded to 1 decimal)
    from collections import defaultdict
    by_ratio = defaultdict(list)
    for c in configs:
        ratio_key = f"{c['ratio']:.2f}"
        by_ratio[ratio_key].append(c)

    # Print table
    print(f"{'Ratio':<8} {'R/P/S':<12} {'N':<4} {'Teeth':<8} {'Margin':<8} {'Notes'}")
    print("-" * 80)

    current_ratio = None
    for c in configs:
        ratio_str = f"{c['ratio']:.2f}:1"
        config_str = f"R{c['R']}/P{c['P']}/S{c['S']}"
        teeth_total = c['R'] + c['P'] + c['S']

        # Notes
        notes = []
        if c['S'] == c['P']:
            notes.append("S=P")
        if c['margin'] > 5:
            notes.append("high margin")
        if c['N'] == 4:
            notes.append("4-planet")

        # Add separator between ratio groups
        ratio_rounded = round(c['ratio'], 1)
        if current_ratio is not None and ratio_rounded != current_ratio:
            print()
        current_ratio = ratio_rounded

        print(f"{ratio_str:<8} {config_str:<12} {c['N']:<4} {teeth_total:<8} {c['margin']:<8.1f} {', '.join(notes)}")

    print()
    print("=" * 80)
    print(f"Total valid configurations: {len(configs)}")
    print()

    # Summary by N
    print("Summary by planet count:")
    for N in [3, 4, 5, 6]:
        count = len([c for c in configs if c['N'] == N])
        print(f"  N={N}: {count} configs")

    print()
    print("Recommended configs (good balance of teeth size and margin):")
    print()

    # Find configs with N=4 and reasonable margin
    n4_configs = [c for c in configs if c['N'] == 4]
    n4_configs.sort(key=lambda x: (x['ratio'], -x['margin']))

    seen_ratios = set()
    print("  N=4 options (one per ratio):")
    for c in n4_configs:
        ratio_key = f"{c['ratio']:.1f}"
        if ratio_key not in seen_ratios:
            seen_ratios.add(ratio_key)
            print(f"    {c['ratio']:.2f}:1  R{c['R']}/P{c['P']}/S{c['S']}  margin={c['margin']:.1f}")

    print()
    n3_configs = [c for c in configs if c['N'] == 3]
    n3_configs.sort(key=lambda x: (x['ratio'], -x['margin']))

    seen_ratios = set()
    print("  N=3 options (one per ratio):")
    for c in n3_configs:
        ratio_key = f"{c['ratio']:.1f}"
        if ratio_key not in seen_ratios:
            seen_ratios.add(ratio_key)
            print(f"    {c['ratio']:.2f}:1  R{c['R']}/P{c['P']}/S{c['S']}  margin={c['margin']:.1f}")


if __name__ == "__main__":
    main()
