import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch
import matplotlib.patheffects as pe

SAVE_GIF = True
SAVE_MP4 = True

gif_name = "bbh_merger_distance_speed.gif"
mp4_name = "bbh_merger_distance_speed.mp4"

fps = 24
duration = 17
nframes = fps * duration

plt.rcParams["font.family"] = [
    "Comic Neue",
    "Humor Sans",
    "Comic Sans MS",
    "DejaVu Sans"
]

with plt.xkcd(scale=0.8, length=80, randomness=2):

    fig, ax = plt.subplots(figsize=(12, 7), facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    earth_pos = np.array([0.12, 0.16])
    galaxy_start = np.array([0.67, 0.68])
    galaxy_end = np.array([0.80, 0.73])

    rng = np.random.default_rng(4)
    ax.scatter(
        rng.uniform(0.02, 0.98, 120),
        rng.uniform(0.10, 0.95, 120),
        s=rng.uniform(2, 10, 120),
        color="black",
        alpha=0.22
    )

    # -------------------------
    # Earth
    # -------------------------

    earth = Circle(earth_pos, 0.05, fill=False, lw=2.5, color="black")
    ax.add_patch(earth)

    continent1 = Ellipse(
        (earth_pos[0] - 0.015, earth_pos[1] + 0.01),
        0.022, 0.012,
        angle=20,
        fill=False,
        lw=1.2,
        color="black"
    )

    continent2 = Ellipse(
        (earth_pos[0] + 0.018, earth_pos[1] - 0.012),
        0.018, 0.010,
        angle=-30,
        fill=False,
        lw=1.2,
        color="black"
    )

    ax.add_patch(continent1)
    ax.add_patch(continent2)

    ax.text(
        earth_pos[0],
        earth_pos[1] - 0.09,
        "EARTH",
        ha="center",
        fontsize=15
    )

    # -------------------------
    # Galaxy, initially hidden
    # -------------------------

    galaxy_rings = []

    for w, h, angle in [
        (0.24, 0.10, 15),
        (0.17, 0.07, 15),
        (0.10, 0.04, 15)
    ]:
        e = Ellipse(
            galaxy_start,
            w,
            h,
            angle=angle,
            fill=False,
            lw=1.8,
            color="black",
            alpha=0
        )
        ax.add_patch(e)
        galaxy_rings.append(e)

    galaxy_label = ax.text(
        galaxy_start[0],
        galaxy_start[1] + 0.11,
        "",
        ha="center",
        fontsize=16
    )

    # -------------------------
    # Black holes
    # -------------------------

    bh1, = ax.plot([], [], "ko", ms=10)
    bh2, = ax.plot([], [], "ko", ms=10)
    merged_bh, = ax.plot([], [], "ko", ms=14, alpha=0)

    # -------------------------
    # Ripple rings
    # -------------------------

    local_ripples = []

    for _ in range(5):
        c = Circle(
            galaxy_start,
            0.02,
            fill=False,
            lw=1.3,
            alpha=0,
            color="black"
        )
        ax.add_patch(c)
        local_ripples.append(c)

    # -------------------------
    # Travelling GW
    # -------------------------

    gw_line, = ax.plot([], [], color="black", lw=2)

    # -------------------------
    # Distance d
    # -------------------------

    d_line, = ax.plot(
        [],
        [],
        color="black",
        lw=1.8,
        ls="--",
        alpha=0
    )

    d_text = ax.text(
        0.40,
        0.37,
        "",
        fontsize=30,
        ha="center"
    )

    # -------------------------
    # Velocity v
    # -------------------------

    v_arrow = FancyArrowPatch(
        (0, 0),
        (0, 0),
        arrowstyle="->",
        mutation_scale=20,
        lw=2.2,
        color="black",
        alpha=0
    )
    ax.add_patch(v_arrow)

    v_text = ax.text(
        0.82,
        0.78,
        "",
        fontsize=30,
        ha="center"
    )

    note = ax.text(
        0.5,
        0.05,
        "",
        ha="center",
        fontsize=17,
        path_effects=[
            pe.withStroke(linewidth=4, foreground="white")
        ]
    )

    def interpolate(a, b, u):
        return (1 - u) * a + u * b

    def set_galaxy_alpha(alpha):
        for e in galaxy_rings:
            e.set_alpha(alpha)

    def update(frame):

        t = frame / nframes

        # -------------------------
        # Galaxy motion
        # -------------------------

        if t < 0.82:
            gpos = galaxy_start
        else:
            u = (t - 0.82) / 0.18
            u = np.clip(u, 0, 1)
            gpos = interpolate(galaxy_start, galaxy_end, u)

        for e in galaxy_rings:
            e.center = gpos

        # -------------------------
        # Show BBH first, then reveal galaxy
        # -------------------------

        if t < 0.25:
            set_galaxy_alpha(0)
            galaxy_label.set_text("")
            note.set_text("Two black holes spiral together...")

        elif t < 0.40:
            set_galaxy_alpha((t - 0.25) / 0.15)
            galaxy_label.set_text("this happens inside a galaxy")
            galaxy_label.set_position((gpos[0], gpos[1] + 0.11))
            note.set_text("That galaxy is where the merger happened.")

        else:
            set_galaxy_alpha(1)
            galaxy_label.set_text("this happens inside a galaxy")
            galaxy_label.set_position((gpos[0], gpos[1] + 0.11))

        # -------------------------
        # BBH inspiral
        # -------------------------

        if t < 0.35:

            u = t / 0.35
            sep = 0.06 * (1 - u) + 0.012
            angle = 9 * np.pi * u

            offset = np.array([
                sep * np.cos(angle),
                0.45 * sep * np.sin(angle)
            ])

            bh1.set_data(
                [gpos[0] - offset[0]],
                [gpos[1] - offset[1]]
            )

            bh2.set_data(
                [gpos[0] + offset[0]],
                [gpos[1] + offset[1]]
            )

            bh1.set_alpha(1)
            bh2.set_alpha(1)
            merged_bh.set_alpha(0)

        else:
            bh1.set_alpha(0)
            bh2.set_alpha(0)

            merged_bh.set_data([gpos[0]], [gpos[1]])
            merged_bh.set_alpha(1)

        # -------------------------
        # Local ripples
        # -------------------------

        if 0.35 <= t < 0.62:

            u = (t - 0.35) / 0.27

            for i, c in enumerate(local_ripples):
                r = 0.025 + 0.035 * (u * 5 - i)

                if r > 0:
                    c.center = gpos
                    c.set_radius(r)
                    c.set_alpha(max(0, 0.6 - r * 2.5))
                else:
                    c.set_alpha(0)

            note.set_text("The merger sends out gravitational waves.")

        else:
            for c in local_ripples:
                c.set_alpha(0)

        # -------------------------
        # GW travels to Earth
        # -------------------------

        if 0.48 <= t < 0.73:

            u = (t - 0.48) / 0.25
            u = np.clip(u, 0, 1)

            start = gpos
            end = earth_pos

            wave_end = interpolate(start, end, u)

            xs = np.linspace(start[0], wave_end[0], 250)
            ys = np.linspace(start[1], wave_end[1], 250)

            wiggle = 0.015 * np.sin(
                np.linspace(0, 16 * np.pi, 250)
            )

            gw_line.set_data(xs, ys + wiggle)
            gw_line.set_alpha(1)

            note.set_text("The gravitational waves reach Earth.")

        elif t >= 0.73:

            start = gpos
            end = earth_pos

            xs = np.linspace(start[0], end[0], 250)
            ys = np.linspace(start[1], end[1], 250)

            wiggle = 0.010 * np.sin(
                np.linspace(0, 16 * np.pi, 250)
            )

            gw_line.set_data(xs, ys + wiggle)
            gw_line.set_alpha(0.50)

        else:
            gw_line.set_data([], [])

        # -------------------------
        # Distance d
        # -------------------------

        if t >= 0.68:

            d_line.set_data(
                [earth_pos[0], gpos[0]],
                [earth_pos[1], gpos[1]]
            )

            d_line.set_alpha(0.85)
            d_text.set_text("d")

            d_text.set_position(
                (
                    (earth_pos[0] + gpos[0]) / 2,
                    (earth_pos[1] + gpos[1]) / 2 - 0.05
                )
            )

            note.set_text("The waves tell us the distance: d")

        else:
            d_line.set_alpha(0)
            d_text.set_text("")

        # -------------------------
        # Galaxy recession speed v
        # -------------------------

        if t >= 0.82:

            v_arrow.set_positions(
                (gpos[0] + 0.05, gpos[1]),
                (gpos[0] + 0.20, gpos[1] + 0.04)
            )

            v_arrow.set_alpha(1)
            v_text.set_text("v")

            v_text.set_position(
                (
                    gpos[0] + 0.14,
                    gpos[1] + 0.08
                )
            )

            note.set_text("The galaxy is moving away from us at speed v")

        else:
            v_arrow.set_alpha(0)
            v_text.set_text("")

        return []

    anim = FuncAnimation(
        fig,
        update,
        frames=nframes,
        interval=1000 / fps,
        blit=False
    )

    if SAVE_GIF:
        anim.save(
            gif_name,
            writer=PillowWriter(fps=fps)
        )
        print(f"Saved GIF: {gif_name}")

    if SAVE_MP4:
        try:
            anim.save(
                mp4_name,
                writer=FFMpegWriter(fps=fps, bitrate=2500)
            )
            print(f"Saved MP4: {mp4_name}")

        except Exception as e:
            print("MP4 failed. Install ffmpeg with:")
            print("sudo apt install ffmpeg")
            print(e)

    plt.show()
