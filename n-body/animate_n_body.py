import csv
import math
import pygame

from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import (
    gluPerspective,
    gluNewQuadric,
    gluSphere,
    gluQuadricNormals,
    GLU_SMOOTH,
)


# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILE = "n_body.csv"

# These match the radius values in your C++ simulation.
# They are not stored in the CSV, so we specify them here.
PARTICLE_RADIUS = 0.1

CAMERA_DISTANCE = 60.0
TRAIL_LENGTH = 60
FPS = 60

# Sphere mesh resolution. Increase for smoother spheres.
SPHERE_SLICES = 16
SPHERE_STACKS = 12


# ============================================================
# LOAD CSV
# ============================================================

with open(CSV_FILE, newline="") as f:
    reader = csv.reader(f)
    header = next(reader)

    body_ids = sorted(
        int(col[1:])
        for col in header
        if col.startswith("x") and col[1:].isdigit()
    )

    if not body_ids:
        raise ValueError("No particle coordinates found in CSV.")

    for i in body_ids:
        for axis in ("x", "y", "z"):
            if f"{axis}{i}" not in header:
                raise ValueError(f"Missing column {axis}{i}.")

    coordinate_columns = [
        tuple(header.index(f"{axis}{i}") for axis in ("x", "y", "z"))
        for i in body_ids
    ]

    time_column = header.index("time")
    frames = []
    times = []

    for row in reader:
        t = float(row[time_column])

        frame = [
            tuple(float(row[c]) for c in cols)
            for cols in coordinate_columns
        ]

        if not all(
            math.isfinite(value)
            for position in frame
            for value in position
        ):
            raise ValueError(
                f"Invalid coordinates at time {t}. "
                "The simulation may have become numerically unstable."
            )

        times.append(t)
        frames.append(frame)

if not frames:
    raise ValueError("The CSV contains no simulation frames.")

n = len(body_ids)

print(f"Loaded {len(frames)} frames, {n} bodies.")


# ============================================================
# INITIALIZE PYGAME AND OPENGL
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1100, 800

pygame.display.set_mode(
    (WIDTH, HEIGHT),
    DOUBLEBUF | OPENGL
)

pygame.display.set_caption("3D N-Body Simulation")

glViewport(0, 0, WIDTH, HEIGHT)

# Perspective projection: distant objects appear smaller.
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45.0, WIDTH / HEIGHT, 0.1, 2000.0)

glMatrixMode(GL_MODELVIEW)

# Dark blue-black background.
glClearColor(0.008, 0.012, 0.028, 1.0)

# Depth testing allows nearer geometry to occlude farther geometry.
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LEQUAL)

# Smooth shading and correct transformed surface normals.
glShadeModel(GL_SMOOTH)
glEnable(GL_NORMALIZE)

# Smooth circular glow points.
glEnable(GL_POINT_SMOOTH)

# Transparency for trails and additive glow.
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# ------------------------------------------------------------
# Lighting
# ------------------------------------------------------------

glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glEnable(GL_COLOR_MATERIAL)

glColorMaterial(
    GL_FRONT_AND_BACK,
    GL_AMBIENT_AND_DIFFUSE
)

glLightfv(
    GL_LIGHT0, GL_AMBIENT,
    (0.12, 0.12, 0.16, 1.0)
)

glLightfv(
    GL_LIGHT0, GL_DIFFUSE,
    (1.0, 1.0, 1.0, 1.0)
)

glLightfv(
    GL_LIGHT0, GL_SPECULAR,
    (1.0, 1.0, 1.0, 1.0)
)

glLightModelfv(
    GL_LIGHT_MODEL_AMBIENT,
    (0.08, 0.08, 0.12, 1.0)
)

# Give the spheres visible highlights.
glMaterialfv(
    GL_FRONT_AND_BACK, GL_SPECULAR,
    (0.7, 0.7, 0.8, 1.0)
)

glMaterialf(
    GL_FRONT_AND_BACK, GL_SHININESS, 48.0
)


# ============================================================
# CREATE A REUSABLE SPHERE MESH
# ============================================================

quadric = gluNewQuadric()
gluQuadricNormals(quadric, GLU_SMOOTH)

# Compile the unit sphere once, rather than rebuilding its mesh
# separately for every particle in every frame.
sphere_list = glGenLists(1)

