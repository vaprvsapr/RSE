import matplotlib.pyplot as plt
import math

EARTH_RADIUS = 6371
LIMITS = 15000
Z_LIMIT = 12000
EARTH_ROTATION_PER_SECOND = 2 * math.pi / 24 / 3600
PARAM_A = 7228

# setting matplotlib begin
plt.figure(1)
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
inclination = float(line_2[2]) * math.pi / 180
right_ascension_of_the_ascending_node = float(line_2[3]) * math.pi / 180
eccentricity = float("0." + line_2[4])
argument_of_perigee = float(line_2[5]) * math.pi / 180
mean_anomaly = float(line_2[6])
mean_motion = float(line_2[7][0:11])
revolution_number_at_epoch = float(line_2[7][11:-1])
delta_anomaly_per_second = mean_motion * math.pi * 2 / 24 / 60 / 60
# TLE reading end

# Controls reading begin
with open("controls.txt") as file:
    latitude = file.readline()
    longitude = file.readline()
    begin = file.readline()
    end = file.readline()
# Controls reading end

# Drawing Earth and laboratory begin
# Рисуем геодезический нуль
zero_geo_coordinates = [math.pi / 2, 0]
zero_coordinates = [EARTH_RADIUS * math.sin(zero_geo_coordinates[0]) *
                    math.cos(zero_geo_coordinates[1]),
                    EARTH_RADIUS * math.sin(zero_geo_coordinates[0]) *
                    math.sin(zero_geo_coordinates[1]),
                    EARTH_RADIUS * math.cos(zero_geo_coordinates[0])]

ax.scatter(zero_coordinates[0], zero_coordinates[1], zero_coordinates[2], c='g', marker='o')

# Рисуем лабораторию
laboratory_geo_coordinates = [(-float(latitude) + 90) / 180 * math.pi,
                              float(longitude) / 180 * math.pi]
laboratory_coordinates = [EARTH_RADIUS * math.sin(laboratory_geo_coordinates[0]) *
                          math.cos(laboratory_geo_coordinates[1]),
                          EARTH_RADIUS * math.sin(laboratory_geo_coordinates[0]) *
                          math.sin(laboratory_geo_coordinates[1]),
                          EARTH_RADIUS * math.cos(laboratory_geo_coordinates[0])]

ax.scatter(laboratory_coordinates[0], laboratory_coordinates[1], laboratory_coordinates[2], c='r', marker='o')

# Рисуем Землю
earth_coordinates = [[], [], []]
n = 18
for seconds_ in range(n):
    theta = math.pi / n * seconds_
    for j in range(n):
        phi = 2 * math.pi / n * j

        x_drawing_earth = EARTH_RADIUS * math.sin(theta) * math.cos(phi)
        y_drawing_earth = EARTH_RADIUS * math.sin(theta) * math.sin(phi)
        z_drawing_earth = EARTH_RADIUS * math.cos(theta)

        if [x_drawing_earth, y_drawing_earth, z_drawing_earth] != zero_coordinates and \
                [x_drawing_earth, y_drawing_earth, z_drawing_earth] != laboratory_coordinates:
            earth_coordinates[0].append(x_drawing_earth)
            earth_coordinates[1].append(y_drawing_earth)
            earth_coordinates[2].append(z_drawing_earth)

ax.scatter(earth_coordinates[0], earth_coordinates[1], earth_coordinates[2], c='b', marker='x')
# Drawing Earth and laboratory end


# Some important functions begin
# Функции, возвращающие положение КА в зависимости от параматров орбиты
def GetX(true_anomaly, right_ascension_of_the_ascending_node_local):
    p = PARAM_A * (1 - eccentricity * eccentricity)
    r = p / (1 + eccentricity * math.cos(true_anomaly))
    u = argument_of_perigee + true_anomaly
    x_getting = r * (math.cos(right_ascension_of_the_ascending_node_local) * math.cos(u) -
                     math.sin(right_ascension_of_the_ascending_node_local) * math.sin(u) * math.cos(inclination))
    return x_getting


