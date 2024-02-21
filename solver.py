import math
import unittest

# Iteration functions

def calculateNextStateEulerCore(y, t, dY_function, h):
    k = dY_function(y, t)
    result = y[:]
    for i in range(len(y)):
        result[i] += h * k[i]
    return result

def calculateNextStateEuler(positions, velocities, t, accelerationsFunction, delta_t):
    tmp = calculateNextStateEulerCore(
        positions + velocities, t,
        lambda y, t: (y[len(positions):] + accelerationsFunction(y[:len(positions)], y[len(positions):], t)),
        delta_t)
    return tmp[:len(positions)], tmp[len(positions):]

def calculateNextStateRK4(positions, velocities, t, accelerationsFunction, delta_t):
    # See https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods

    f = lambda y, t: y[len(positions):] + accelerationsFunction(y[:len(positions)], y[len(positions):], t)

    y0 = positions + velocities

    k1 = f(y0, t)
    y1 = y0[:]
    for i in range(len(y1)):
        y1[i] += 0.5 * delta_t * k1[i]

    k2 = f(y1, t + delta_t * 0.5)
    y2 = y0[:]
    for i in range(len(y1)):
        y2[i] += 0.5 * delta_t * k2[i]

    k3 = f(y2, t + delta_t * 0.5)
    y3 = y0[:]
    for i in range(len(y1)):
        y3[i] += delta_t * k2[i]

    k4 = f(y3, t + delta_t)

    yf = y0[:]
    for i in range(len(y1)):
        yf[i] += delta_t * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6
    return yf[:len(positions)], yf[len(positions):]

# Loop functions

def solveGeneric(initial_positions, initial_velocities, calculate_accelerations_p_v_t, duration, time_step, solver_function, progress_listener_callback_p_v_t):
    if len(initial_positions) == 0:
        raise Exception("No positions")
    if len(initial_positions) != len(initial_velocities):
        raise Exception("The size of the positions and velocities vectors don't match (" + len(initial_positions) + " vs " + len(initial_velocities) + ")")
    positions = initial_positions[:]
    velocities = initial_velocities[:]

    time = 0
    finished = False
    while time < duration:
        if progress_listener_callback_p_v_t:
            finished = progress_listener_callback_p_v_t(positions, velocities, time)
            if finished:
                break
        positions, velocities = solver_function(positions, velocities, time, calculate_accelerations_p_v_t, time_step)
        time = time + time_step

    if not finished and progress_listener_callback_p_v_t:
        progress_listener_callback_p_v_t(positions, velocities, time)
    return positions, velocities, time

def solveRK4(initial_positions, initial_velocities, calculate_accelerations_p_v_t, duration, time_step, progress_listener_callback_p_v_t = None):
    return solveGeneric(initial_positions, initial_velocities, calculate_accelerations_p_v_t, duration, time_step, calculateNextStateRK4, progress_listener_callback_p_v_t)

#### Self tests

