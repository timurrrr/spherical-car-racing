# Welcome to the Race 3 of the Spherical Car Racing tournament!
#
# Today we're going to do our first 2D race, and it will start to resemble an
# autox course.
#
# TODO: draw the map as a PNG. For now, here's the text description:
#   You start at (0,0) and drive at INITIAL_SPEED in the direction of the
#   x axis (i.e. right on the map).
#   You turn left to go around a straight wall that starts at (20, 20) and goes
#   along the y axis (i.e. up on the map) to (20, 60)
#   You then need to turn right around the apex at (40, 40).
#   There's another straight wall from (20, 60) to (60, 60).
#   At the track out, you need to avoid the end of the third straight wall that
#   goes from (60, 60) to (60, 20).
#   The finish line is then ahead of you, going from (50, 0) to (70, 0).
#
# Only modify the code between the "LADIES AND GENTLEMEN, START YOUR ENGINES"
# and the "FINISH" lines.

# This is the current record. Can you match or even beat it?
RECORD = 6.828

from common import *
import math
import solver

TIME_LIMIT = 20 # seconds.

MAX_TRACTION = 10 # m/s^2.

# We start at (0, 0) in the frame of referene stationary to the track.
INITIAL_POSITION = [0, 0]

# LADIES AND GENTLEMEN, START YOUR ENGINES
#
# Below is a very naive (and not the fastest!) solution.
# Edit it to your liking and see how much faster you can make the driver.
#
# Tip: try to solve this using your physics knowledge.
# This time it's probably too hard to make the solution generic enough, so I'm
# not going to tempt you with brownie points.

# The car starts at x=0, y=0 and has an initial velocity along the x axis.
# You can change the initial speed to your liking.
# sqrt(20 * 10) is the max constant speed a car can drive around an arc with
# a 20 meter radius with 10 m/s traction.
INITIAL_SPEED = math.sqrt(20 * 10)

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
    # First, do a 90º arc with a 20 meter radius with the center at (0, 20).
    # The small offsets are added to correct for rounding/integration errors
    # (duh...). This shouldn't affect the total time much, and is not needed
    # for the optimal solution.
    if t < 0.5 * math.pi * 20 / INITIAL_SPEED:
        return (0.5 * (0 - x) + 0.0001, 0.5 * (20 - y))

    # Then, do an 180º arc with a 20 meter radius with the center at (40, 20).
    # 0.01 is added here to correct for rounding/integration errors as well.
    if t < 1.5 * math.pi * 20 / INITIAL_SPEED:
        return (0.5 * (40 - x) - 0.003, 0.5 * (20 - y) + 0.0001)

    # Straight line acceleration to the finish.
    return 0, -10

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
   ([], "line curvature radius, 1000/m", "distance, m"),
]
prev_position = [0, 0]
distance = 0
passed_apex = False

def progress_listener_callback_p_v_t(positions, velocities, t):
    x, y = positions[0], positions[1]
    if y > 20 and x < 20:
        raise Exception(f"Cut the course at (x={x:.3f}, y={y:.3f}), t={t:.3f}")
    if y > 20 and x > 60:
        raise Exception(f"Cut the course at (x={x:.3f}, y={y:.3f}), t={t:.3f}")
    if y > 60:
        raise Exception(f"Hit the wall at (x={x:.3f}, y={y:.3f}), t={t:.3f}")

    global passed_apex
    if x >= 40 and not passed_apex:
        if y < 40:
            raise Exception(f"Cut the course at (x={x:.3f}, y={y:.3f}), t={t:.3f}")
        passed_apex = True
        print(f"Passed the cone at (x={x:.3f}, y={y:.3f}), t={t:.3f}")

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
        line_radius = math.pow(v_total, 2) / lat_g
        line_curvature = 1000 / line_radius
    else:
        line_curvature = 0


    speed = math.sqrt(math.pow(velocities[0], 2) + math.pow(velocities[1], 2))

    data_log[0][0].append((positions[1], positions[0]))
    data_log[1][0].append((long_g, t))
    data_log[2][0].append((lat_g, t))
    data_log[3][0].append((speed, distance))
    data_log[4][0].append((long_g, distance))
    data_log[5][0].append((lat_g, distance))
    data_log[6][0].append((line_curvature, distance))

    if x >= 50 and x <= 70 and y < 0:
        return True  # Finished!
    return False

def main():
    try:
        positions, velocities, time = solver.solveRK4(
            INITIAL_POSITION, [INITIAL_SPEED, 0],
            calculate_accelerations_p_v_t,
            TIME_LIMIT, 0.0001,
            progress_listener_callback_p_v_t)

        if time < TIME_LIMIT:
            print(f"Finished in {time:.3f} seconds.")
            compare_lap_time_with_record_and_reference(time, RECORD, 7.701)
            print(f"Distance traveled: {distance:.3f} meters.")
        else:
            print(f"DNF")

    finally:
        # TODO: draw a map with obstacles.

        if len(data_log[0][0]):
            try:
                import data_log_plotter
                graphs_filename = "race_03.png"
                data_log_plotter.plot_graphs(data_log, graphs_filename)
                print(f"Graphs for the data log were rendered to '{graphs_filename}'.")
            except ModuleNotFoundError:
                print("Unable to plot the graphs, please install Pillow. See README for tips.")
        else:
            print("Warning: no data log collected, not plotting the graphs.")

if __name__ == '__main__':
    main()
