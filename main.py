import matplotlib.pyplot as plt
import math

EARTH_RADIUS = 6371
LIMITS = 15000
Z_LIMIT = 12000
EARTH_ROTATION_PER_SECOND = 2 * math.pi / 24 / 3600
PARAM_A = 7000

# setting matplotlib begin
ax = plt.axes(projection="3d")
ax.axes.set_xlim3d(left=-LIMITS, right=LIMITS)
ax.axes.set_ylim3d(bottom=-LIMITS, top=LIMITS)
ax.axes.set_zlim3d(bottom=-Z_LIMIT, top=Z_LIMIT)
# setting matplotlib end

# TLE reading begin
with open("TLE.txt") as file:
    line_1 = file.readline().split()
    line_2 = file.readline().split()

epoch_year = float(line_1[3][0:2])
epoch = float(line_1[3][2:])

inclination = float(line_2[2])
right_ascension_of_the_ascending_node = float(line_2[3])
eccentricity = float("0." + line_2[4])
argument_of_perigee = float(line_2[5])
mean_anomaly = float(line_2[6])
mean_motion = float(line_2[7][0:11])
revolution_number_at_epoch = float(line_2[7][11:-1])
delta_anomaly_per_second = mean_motion * math.pi * 2 / 24 / 60 / 60
# TLE reading end
print(inclination, right_ascension_of_the_ascending_node,
      eccentricity, argument_of_perigee, mean_anomaly,
      mean_motion, revolution_number_at_epoch)

# Drawing Earth and laboratory begin
zero_geo_coordinates = [math.pi / 2, 0]
zero_coordinates = [EARTH_RADIUS * math.sin(zero_geo_coordinates[0]) *
                    math.cos(zero_geo_coordinates[1]),
                    EARTH_RADIUS * math.sin(zero_geo_coordinates[0]) *
                    math.sin(zero_geo_coordinates[1]),
                    EARTH_RADIUS * math.cos(zero_geo_coordinates[0])]

ax.scatter(zero_coordinates[0], zero_coordinates[1], zero_coordinates[2], c='g', marker='o')

earth_coordinates = [[], [], []]
n = 18
for seconds in range(n):
    theta = math.pi / n * seconds
    for j in range(n):
        phi = 2 * math.pi / n * j

        x_drawing_earth = EARTH_RADIUS * math.sin(theta) * math.cos(phi)
        y_drawing_earth = EARTH_RADIUS * math.sin(theta) * math.sin(phi)
        z_drawing_earth = EARTH_RADIUS * math.cos(theta)

        if [x_drawing_earth, y_drawing_earth, z_drawing_earth] != zero_coordinates:
            earth_coordinates[0].append(x_drawing_earth)
            earth_coordinates[1].append(y_drawing_earth)
            earth_coordinates[2].append(z_drawing_earth)

ax.scatter(earth_coordinates[0], earth_coordinates[1], earth_coordinates[2], c='b', marker='x')

print("Введите геодезические координаты точки наблюдени.")
# Рисуем положение лаборатории
laboratory_geo_coordinates = [(-float(input()) + 90) / 180 * math.pi, float(input()) / 180 * math.pi]
laboratory_coordinates = [EARTH_RADIUS * math.sin(laboratory_geo_coordinates[0]) *
                          math.cos(laboratory_geo_coordinates[1]),
                          EARTH_RADIUS * math.sin(laboratory_geo_coordinates[0]) *
                          math.sin(laboratory_geo_coordinates[1]),
                          EARTH_RADIUS * math.cos(laboratory_geo_coordinates[0])]

ax.scatter(laboratory_coordinates[0], laboratory_coordinates[1], laboratory_coordinates[2], c='r', marker='o')


# Drawing Earth and laboratory end

# Some important functions begin
def GetX(true_anomaly):
    p = PARAM_A * (1 - eccentricity * eccentricity)
    r = p / (1 + eccentricity * math.cos(true_anomaly))
    u = argument_of_perigee + true_anomaly
    x_getting = r * (math.cos(right_ascension_of_the_ascending_node) * math.cos(u) -
                     math.sin(right_ascension_of_the_ascending_node) * math.sin(u) * math.cos(inclination))
    return x_getting


