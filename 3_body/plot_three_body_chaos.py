#!/usr/bin/env python3
"""Compare two three-body simulations with nearby initial conditions.

Expected CSV columns (spaces after commas are fine):
time, x1, y1, x2, y2, x3, y3

The two simulations should use the same physics, integrator, time step, and
output cadence. Only the initial conditions should differ slightly.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Change these names to match your output files.
BASELINE_CSV = "three_body.csv"
PERTURBED_CSV = "three_body_perturbed.csv"

BODY_COLORS = ("tab:blue", "tab:orange", "tab:green")


def load_simulation(filename):
    """Load time and the three bodies' x/y positions from CSV."""
    times = []
    positions = []

    with open(filename, "r", newline="") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        required = ["time", "x1", "y1", "x2", "y2", "x3", "y3"]
        if reader.fieldnames is None:
            raise ValueError(f"{filename}: CSV is empty or has no header")

        missing = [name for name in required if name not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"{filename}: missing columns {missing}. "
                f"Found: {reader.fieldnames}"
            )

        for line_number, row in enumerate(reader, start=2):
            try:
                times.append(float(row["time"]))
                positions.append([
                    [float(row["x1"]), float(row["y1"])],
                    [float(row["x2"]), float(row["y2"])],
                    [float(row["x3"]), float(row["y3"])],
                ])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{filename}: invalid numeric data on line {line_number}"
                ) from exc

    if not times:
        raise ValueError(f"{filename}: no data rows found")

    times = np.asarray(times, dtype=float)
    positions = np.asarray(positions, dtype=float)  # (steps, 3 bodies, 2 coordinates)

    if not np.all(np.isfinite(times)) or not np.all(np.isfinite(positions)):
        raise ValueError(f"{filename}: contains NaN or infinite values")

    return times, positions


def main():
    for filename in (BASELINE_CSV, PERTURBED_CSV):
        if not Path(filename).is_file():
            raise FileNotFoundError(
                f"Could not find {filename!r}. Put it beside this script or "
                "change BASELINE_CSV / PERTURBED_CSV at the top of the script."
            )

    t_base, r_base = load_simulation(BASELINE_CSV)
    t_pert, r_pert = load_simulation(PERTURBED_CSV)

    # Compare only the shared length; require the timestamps to match.
    n = min(len(t_base), len(t_pert))
    t_base, r_base = t_base[:n], r_base[:n]
    t_pert, r_pert = t_pert[:n], r_pert[:n]

    if not np.allclose(t_base, t_pert, rtol=1e-8, atol=1e-10):
        raise ValueError(
            "The CSV timestamps do not match. Run both simulations with the "
            "same time step and output cadence before comparing them."
        )

    times = t_base

    # Per-body position differences, then RMS over all three bodies.
    # This is a position-separation diagnostic, not the full phase-space distance.
    per_body_separation = np.linalg.norm(r_pert - r_base, axis=2)  # (steps, 3)
    rms_separation = np.sqrt(np.mean(per_body_separation**2, axis=1))

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    fig.suptitle("Three-Body Simulation: Sensitivity to Initial Conditions", fontsize=14)

    # Baseline trajectory.
    ax = axes[0]
    for body in range(3):
        ax.plot(r_base[:, body, 0], r_base[:, body, 1],
                color=BODY_COLORS[body], label=f"Body {body + 1}")
        ax.scatter(r_base[0, body, 0], r_base[0, body, 1],
                   color=BODY_COLORS[body], marker="o", s=28)
    ax.set_title("Baseline trajectory")
    ax.set_xlabel("x position")
    ax.set_ylabel("y position")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)

    # Slightly perturbed trajectory, same body color, dashed lines.
    ax = axes[1]
    for body in range(3):
        ax.plot(r_pert[:, body, 0], r_pert[:, body, 1],
                color=BODY_COLORS[body], linestyle="--", label=f"Body {body + 1}")
        ax.scatter(r_pert[0, body, 0], r_pert[0, body, 1],
                   color=BODY_COLORS[body], marker="o", s=28)
    ax.set_title("Nearby initial conditions")
    ax.set_xlabel("x position")
    ax.set_ylabel("y position")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)

    # On a log scale, growth over several orders of magnitude is easier to inspect.
    ax = axes[2]
    positive = rms_separation > 0
    if np.any(positive):
        ax.semilogy(times[positive], rms_separation[positive], color="black")
    else:
        ax.text(0.5, 0.5, "No measurable position separation", ha="center",
                va="center", transform=ax.transAxes)
    ax.set_title("RMS position separation")
    ax.set_xlabel("Time")
    ax.set_ylabel("RMS separation (log scale)")
    ax.grid(True, which="both", alpha=0.3)

    plt.tight_layout()
    plt.show()

    if np.any(positive):
        print(f"Compared {n} aligned time samples from t={times[0]:g} to {times[-1]:g}.")
        print(f"Initial measured RMS position separation: {rms_separation[positive][0]:.6g}")
        print(f"Final RMS position separation: {rms_separation[-1]:.6g}")
        print("Interpretation: sustained rapid separation supports sensitivity to initial conditions,")
        print("but one plot alone does not prove chaos. Check time-step convergence and numerical error.")


if __name__ == "__main__":
    main()