def GetY(true_anomaly, right_ascension_of_the_ascending_node_local):
    p = PARAM_A * (1 - eccentricity * eccentricity)
    r = p / (1 + eccentricity * math.cos(true_anomaly))
    u = argument_of_perigee + true_anomaly
    y_getting = r * (math.sin(right_ascension_of_the_ascending_node_local) * math.cos(u) +
                     math.cos(right_ascension_of_the_ascending_node_local) * math.sin(u) * math.cos(inclination))
    return y_getting


def GetZ(true_anomaly):
    p = PARAM_A * (1 - eccentricity * eccentricity)
    r = p / (1 + eccentricity * math.cos(true_anomaly))
    u = argument_of_perigee + true_anomaly
    z_getting = r * math.sin(u) * math.sin(inclination)
    return z_getting


# Функция, отвечающая на вопрос: Виден ли в данный момент КА из лаборатории
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


def AbsVec(vec):
    return math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)


def ScalarMultiplication(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]


def AngleBetweenTwoVectors(vec1, vec2):
    cos_phi = ScalarMultiplication(vec1, vec2) / AbsVec(vec1) / AbsVec(vec2)
    return math.acos(cos_phi)


def Projection(a, b):
    return [i * ScalarMultiplication(a, b) / AbsVec(b) / AbsVec(b) for i in b]


_z = [0, 0, 1]
angle_z_lab = AngleBetweenTwoVectors(_z, laboratory_coordinates)
Z = [0, 0, EARTH_RADIUS / math.cos(angle_z_lab)]
Z_minus_lab = [-laboratory_coordinates[0], -laboratory_coordinates[1], Z[2] - laboratory_coordinates[2]]

norm_norm = [(laboratory_coordinates[1] * _z[2] - _z[1] * laboratory_coordinates[2]),
             -(laboratory_coordinates[0] * _z[2] - _z[0] * laboratory_coordinates[2]),
             (laboratory_coordinates[0] * _z[1] - _z[0] * laboratory_coordinates[1])]


def IsAbove(x, y, z):
    return norm_norm[0] * (x - laboratory_coordinates[0]) + \
           norm_norm[1] * (y - laboratory_coordinates[1]) + \
           norm_norm[2] * (z - laboratory_coordinates[2])


def ParsePeriod(inp):
    inp = inp.split(' ')
    t1 = inp[0].split(':')
    t2 = inp[1].split(':')
    days = int(t2[0]) - 1
    for m in range(0, int(t2[1])):
        days += MONTHS[m]
    sec = int(t1[0]) * 3600 + int(t1[1]) * 60 + int(t1[2]) + days * 24 * 3600
    return sec
# Some important functions end


# Drawing ship trajectory begin
epoch_seconds = int(24 * 3600 * epoch)

MONTHS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# Временные промежутки достаём из файла controls.txt
epoch_second_begin = ParsePeriod(begin)
epoch_second_end = ParsePeriod(end)