def GetY(true_anomaly):
    p = PARAM_A * (1 - eccentricity * eccentricity)
    r = p / (1 + eccentricity * math.cos(true_anomaly))
    u = argument_of_perigee + true_anomaly
    y_getting = r * (math.sin(right_ascension_of_the_ascending_node) * math.cos(u) +
                     math.cos(right_ascension_of_the_ascending_node) * math.sin(u) * math.cos(inclination))
    return y_getting


def GetZ(true_anomaly):
    p = PARAM_A * (1 - eccentricity * eccentricity)
    r = p / (1 + eccentricity * math.cos(true_anomaly))
    u = argument_of_perigee + true_anomaly
    z_getting = r * math.sin(u) * math.sin(inclination)
    return z_getting


def IsShipObservable(_laboratory_coordinates, _ship_coordinates):
    lab_x = _laboratory_coordinates[0]
    lab_y = _laboratory_coordinates[1]
    lab_z = _laboratory_coordinates[2]

    ship_x = _ship_coordinates[0] - lab_x
    ship_y = _ship_coordinates[1] - lab_y
    ship_z = _ship_coordinates[2] - lab_z

    lab_abs = math.sqrt(lab_x ** 2 + lab_y ** 2 + lab_z ** 2)
    ship_abs = math.sqrt(ship_x ** 2 + ship_y ** 2 + ship_z ** 2)

    lab_x_norm = lab_x / lab_abs
    lab_y_norm = lab_y / lab_abs
    lab_z_norm = lab_z / lab_abs

    ship_x_norm = ship_x / ship_abs
    ship_y_norm = ship_y / ship_abs
    ship_z_norm = ship_z / ship_abs

    delta_x_norm = lab_x_norm - ship_x_norm
    delta_y_norm = lab_y_norm - ship_y_norm
    delta_z_norm = lab_z_norm - ship_z_norm

    delta_abs_norm = math.sqrt(delta_x_norm ** 2 + delta_y_norm ** 2 + delta_z_norm ** 2)

    if delta_abs_norm < math.sqrt(2):
        return True
    else:
        return False


# Some important functions end


# Drawing ship trajectory begin
epoch_seconds = int(24 * 3600 * epoch)

print("Введите день в формате __._____ с 1 января 2022 года - начало")
epoch_second_begin = int(24 * 3600 * float(input()))
print("Введите день в формате __._____ с 1 января 2022 года - конец")
epoch_second_end = int(24 * 3600 * float(input()))

x_ship_visible, y_ship_visible, z_ship_visible = [], [], []
x_ship_invisible, y_ship_invisible, z_ship_invisible = [], [], []
is_ship_observable = False

for seconds in range(epoch_seconds, epoch_second_end):

    right_ascension_of_the_ascending_node += EARTH_ROTATION_PER_SECOND

    if seconds > epoch_second_begin:
        local_time = delta_anomaly_per_second * seconds
        x_drawing_trajectory = GetX(local_time)
        y_drawing_trajectory = GetY(local_time)
        z_drawing_trajectory = GetZ(local_time)

        if IsShipObservable(laboratory_coordinates, [x_drawing_trajectory, y_drawing_trajectory, z_drawing_trajectory]):
            if seconds % 10 == 0:
                x_ship_visible.append(x_drawing_trajectory)
                y_ship_visible.append(y_drawing_trajectory)
                z_ship_visible.append(z_drawing_trajectory)

            if not is_ship_observable:
                is_ship_observable = True
                print("Now ship is observable. Time:", int(seconds / 24 / 60 / 60),
                      int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600),
                      int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) -
                          int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600) * 3600) / 60)
        else:
            if seconds % 10 == 0:
                x_ship_invisible.append(x_drawing_trajectory)
                y_ship_invisible.append(y_drawing_trajectory)
                z_ship_invisible.append(z_drawing_trajectory)

            if is_ship_observable:
                is_ship_observable = False
                print("Now ship is not observable. Time:", int(seconds / 24 / 60 / 60),
                      int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600),
                      int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) -
                          int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600) * 3600) / 60)

ax.scatter(x_ship_visible, y_ship_visible, z_ship_visible, c='g', marker=".")
ax.scatter(x_ship_invisible, y_ship_invisible, z_ship_invisible, c='y', marker=".", s=1)
# Drawing ship trajectory end

plt.show()
