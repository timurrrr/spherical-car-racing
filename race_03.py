# Welcome to the Race 2 of the Spherical Car Racing tournament!
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
# The current record is 6.828 seconds. Can you match or even beat it?
#
# Only modify the code between the "LADIES AND GENTLEMEN, START YOUR ENGINES" and the
# "FINISH" lines.

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
    # The 0.01 is added to correct for rounding/integration errors (duh...).
    # This shouldn't affect the total time much, and is not needed for the
    # optimal solution.
    if t < 0.5 * math.pi * 20 / INITIAL_SPEED:
        return (0.5 * (0 - x) + 0.01, 0.5 * (20 - y))

    # Then, do an 180º arc with a 20 meter radius with the center at (40, 20).
    # 0.01 is added here to correct for rounding/integration errors as well.
    if t < 1.5 * math.pi * 20 / INITIAL_SPEED:
        return (0.5 * (40 - x), 0.5 * (20 - y) + 0.01)

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
    ax, ay = normalize_accelerations(ax, ay)
    if ax**2 + ay**2 > MAX_TRACTION**2:
        raise Exception(f"Too much traction demanded: ({ax}, {ay})")
    return [ax, ay]

data_log = [
   ([], "y, m", "x, m"),
   ([], "x, m", "time, sec"),
   ([], "y, m", "time, sec"),
   ([], "speed, m/s", "distance, m")
]
prev_position = [0, 0]
distance = 0
passed_apex = False

def progress_listener_callback_p_v_t(positions, velocities, t):
    x, y = positions[0], positions[1]
    if y > 20 and x < 20:
        raise Exception(f"Cut the course at ({x}, {y})")
    if y > 20 and x > 60:
        raise Exception(f"Cut the course at ({x}, {y})")
    if y > 60:
        raise Exception(f"Hit the wall at ({x}, {y})")

    global passed_apex
    if x >= 40 and not passed_apex:
        if y >= 40:
            passed_apex = True
        else:
            raise Exception(f"Cut the course at ({x}, {y})")

    global distance
    global prev_position
    distance += math.sqrt(math.pow(positions[0] - prev_position[0], 2) + math.pow(positions[1] - prev_position[1], 2))
    prev_position = positions[:]

    speed = math.sqrt(math.pow(velocities[0], 2) + math.pow(velocities[1], 2))
    data_log[0][0].append((positions[1], positions[0]))
    data_log[1][0].append((positions[0], t))
    data_log[2][0].append((positions[1], t))
    data_log[3][0].append((speed, distance))

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
            # Need to do <= comparisons here as the underlying number has more than
            # .3 precision. It can be tricky to deal with rounding!
            if time <= 6.8275:
                print("NEW RECORD! Please reach out to timurrrr@ to certify.")
            elif time <= 6.8285:
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
                graphs_filename = "race_03.png"
                data_log_plotter.plot_graphs(data_log, graphs_filename)
                print(f"Graphs for the data log were rendered to '{graphs_filename}'.")
            except ModuleNotFoundError:
                print("Unable to plot the graphs, please install Pillow. See README for tips.")
        else:
            print("Warning: no data log collected, not plotting the graphs.")

if __name__ == '__main__':
    main()