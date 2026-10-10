"""Animate positions recorded by the C++ bouncing-ball simulation.

Expected CSV columns: time, position
Assumption: position is the ball centre's height above a floor at y = 0.
Python only renders the recorded trajectory; it does not update the physics.
"""

import csv
from statistics import median

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

CSV_PATH = "ball.csv"
RADIUS = 0.5          # Visual circle radius; set to match the C++ model.
PLAYBACK_SPEED = 2.0  # 1.0 = approximate simulation time; 2.0 = twice as fast.


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

    # Keep the displayed scene scaled to the recorded trajectory.
    x_extent = max(10 * RADIUS, 1.0)
    y_top = max(positions) + RADIUS + 0.2 * RADIUS
    y_bottom = min(0.0, min(positions) - 0.2 * RADIUS)

    fig, ax = plt.subplots(figsize=(6.5, 7))
    ax.set_xlim(-x_extent, x_extent)
    ax.set_ylim(y_bottom, y_top)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Horizontal position (m)")
    ax.set_ylabel("Height (m)")
    ax.set_title("Bouncing Ball — C++ Simulation Data")
    ax.grid(True, alpha=0.25)
    ax.axhline(0, color="black", linewidth=2, label="Floor")
    ax.axhline(
        RADIUS,
        color="tab:orange",
        linestyle="--",
        linewidth=1.0,
        alpha=0.75,
        label="Centre height at contact",
    )

    # Circle centre is the position recorded by C++.
    ball = Circle((0, positions[0]), RADIUS, color="royalblue")
    ax.add_patch(ball)
    time_label = ax.text(
        0.04, 0.96, "", transform=ax.transAxes,
        verticalalignment="top", fontsize=11
    )
    ax.legend(loc="upper right")

    def update(frame):
        ball.center = (0, positions[frame])
        time_label.set_text(f"Time: {times[frame]:.2f} s")
        return ball, time_label

    if len(times) > 1:
        positive_steps = [b - a for a, b in zip(times, times[1:]) if b > a]
        frame_interval_ms = 1000.0 * median(positive_steps) / PLAYBACK_SPEED if positive_steps else 50.0
    else:
        frame_interval_ms = 50.0

    animation = FuncAnimation(
        fig,
        update,
        frames=len(times),
        interval=frame_interval_ms,
        blit=True,
        repeat=False,
    )

    # Keep a reference alive for the duration of the window.
    _ = animation
    fig.tight_layout()
    #animation.save("bouncing_ball.gif", writer="pillow", fps=30)
    plt.show()


if __name__ == "__main__":
    main()