# Главная функия, рисующая траектории КА, и выводящая временные промежутки, когда КА наблюдается
def Calculate():
    # Создаем два массива для хранения координат КА. Один для видимых, другой для невидимых.
    x_ship_visible, y_ship_visible, z_ship_visible = [], [], []
    x_ship_invisible, y_ship_invisible, z_ship_invisible = [], [], []
    angle_ship_visible = []
    direction_ship_visible = []
    is_ship_observable = False
    right_ascension_of_the_ascending_node_local = right_ascension_of_the_ascending_node

    for seconds in range(epoch_seconds, epoch_second_end):

        right_ascension_of_the_ascending_node_local += EARTH_ROTATION_PER_SECOND

        if seconds > epoch_second_begin:
            local_time = delta_anomaly_per_second * seconds
            x_drawing_trajectory = GetX(local_time, right_ascension_of_the_ascending_node_local)
            y_drawing_trajectory = GetY(local_time, right_ascension_of_the_ascending_node_local)
            z_drawing_trajectory = GetZ(local_time)

            if IsShipObservable(laboratory_coordinates,
                                [x_drawing_trajectory, y_drawing_trajectory, z_drawing_trajectory]):
                if seconds % 20 == 0:
                    x_ship_visible.append(x_drawing_trajectory)
                    y_ship_visible.append(y_drawing_trajectory)
                    z_ship_visible.append(z_drawing_trajectory)

                    ship_minus_lab = [x_drawing_trajectory - laboratory_coordinates[0],
                                      y_drawing_trajectory - laboratory_coordinates[1],
                                      z_drawing_trajectory - laboratory_coordinates[2]]

                    elevation = AngleBetweenTwoVectors(ship_minus_lab, laboratory_coordinates) / math.pi * 180
                    angle_ship_visible.append(elevation)

                    ship_proj_lab = Projection([x_drawing_trajectory, y_drawing_trajectory, z_drawing_trajectory],
                                               laboratory_coordinates)
                    ship_proj_perpendicular_lab = [x_drawing_trajectory - ship_proj_lab[0],
                                                   y_drawing_trajectory - ship_proj_lab[1],
                                                   z_drawing_trajectory - ship_proj_lab[2]]

                    if IsAbove(x_drawing_trajectory, y_drawing_trajectory, z_drawing_trajectory) < 0:
                        direction_ship_visible.append(AngleBetweenTwoVectors(Z_minus_lab, ship_proj_perpendicular_lab))
                    else:
                        direction_ship_visible.append(
                            2 * math.pi - AngleBetweenTwoVectors(Z_minus_lab, ship_proj_perpendicular_lab))

                if not is_ship_observable:
                    is_ship_observable = True

                    day = int(seconds / 24 / 60 / 60)
                    hour = int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600)
                    minute = int(int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) -
                                     int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600) * 3600) / 60)
                    second = seconds - day * 24 * 3600 - hour * 3600 - minute * 60
                    print("Now ship is observable.     Time:", day, end=' ')
                    if hour > 9:
                        print(str(hour) + ":", end='')
                    else:
                        print("0" + str(hour) + ":", end='')
                    if minute > 9:
                        print(str(minute) + ":", end='')
                    else:
                        print("0" + str(minute) + ":", end='')
                    if second > 9:
                        print(str(second))
                    else:
                        print("0" + str(second))
            else:
                if seconds % 30 == 0:
                    x_ship_invisible.append(x_drawing_trajectory)
                    y_ship_invisible.append(y_drawing_trajectory)
                    z_ship_invisible.append(z_drawing_trajectory)

                if is_ship_observable:
                    is_ship_observable = False

                    day = int(seconds / 24 / 60 / 60)
                    hour = int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600)
                    minute = int(int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) -
                                     int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600) * 3600) / 60)
                    second = seconds - day * 24 * 3600 - hour * 3600 - minute * 60
                    print("Now ship is not observable. Time:", day, end=" ")
                    if hour > 9:
                        print(str(hour) + ":", end='')
                    else:
                        print("0" + str(hour) + ":", end='')
                    if minute > 9:
                        print(str(minute) + ":", end='')
                    else:
                        print("0" + str(minute) + ":", end='')
                    if second > 9:
                        print(str(second))
                    else:
                        print("0" + str(second))

    ax.scatter(x_ship_visible, y_ship_visible, z_ship_visible, c='g', marker=".")
    ax.scatter(x_ship_invisible, y_ship_invisible, z_ship_invisible, c='y', marker=".", s=1)

    plt.suptitle("Satellite trajectory.")
    plt.figure(2)
    pp = plt.subplot(111, projection='polar')
    pp.set_theta_zero_location('N')
    pp.plot(direction_ship_visible, angle_ship_visible, marker='.', linestyle='None')
    pp.grid(True)


Calculate()

plt.title("Dependence of elevation angle on the direction.")
plt.show()
# Drawing ship trajectory end
