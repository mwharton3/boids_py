# Import standard modules.
import argparse
import sys
import svgwrite

# Import non-standard modules.
import pygame as pg
from pygame.locals import *

# Import local modules
from boid import Boid

###########################
# DEFAULTS
default_boids = 50
num_frames = 1000

# BOID PARAMETERS
Boid.min_speed = 0.01
Boid.max_speed = 0.2
Boid.max_force = 1
Boid.max_turn = 5
Boid.perception = 100
Boid.crowding = 15
Boid.edge_distance_pct = 5
###########################


default_geometry = "1000x1000"
boid_paths = [[] for _ in range(default_boids)]


def update(dt, boids):
    """
    Update game. Called once per frame.
    dt is the amount of time passed since last frame.
    If you want to have constant apparent movement no matter your framerate,
    what you can do is something like

    x += v * dt

    and this will scale your velocity based on time. Extend as necessary."""

    # Go through events that are passed to the script by the window.
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit(0)
        elif event.type == KEYDOWN:
            mods = pg.key.get_mods()
            if event.key == pg.K_q:
                # quit
                pg.quit()
                sys.exit(0)
            elif event.key == pg.K_UP:
                # add boids
                if mods & pg.KMOD_SHIFT:
                    add_boids(boids, 100)
                else:
                    add_boids(boids, 10)
            elif event.key == pg.K_DOWN:
                # remove boids
                if mods & pg.KMOD_SHIFT:
                    boids.remove(boids.sprites()[:100])
                else:
                    boids.remove(boids.sprites()[:10])
            elif event.key == pg.K_1:
                for boid in boids:
                    boid.max_force /= 2
                print("max force {}".format(boids.sprites()[0].max_force))
            elif event.key == pg.K_2:
                for boid in boids:
                    boid.max_force *= 2
                print("max force {}".format(boids.sprites()[0].max_force))
            elif event.key == pg.K_3:
                for boid in boids:
                    boid.perception *= 0.8
                print("perception {}".format(boids.sprites()[0].perception))
            elif event.key == pg.K_4:
                for boid in boids:
                    boid.perception *= 1.2
                print("perception {}".format(boids.sprites()[0].perception))
            elif event.key == pg.K_5:
                for boid in boids:
                    boid.crowding *= 0.8
                print("crowding {}".format(boids.sprites()[0].crowding))
            elif event.key == pg.K_6:
                for boid in boids:
                    boid.crowding *= 1.2
                print("crowding {}".format(boids.sprites()[0].crowding))
            elif event.key == pg.K_d:
                # toggle debug
                for boid in boids:
                    boid.debug = not boid.debug
            elif event.key == pg.K_r:
                # reset
                num_boids = len(boids)
                boids.empty()
                add_boids(boids, num_boids)

    for i, b in enumerate(boids):
        b.update(dt, boids)


def draw(screen, background, boids):
    """
    Draw things to the window. Called once per frame.
    """

    # Redraw screen here
    boids.clear(screen, background)
    dirty = boids.draw(screen)

    # Save the paths
    for i, b in enumerate(boids):
        boid_paths[i].append((b.position[0], b.position[1]))

    # Flip the display so that the things we drew actually show up.
    pg.display.update(dirty)


def path2str(path):
    pathstr = ""
    for i, pt in enumerate(path):
        basepath = f"{int(pt[0])},{int(pt[1])}"
        if i == 0:
            pathstr += "M" + basepath
        elif i == 1:
            pathstr += " C" + basepath
        else:
            pathstr += " " + basepath
    return pathstr


def main(args):
    # Initialise pg.
    pg.init()

    pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP])

    # Set up the clock to maintain a relatively constant framerate.
    fps = 60.0
    fpsClock = pg.time.Clock()

    # Set up the window.
    logo = pg.image.load("logo32x32.png")
    pg.display.set_icon(logo)
    pg.display.set_caption("BOIDS!")
    window_width, window_height = [int(x) for x in args.geometry.split("x")]
    flags = DOUBLEBUF

    screen = pg.display.set_mode((window_width, window_height), flags)
    screen.set_alpha(None)
    background = pg.Surface(screen.get_size()).convert()
    background.fill(pg.Color("black"))

    boids = pg.sprite.RenderUpdates()

    add_boids(boids, args.num_boids)

    # Main game loop.
    dt = 1 / fps  # dt is the time since last frame.

    # Loop over all the frames
    for _ in range(num_frames):
        update(dt, boids)
        draw(screen, background, boids)
        dt = fpsClock.tick(fps)

    # Write the result to SVG
    dwg = svgwrite.Drawing("boid_paths.svg", profile="tiny", size=("1000px", "1000px"))
    for path in boid_paths:
        dwg.add(
            dwg.path(
                d=path2str(path),
                stroke="#000",
                fill="none",
                stroke_width=1,
            )
        )
    dwg.save()


def add_boids(boids, num_boids):
    for _ in range(num_boids):
        boids.add(Boid())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Emergent flocking.")
    parser.add_argument(
        "--geometry",
        metavar="WxH",
        type=str,
        default=default_geometry,
        help="geometry of window",
    )
    parser.add_argument(
        "--number",
        dest="num_boids",
        default=default_boids,
        help="number of boids to generate",
    )
    args = parser.parse_args()

    main(args)
