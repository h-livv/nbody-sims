import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

CSV_FILE = "three_body_perturbed.csv"
BODY_RADIUS = 0.1  # Visual radius; this script does not calculate physics.
INTERVAL_MS = 20   # Delay between displayed frames.
TRAIL_LENGTH = 250 # Number of recent positions shown for each body; set None for full trails.

# Read the positions recorded by the C++ simulation.
time = []
positions = [[], [], []]

with open(CSV_FILE, newline="") as file:
    reader = csv.DictReader(file, skipinitialspace=True)
    required = ["time", "x1", "y1", "x2", "y2", "x3", "y3"]
    if reader.fieldnames is None or any(name not in reader.fieldnames for name in required):
        raise ValueError(
            "CSV must have headers: time, x1, y1, x2, y2, x3, y3"
        )

    for row in reader:
        time.append(float(row["time"]))
        for i in range(3):
            x = float(row[f"x{i + 1}"])
            y = float(row[f"y{i + 1}"])
            positions[i].append((x, y))

if not time:
    raise ValueError(f"No simulation data found in {CSV_FILE!r}.")

# Set fixed limits from all recorded positions so the view does not jump around.
all_x = [xy[0] for body in positions for xy in body]
all_y = [xy[1] for body in positions for xy in body]
padding = BODY_RADIUS + 0.5
x_min, x_max = min(all_x) - padding, max(all_x) + padding
y_min, y_max = min(all_y) - padding, max(all_y) + padding

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_aspect("equal", adjustable="box")
ax.set_xlabel("x position")
ax.set_ylabel("y position")
ax.set_title("Three-Body Simulation")
ax.grid(True, alpha=0.25)

# One circle and one trajectory line per body.
colors = ["tab:blue", "tab:orange", "tab:green"]
balls = []
trails = []
for i, color in enumerate(colors):
    ball = Circle(positions[i][0], BODY_RADIUS, color=color, label=f"Body {i + 1}")
    ax.add_patch(ball)
    balls.append(ball)
    (trail,) = ax.plot([], [], color=color, linewidth=1.2, alpha=0.75)
    trails.append(trail)

time_text = ax.text(0.02, 0.98, "", transform=ax.transAxes, va="top")
ax.legend(loc="upper right")


def update(frame):
    start = 0 if TRAIL_LENGTH is None else max(0, frame - TRAIL_LENGTH + 1)
    for i in range(3):
        x, y = positions[i][frame]
        balls[i].center = (x, y)
        path = positions[i][start:frame + 1]
        trails[i].set_data([p[0] for p in path], [p[1] for p in path])
    time_text.set_text(f"Time: {time[frame]:.3f} s")
    return (*balls, *trails, time_text)


animation = FuncAnimation(
    fig,
    update,
    frames=len(time),
    interval=INTERVAL_MS,
    blit=True,
    repeat=False,
)

plt.tight_layout()
plt.show()

# To save a GIF instead of (or as well as) displaying the window, uncomment:
# animation.save("three_body.gif", writer="pillow", fps=50)
