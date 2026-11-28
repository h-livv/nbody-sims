import argparse
import pandas as pd
import matplotlib.pyplot as plt


def plot_trajectory(filename):
    # Load trajectory data
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()

    required = {"time", "x", "y", "z"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required}")

    df = df[["time", "x", "y", "z"]].apply(
        pd.to_numeric, errors="raise"
    ).dropna()

    if len(df) < 2:
        raise ValueError("Need at least two valid trajectory points.")

    t = df["time"].to_numpy()
    x = df["x"].to_numpy()
    y = df["y"].to_numpy()
    z = df["z"].to_numpy()

    # Create 3D plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Draw trajectory
    ax.plot(x, y, z, color="gray", linewidth=1, alpha=0.7)

    # Colour points according to time
    points = ax.scatter(
        x, y, z,
        c=t,
        cmap="viridis",
        s=8
    )

    # Mark start and end
    ax.scatter(*[x[0], y[0], z[0]],
               color="green", s=80, label="Start")
    ax.scatter(*[x[-1], y[-1], z[-1]],
               color="red", s=80, label="End")

    ax.set_xlabel("X position")
    ax.set_ylabel("Y position")
    ax.set_zlabel("Z position")
    ax.set_title("Particle Trajectory")

    fig.colorbar(points, ax=ax, label="Time", pad=0.1)
    ax.legend()

    # Keep the 3D plot's axis proportions comparable
    ranges = [
        max(values) - min(values)
        for values in (x, y, z)
    ]
    ranges = [r if r > 0 else 1e-12 for r in ranges]
    ax.set_box_aspect(ranges)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot a particle trajectory from a CSV file."
    )
    parser.add_argument("csv_file", help="Path to the trajectory CSV")
    args = parser.parse_args()

    plot_trajectory(args.csv_file)