class TestStringMethods(unittest.TestCase):

    def assertEqualsApprox(self, actual, expected, tolerance):
        self.assertGreaterEqual(actual, expected - tolerance)
        self.assertLessEqual(actual, expected + tolerance)

    def test_stationary_object_no_accelerations(self):
        # Basic sanity test: a stationary object with acceleration applied remains stationary.
        #   x(t) = 42,
        #   v_x(t) = 0.

        positions = [42]
        velocities = [0]
        calculate_accelerations_p_v_t = lambda p, v, t: [0]

        positions, velocities, time = solveRK4(positions, velocities, calculate_accelerations_p_v_t, 10, 0.1)

        # Ideally this would be exactly 10, but adding 0.1 10 times gives 0.9999999999999999.
        # Close enough for practical applications, but bad for precise checks like this.
        # It gets better with a smaller time step.
        self.assertEqualsApprox(time, 10, 0.1)

        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0], 42)

        self.assertEqual(len(velocities), 1)
        self.assertEqual(velocities[0], 0)


    def test_moving_object_no_force(self):
        # An object with no force applied continues to travel with a constant velocity.
        #   x(t) = 1 * t,
        #   v_x(t) = 1.

        positions = [0]
        velocities = [1]
        calculate_accelerations_p_v_t = lambda p, v, t: [0]

        positions, velocities, time = solveRK4(positions, velocities, calculate_accelerations_p_v_t, 10, 0.001)

        self.assertEqualsApprox(time, 10, 0.001)
        
        self.assertEqual(len(positions), 1)

        # This is much closer to the expected 50.
        self.assertEqualsApprox(positions[0], 10, 0.001)

        self.assertEqual(len(velocities), 1)
        self.assertEqual(velocities[0], 1)

    def test_stationary_object_constant_force(self):
        # A stationary object with a constant force applied travels at
        #   x(t) = 1 * t^2 / 2,
        #   v_x(t) = 1 * t.

        positions = [0]
        velocities = [0]
        calculate_accelerations_p_v_t = lambda p, v, t: [1]

        positions, velocities, time = solveRK4(positions, velocities, calculate_accelerations_p_v_t, 10, 0.001)

        self.assertEqualsApprox(time, 10, 0.001)
        
        self.assertEqual(len(positions), 1)

        # This is much closer to the expected 50.
        # 0.011 out of 50 is 0.022% precision.
        self.assertEqualsApprox(positions[0], 50, 0.011)

        self.assertEqual(len(velocities), 1)
        self.assertEqualsApprox(velocities[0], 10, 0.001)


    def test_moving_object_acceleration(self):
        # x(t) = 1 * t + 1 * t^2 / 2,
        # v_x(t) = 1 + 1 * t.

        positions = [0]
        velocities = [1]
        calculate_accelerations_p_v_t = lambda p, v, t: [1]

        positions, velocities, time = solveRK4(positions, velocities, calculate_accelerations_p_v_t, 10, 0.001)

        self.assertEqualsApprox(time, 10, 0.001)
        
        self.assertEqual(len(positions), 1)
        self.assertEqualsApprox(positions[0], 60, 0.02)

        self.assertEqual(len(velocities), 1)
        self.assertEqualsApprox(velocities[0], 11, 0.001)

    def test_pendulum(self):
        # Differential equation: f(x, v, t) = - x.
        # The precise solution is:
        #   x = cos(t),
        #   v = -sin(t).

        init_positions = [1]
        init_velocities = [0]
        calculate_accelerations_p_v_t = lambda p, v, t: [-p[0]]

        # Energy = (x^2 + v^2)/2.
        # For the precise solution, the energy of this system remains constant at 0.5.
        # Many other solving algorithm either lose or gain energy out of nowhere,
        # so it's useful to sanity test what we have here.
        energy = lambda p, v: 0.5 * (math.pow(p[0], 2) + math.pow(v[0], 2))

        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 1.5708, 0.001)
        self.assertEqualsApprox(positions[0], 0, 0.0003)
        self.assertEqualsApprox(velocities[0], -1, 0.00001)
        self.assertEqualsApprox(energy(positions, velocities), 0.5, 0.00000001)

        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 3.1416, 0.001)
        self.assertEqualsApprox(positions[0], -1, 0.0001)
        self.assertEqualsApprox(velocities[0], 0, 0.0005)
        self.assertEqualsApprox(energy(positions, velocities), 0.5, 0.00000001)

        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 4.7124, 0.001)
        self.assertEqualsApprox(positions[0], 0, 0.0007)
        self.assertEqualsApprox(velocities[0], 1, 0.0001)
        self.assertEqualsApprox(energy(positions, velocities), 0.5, 0.00000001)

        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 6.2832, 0.001)
        self.assertEqualsApprox(positions[0], 1, 0.0001)
        self.assertEqualsApprox(velocities[0], 0, 0.0009)
        self.assertEqualsApprox(energy(positions, velocities), 0.5, 0.00000001)

        # 314.1593 = 50 * (2 * pi). With the 0.001 time step this is 314k iterations, so a good test of longer-term precision.
        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 314.1593, 0.001)
        self.assertEqualsApprox(positions[0], 1, 0.0000003)
        self.assertEqualsApprox(velocities[0], 0, 0.0008)
        self.assertEqualsApprox(energy(positions, velocities), 0.5, 0.00000002)

    def test_pendulum_2D(self):
        # Differential equation: f([x, y], [vx, vy], t) = [-x, -4*y].
        # The precise solution is:
        #   x = cos(t),
        #   y = cos(2*t),
        #   v_x = -sin(t),
        #   v_y = -2*sin(t).

        init_positions = [1, 1]
        init_velocities = [0, 0]
        calculate_accelerations_p_v_t = lambda p, v, t: [-p[0], -4*p[1]]

        # Energy = (x^2 + v_x^2 + 4*y^2 + v_y^2)/2.
        # For the precise solution, the energy of this system remains constant at 2.5.
        # Many other solving algorithm either lose or gain energy out of nowhere,
        # so it's useful to sanity test what we have here.
        energy = lambda p, v: 0.5 * (math.pow(p[0], 2) + math.pow(v[0], 2) + 4 * math.pow(p[1], 2) + math.pow(v[1], 2))

        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 0.7854, 0.001)
        self.assertEqualsApprox(positions[1], 0, 0.002)
        self.assertEqualsApprox(velocities[1], -2, 0.000002)
        self.assertEqualsApprox(energy(positions, velocities), 2.5, 0.00000001)

        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 1.5708, 0.001)
        self.assertEqualsApprox(positions[0], 0, 0.0003)
        self.assertEqualsApprox(velocities[0], -1, 0.00001)
        self.assertEqualsApprox(positions[1], -1, 0.0009)
        self.assertEqualsApprox(velocities[1], 0, 0.0009)
        self.assertEqualsApprox(energy(positions, velocities), 2.5, 0.00000001)

        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 3.1416, 0.001)
        self.assertEqualsApprox(positions[0], -1, 0.0001)
        self.assertEqualsApprox(velocities[0], 0, 0.0005)
        self.assertEqualsApprox(energy(positions, velocities), 2.5, 0.00000001)

        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 4.7124, 0.001)
        self.assertEqualsApprox(positions[0], 0, 0.0007)
        self.assertEqualsApprox(velocities[0], 1, 0.0001)
        self.assertEqualsApprox(energy(positions, velocities), 2.5, 0.00000002)

        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 6.2832, 0.001)
        self.assertEqualsApprox(positions[0], 1, 0.0001)
        self.assertEqualsApprox(velocities[0], 0, 0.0009)
        self.assertEqualsApprox(energy(positions, velocities), 2.5, 0.00000002)

        # 314.1593 = 50 * (2 * pi). With the 0.001 time step this is 314k iterations, so a good test of longer-term precision.
        positions, velocities, time = solveRK4(init_positions, init_velocities, calculate_accelerations_p_v_t, 314.1593, 0.001)
        self.assertEqualsApprox(positions[0], 1, 0.0000003)
        self.assertEqualsApprox(velocities[0], 0, 0.0008)
        self.assertEqualsApprox(positions[1], 1, 0.000002)
        self.assertEqualsApprox(velocities[1], 0, 0.003)
        self.assertEqualsApprox(energy(positions, velocities), 2.5, 0.0000009)

    def test_finish(self):
        # x(t) = 1 * t,
        # v_x(t) = 1.
        #
        # Should reach x >= 10 in 10 seconds.

        positions = [0]
        velocities = [1]
        calculate_accelerations_p_v_t = lambda p, v, t: [0]

        progress_listener_callback_p_v_t = lambda p, v, t: p[0] >= 10

        positions, velocities, time = solveRK4(positions, velocities, calculate_accelerations_p_v_t, 100, 0.001, progress_listener_callback_p_v_t)

        self.assertEqualsApprox(time, 10, 0.001)
        self.assertEqualsApprox(positions[0], 10, 0.001)

    def test_dnf(self):
        # x(t) = 1 * t,
        # v_x(t) = 1.
        #
        # Should reach x >= 10 in 10 seconds.

        positions = [0]
        velocities = [1]
        calculate_accelerations_p_v_t = lambda p, v, t: [0]

        progress_listener_callback_p_v_t = lambda p, v, t: p[0] >= 10

        positions, velocities, time = solveRK4(positions, velocities, calculate_accelerations_p_v_t, 4.2, 0.001, progress_listener_callback_p_v_t)

        self.assertEqualsApprox(time, 4.2, 0.001)
        self.assertEqualsApprox(positions[0], 4.2, 0.001)

if __name__ == '__main__':
    print("Running solver tests:")
    unittest.main()
