# Welcome to the Race 2 of the Spherical Car Racing tournament!
#
# Today we're going to go back to the basics, and study a single 90º corner.
# How hard can that be?
#
# TODO: draw the map as a PNG. For now, here's the text description:
#   You start anywhere between (0,0) and (20,0) drive at INITIAL_SPEED in the
#   direction of the y axis (i.e. up on the map).
#   You need to go around the cone at (20, 100), and finish between (120, 100)
#   and (120, 120).
#   Before the cone, you need to be between 0 and 20 on the x axis; after the
#   cone you need to be between 100 and 120 on the y axis.
#
# The current record is 6.837 seconds. Can you match or even beat it?
#
# Only modify the code between the "LADIES AND GENTLEMEN, START YOUR ENGINES" and the
# "FINISH" lines.

import math
import solver

TIME_LIMIT = 20 # seconds.

MAX_TRACTION = 10 # m/s^2.

# LADIES AND GENTLEMEN, START YOUR ENGINES
#
# Below is a very naive (and not the fastest!) solution.
# Edit it to your liking and see how much faster you can make the driver.
#
# Tip: try to solve this using your physics knowledge.
# This time it's probably too hard to make the solution generic enough, so I'm
# not going to tempt you with brownie points.

# The initial position along the x axis. Must be between 0 and 20.
# Intentionally picking an unoptimal initial value so that you can play around
# with the naive solution and quantify how much difference "using the whole
# width of the track" makes.
INITIAL_X = 10

# The initial velocity along the y axis.
# You can change the initial speed to your liking.
INITIAL_SPEED = 40

# my_driver_algorithm(x, y, vx, vy, t) defines how your driver will drive.
#
# Inputs:
#   x, y: coordinates relative to the starting position, in meters.
#   vx, vy: velocity vector, in m/s.
#   t: time since start
#
# Returns driver input (to the car), encoded as an acceleration tuple (ax, ay).
#   You can use any acceleration such that (ax**2 + ay**2) <= MAX_TRACTION**2.
#   Basically this spherical car is AWD and has enough power to spin the wheels
#   at any speed it can achieve in this race. Think Tesla Model S Plaid,
#   Lucid Air Sapphire or Bugatti Veyron. We assume that it can change direction
#   as desired, without limitation or negative effect to the overall traction.
#   It's a heck of a car!
#
#   Note that (ax, ay) are specified in the global frame of reference, not the
#   moving frame of reference of the car.
#
#   Hint: you're free to program the driver based on (x,y) only, or t only, or
#   any combination of inputs.
def my_driver_algorithm(x, y, vx, vy, t):
    # The naive solution involves driving in a straight line, then taking a 90º
    # arc at a constant speed, and then driving in a straight line towards the
    # finish.

    # If we want to hit the apex and we start 10 meters away from the inside
    # "wall" and we want to be 10 meters away from the inside wall after the
    # corner, this is the radius of the arc we need to take:
    R = 10 / (1 - math.sqrt(0.5))

    # This is the max speed we can carry in the arc at that speed.
    Vr = math.sqrt(MAX_TRACTION * R)

    # Driving in a straight line down the first straight.
    if x < 20 and y < 110 - R:
        # Hint: you can optimize this by using the knowledge from the previous
        # races.
        if vy > Vr:
            return 0, -10
        else:
            return 0, 0

    # 90º arc with a 20 meter radius with the center at (0, 20).
    if x < 10 + R:
        ax, ay = 10 + R - x, 110 - R - y
        norm = math.sqrt(math.pow(ax, 2) + math.pow(ay, 2))
        ax = 10 * ax / norm
        ay = 10 * ay / norm
        return ax, ay

    # Straight line acceleration to the finish.
    return 10, 0

# # # # # # # # # # # # # # # # # # # # #
 # # # # # # # # FINISH! # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # #

# Rounding and integration errors really suck! It's hard to precisely satisfy
# the "at most MAX_TRACTION total acceleration" constraint. To avoid turning
# this into a nightmare, I've introduced this function so that if the "driver"
# exceeds the limit only slighlty, it gets automatically reduced a bit to get
# back into the allowed range.
def normalize_accelerations(ax, ay):
    # If the value is too far from the limit, just return it -- betteer to expose
    # obvious bugs than hide and then waste time debugging.
    if ax**2 + ay**2 > 1.01 * (MAX_TRACTION ** 2):
        return (ax, ay)

    while ax**2 + ay**2 > MAX_TRACTION ** 2:
        ax = ax * 0.999
        ay = ay * 0.999
    return (ax, ay)