glNewList(sphere_list, GL_COMPILE)
gluSphere(quadric, 1.0, SPHERE_SLICES, SPHERE_STACKS)
glEndList()


# ============================================================
# CAMERA AND PLAYBACK STATE
# ============================================================

yaw = 0.0
pitch = 20.0
camera_distance = CAMERA_DISTANCE

dragging = False
paused = False
frame_index = 0

clock = pygame.time.Clock()
running = True


# ============================================================
# DRAW THE ACTUAL 3D SPHERES
# ============================================================

def draw_spheres(frame_index):
    current = frames[frame_index]

    for i, position in enumerate(current):
        x, y, z = position

        radius = PARTICLE_RADIUS
        glColor3f(0.12, 0.72, 1.0)   # Cyan-blue

        glPushMatrix()

        glTranslatef(x, y, z)
        glScalef(radius, radius, radius)

        glCallList(sphere_list)

        glPopMatrix()


# ============================================================
# DRAW GLOW AROUND PARTICLES
# ============================================================

def draw_glows(frame_index):
    current = frames[frame_index]

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glDepthMask(GL_FALSE)

    # Additive blending for a luminous effect.
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)

    # Broad, subtle blue halo.
    glPointSize(5.0)
    glBegin(GL_POINTS)

    for position in current:
        glColor4f(0.0, 0.45, 1.0, 0.20)
        glVertex3fv(position)

    glEnd()

    # Smaller, brighter halo.
    glPointSize(9.0)
    glBegin(GL_POINTS)

    for position in current:
        glColor4f(0.15, 0.75, 1.0, 0.18)
        glVertex3fv(position)

    glEnd()

    # Restore the normal graphics state.
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_TRUE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)


# ============================================================
# DRAW TRAILS
# ============================================================

def draw_trails(frame_index):
    start = max(0, frame_index - TRAIL_LENGTH)

    if start >= frame_index:
        return

    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Trails should not modify the depth buffer.
    glDepthMask(GL_FALSE)
    glLineWidth(1.5)

    glBegin(GL_LINES)

    # Skip body 0: it is fixed at the center.
    for i in range(0, n):
        for k in range(start + 1, frame_index + 1):
            fraction = (k - start) / (frame_index - start)
            alpha = 0.05 + 0.75 * fraction

            glColor4f(0.08, 0.65, 1.0, alpha)

            glVertex3fv(frames[k - 1][i])
            glVertex3fv(frames[k][i])

    glEnd()

    glDepthMask(GL_TRUE)
    glEnable(GL_LIGHTING)


# ============================================================
# MAIN LOOP
# ============================================================

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE:
                paused = not paused

            elif event.key == pygame.K_RIGHT:
                frame_index = min(
                    frame_index + 5, len(frames) - 1
                )

            elif event.key == pygame.K_LEFT:
                frame_index = max(frame_index - 5, 0)

            elif event.key == pygame.K_HOME:
                frame_index = 0

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            dx, dy = event.rel

            yaw += dx * 0.5
            pitch = max(-89.0, min(89.0, pitch + dy * 0.5))

        elif event.type == pygame.MOUSEWHEEL:
            camera_distance -= event.y * 2.0
            camera_distance = max(
                8.0, min(500.0, camera_distance)
            )

    # --------------------------------------------------------
    # Prepare frame and camera
    # --------------------------------------------------------

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # The light is positioned relative to the camera.
    glLightfv(
        GL_LIGHT0, GL_POSITION,
        (12.0, 18.0, 25.0, 1.0)
    )

    glTranslatef(0.0, 0.0, -camera_distance)
    glRotatef(pitch, 1.0, 0.0, 0.0)
    glRotatef(yaw, 0.0, 1.0, 0.0)

    # Glow behind the opaque spheres.
    draw_glows(frame_index)

    # Actual three-dimensional surfaces with lighting.
    draw_spheres(frame_index)

    # Trails are depth-tested, so spheres can occlude them.
    draw_trails(frame_index)

    pygame.display.flip()
    clock.tick(FPS)

    pygame.display.set_caption(
        f"3D N-Body | t={times[frame_index]:.3f} | "
        f"Bodies: {n} | "
        f"{'PAUSED' if paused else 'PLAYING'}"
    )

    if not paused:
        frame_index = (frame_index + 1) % len(frames)


# ============================================================
# CLEANUP
# ============================================================

glDeleteLists(sphere_list, 1)
gluDeleteQuadric(quadric)
pygame.quit()