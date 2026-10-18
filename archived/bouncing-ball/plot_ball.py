"""Plot the trajectory recorded by the C++ bouncing-ball simulation.

Expected CSV columns: time, position
Assumption: position is the ball centre's height above a floor at y = 0.
This script only visualizes recorded data; it does not simulate the physics.
"""

import csv
import matplotlib.pyplot as plt

CSV_PATH = "ball.csv"
RADIUS = 0.5  # Display/reference geometry only; physics is computed in C++.


def load_data(path):
    times = []
    positions = []

    with open(path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file, skipinitialspace=True)
        if not reader.fieldnames or not {"time", "position"}.issubset(reader.fieldnames):
            raise ValueError(
                f"{path} must have CSV headers named 'time' and 'position'. "
                f"Found: {reader.fieldnames}"
            )

        for row in reader:
            times.append(float(row["time"]))
            positions.append(float(row["position"]))

    if not times:
        raise ValueError(f"No simulation rows found in {path}.")

    return times, positions


def main():
    times, positions = load_data(CSV_PATH)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(times, positions, label="Ball centre", linewidth=1.8)
    ax.axhline(0, color="black", linewidth=1.5, label="Floor")
    ax.axhline(
        RADIUS,
        color="tab:orange",
        linestyle="--",
        linewidth=1.3,
        label="Centre height at contact",
    )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Centre height (m)")
    ax.set_title("Bouncing Ball — C++ Simulation Data")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