def calculate_accelerations_p_v_t(positions, velocities, t):
    ax, ay = my_driver_algorithm(positions[0], positions[1], velocities[0], velocities[1], t)
    total = math.sqrt(math.pow(ax, 2) + math.pow(ay, 2))
    ax, ay = normalize_accelerations(ax, ay)
    if ax**2 + ay**2 > MAX_TRACTION**2:
        raise Exception(f"Too much traction demanded: (ax={ax}, ay={ay}, total before normalization={total}")
    return [ax, ay]

data_log = [
   ([], "y, m", "x, m"),  # TODO force same scale x vs y.
   ([], "long G, m/s^2", "time, sec"),
   ([], "lat G, m/s^2", "time, sec"),
   ([], "speed, m/s", "distance, m"),
   ([], "long G, m/s^2", "distance, m"),
   ([], "lat G, m/s^2", "distance, m"),
   ([], "line curvature radius, m", "distance, m"),
]

INITIAL_POSITION = [INITIAL_X, 0]
prev_position = INITIAL_POSITION[:]
distance = 0

def progress_listener_callback_p_v_t(positions, velocities, t):
    x, y = positions[0], positions[1]
    if x < 0 or y > 120 or y < 0 or (x > 20 and y < 100):
        raise Exception(f"Cut the course at (x={x:.3f}, y={y:.3f}), t={t:.3f}")

    global distance
    global prev_position
    distance += math.sqrt(math.pow(positions[0] - prev_position[0], 2) + math.pow(positions[1] - prev_position[1], 2))
    prev_position = positions[:]

    vx, vy = velocities[0], velocities[1]
    ax, ay = my_driver_algorithm(x, y, vx, vy, t)

    v_total = math.sqrt(math.pow(vx, 2) + math.pow(vy, 2))
    if v_total > 0:
        long_g = (ax * vx + ay * vy) / v_total
        lat_g = (ax * vy - ay * vx) / v_total
    else:
        long_g = None
        lat_g = None

    if lat_g:
        line_curvature = math.pow(v_total, 2) / lat_g
        if abs(line_curvature) > 50:
            line_curvature = None
    else:
        line_curvature = None


    speed = math.sqrt(math.pow(velocities[0], 2) + math.pow(velocities[1], 2))

    data_log[0][0].append((positions[1], positions[0]))
    data_log[1][0].append((long_g, t))
    data_log[2][0].append((lat_g, t))
    data_log[3][0].append((speed, distance))
    data_log[4][0].append((long_g, distance))
    data_log[5][0].append((lat_g, distance))
    data_log[6][0].append((line_curvature, distance))

    if x >= 120 and y >= 100 and y <= 120:
        return True  # Finished!
    return False

def main():
    try:
        positions, velocities, time = solver.solveRK4(
            INITIAL_POSITION, [0, INITIAL_SPEED],
            calculate_accelerations_p_v_t,
            TIME_LIMIT, 0.0001,
            progress_listener_callback_p_v_t)

        if time < TIME_LIMIT:
            # Need to do <= comparisons here as the underlying number has more than
            # .3 precision. It can be tricky to deal with rounding!
            if time <= 6.8135:
                print("NEW RECORD! Please reach out to timurrrr@ to certify.")
            elif time <= 6.8145:
                print("YOU WON! Congrats.")
            else:
                print("Good effort, but can you go quicker?")
            print(f"Finished in {time:.3f} seconds.")
            print(f"Distance traveled: {distance:.3f} meters.")
        else:
            print(f"DNF")

    finally:
        # TODO: draw a map with obstacles.

        if len(data_log[0][0]):
            try:
                import data_log_plotter
                graphs_filename = "race_05.png"
                data_log_plotter.plot_graphs(data_log, graphs_filename)
                print(f"Graphs for the data log were rendered to '{graphs_filename}'.")
            except ModuleNotFoundError:
                print("Unable to plot the graphs, please install Pillow. See README for tips.")
        else:
            print("Warning: no data log collected, not plotting the graphs.")

if __name__ == '__main__':
    main()
