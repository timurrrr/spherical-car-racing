# Welcome to the Race 2 of the Spherical Car Racing tournament!
#
# Today, we're going to have a slightly more complicated race:
# You need to drive a 100-meter section of a straight road as quickly as possible.
# You can enter the section at any speed, but your speed at the end of the
# section should be 30 m/s or lower.
#
# The current record is 2.386 seconds. Can you match or even beat it?
#
# Note that due to rounding errors you might not be able to have the exit speed
# precisely match 30 m/s.
#
# Only modify the code between the "LADIES AND GENTLEMEN, START YOUR ENGINES" and the
# "FINISH" lines.

import math
import solver

RACE_DISTANCE = 100 # meters. We're using the SI system here.
MAX_SPEED_AT_FINISH = 30 # m/s.
TIME_LIMIT = 50 # seconds.

# For simplicity, the car is AWD with CVT.
# Furthermore, these spherical cars race in vacuum, so there's no aero drag.
MASS = 1000 # kg.
POWER = 150000 # Watts. This is ~200 whp.
TRACTION = 10 # m/s^2.

INITIAL_POSITION = 0

# LADIES AND GENTLEMEN, START YOUR ENGINES
#
# Below is a very naive (and not the fastest!) solution.
# Edit it to your liking and see how much faster you can make the driver.
#
# Tip: try to solve this using your physics knowledge.
# Bonus points if your solution provides the fastest result for any RACE_DISTANCE.

# This time, you can control the initial speed.
INITIAL_SPEED = 30 # m/s.

# my_driver_algorithm(x, v, t) defines how your driver will drive.
#
# Inputs:
#   x: distance from the start position
#   v: speed
#   t: time since the start of the race
#
# Returns driver input (to the car), encoded as:
#   1 for maximum acceleration (think of it as an accelerator pedal),
#   -1 for maximum braking (think of it as a brake pedal),
#   anything in between -1 and 1 for partial acceleration/braking.
#
# This spherical car has traction control, meaning if the driver requests more
# power than the tires can handle, the car will only use the amount of power the
# tires can handle.
def my_driver_algorithm(x, v, t):
    if x < 69:
        return 1
    else:
        return -1

# # # # # # # # # # # # # # # # # # # # #
 # # # # # # # # FINISH! # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # #

def convert_racer_algorithm_to_acceleration(driver_input, v):
    if driver_input > 1:
        raise Exception(f"Too much throttle requested: {driver_input}")
    if driver_input < -1:
        raise Exception(f"Too much braking requested: {driver_input}")

    if driver_input > 0:
        # Power = Force * Velocity.
        # At low speeds, the car is traction limited and the TC kicks in:
        if driver_input * POWER >= TRACTION * MASS * v:
            return TRACTION
        # Beyond that, it's power-limited:
        return driver_input * POWER / (v * MASS)
    else:
        # Braking.
        return driver_input * TRACTION

def calculate_forces_p_v_t(positions, velocities, t):
    x = positions[0]
    v = velocities[0]
    return [convert_racer_algorithm_to_acceleration(my_driver_algorithm(x, v, t), v)]

data_log = [
   ([], "distance, m", "time, sec"),
   ([], "speed, m/s", "time, sec"),
   ([], "speed, m/s", "distance, m")
]

def progress_listener_callback_p_v_t(positions, velocities, t):
    if velocities[0] < 0 and positions[0] < RACE_DISTANCE:
        raise Exception(f"The car went backwards! Position = {positions[0]}, velocity = {velocities[0]}")

    data_log[0][0].append((positions[0], t))
    data_log[1][0].append((velocities[0], t))
    data_log[2][0].append((velocities[0], positions[0]))

    if positions[0] >= RACE_DISTANCE:
        return True  # Finished!
    return False

def main():
    positions, velocities, time = solver.solveRK4(
        [INITIAL_POSITION], [INITIAL_SPEED],
        calculate_forces_p_v_t,
        TIME_LIMIT, 0.001,
        progress_listener_callback_p_v_t)

    if time < TIME_LIMIT:
        if velocities[0] <= MAX_SPEED_AT_FINISH:
            # Need to do <= comparisons here as the underlying number has more than
            # .3 precision. It can be tricky to deal with rounding!
            if time <= 2.3855:
                print("NEW RECORD! Please reach out to timurrrr@ to certify.")
            elif time <= 2.386:
                print("YOU WON! Congrats.")
            else:
                print("Good effort, but can you go quicker?")
            print(f"Finished in {time:.3f} seconds.")
            print(f"Distance traveled: {positions[0]:.1f} meters.")
            print(f"Speed at the finish: {velocities[0]:.2f} m/s.")
        else:
            print("DISQUALIFIED!")
            print(f"Finished the race in {time:.3f} seconds,")
            print(f"but the speed at the finish was too high ({velocities[0]:.2f} m/s.)")
    else:
        print(f"DNF")

    if len(data_log[0][0]):
        try:
            import data_log_plotter
            graphs_filename = "race_02.png"
            data_log_plotter.plot_graphs(data_log, graphs_filename)
            print(f"Graphs for the data log were rendered to '{graphs_filename}'.")
        except ModuleNotFoundError:
            print("Unable to plot the graphs, please install Pillow. See README for tips.")
    else:
        print("Warning: no data log collected, not plotting the graphs.")

if __name__ == '__main__':
    main()
