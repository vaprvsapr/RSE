import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import math

EARTH_RADIUS = 6371
ORBIT_RADIUS = 10000
LIMITS = 15000
Z_LIMITS = 12000

ax = plt.axes(projection="3d")
ax.axes.set_xlim3d(left=-LIMITS, right=LIMITS)
ax.axes.set_ylim3d(bottom=-LIMITS, top=LIMITS)
ax.axes.set_zlim3d(bottom=-Z_LIMITS, top=Z_LIMITS)

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
print(mean_motion)
# print(inclination, right_ascension_of_the_ascending_node,
#       eccentricity, argument_of_perigee, mean_anomaly,
#       mean_motion, revolution_number_at_epoch)
# TLE reading end


# Earth model begin
# Рисуем землю
earth_coordinates = [[], [], []]

n = 18
for seconds in range(n):
    theta = math.pi / n * seconds
    for j in range(n):
        phi = 2 * math.pi / n * j

        x_visible = EARTH_RADIUS * math.sin(theta) * math.cos(phi)
        y_visible = EARTH_RADIUS * math.sin(theta) * math.sin(phi)
        z_visible = EARTH_RADIUS * math.cos(theta)

        earth_coordinates[0].append(x_visible)
        earth_coordinates[1].append(y_visible)
        earth_coordinates[2].append(z_visible)

ax.scatter(earth_coordinates[0], earth_coordinates[1], earth_coordinates[2], c='b', marker='x')

# Earth model end

print("Введите геодезические координаты точки наблюдени.")
# Рисуем положение лаборатории
laboratory_geo_coordinates = [(-float(input()) + 90) / 180 * math.pi, float(input()) / 180 * math.pi]
laboratory_coordinates = [EARTH_RADIUS * math.sin(laboratory_geo_coordinates[0]) *
                          math.cos(laboratory_geo_coordinates[1]),
                          EARTH_RADIUS * math.sin(laboratory_geo_coordinates[0]) *
                          math.sin(laboratory_geo_coordinates[1]),
                          EARTH_RADIUS * math.cos(laboratory_geo_coordinates[0])]

# Рисуем геодезический нуль
zero_geo_coordinates = [math.pi / 2, 0]
zero_coordinates = [EARTH_RADIUS * math.sin(zero_geo_coordinates[0]) *
                    math.cos(zero_geo_coordinates[1]),
                    EARTH_RADIUS * math.sin(zero_geo_coordinates[0]) *
                    math.sin(zero_geo_coordinates[1]),
                    EARTH_RADIUS * math.cos(zero_geo_coordinates[0])]

# Считаем промежужток времени, в который будем производить наблюдения. Минимальная еденица времени - 1 секунда.
# Время отсчитываем в минутах, с начала времен. Т.е. с Рождества Христова.

# Число дней в различные месяцы (есть погрешность)
# Отсчет времени ведется с 00:00 1 января 2000 года.
MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
YEAR_SUM = 365
MONTH_0 = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
YEAR_SUM_0 = 366


def GetTime(inp):
    days = int(inp[3])

    if inp[5] != 0:
        for year in range(0, int(inp[5])):
            if year % 4 == 0:
                days += YEAR_SUM_0
            elif year % 4 != 0:
                days += YEAR_SUM

    if inp[4] != 0:
        for month in range(0, int(inp[4]) - 1):
            if int(inp[5]) % 4 == 0:
                days += MONTH_0[month]
            elif int(inp[5]) % 4 != 0:
                days += MONTH_0[month]

    time = int(inp[2]) + int(inp[1]) * 60 + int(inp[0]) * 3600 + int(days) * 24 * 3600
    return time


def GetX(anomaly):
    return ORBIT_RADIUS * \
           (math.cos(right_ascension_of_the_ascending_node) * math.cos(anomaly) -
            math.sin(right_ascension_of_the_ascending_node) * math.sin(anomaly) *
            math.cos(inclination))


def GetY(anomaly):
    return ORBIT_RADIUS * \
           (math.sin(right_ascension_of_the_ascending_node) * math.cos(anomaly) +
            math.cos(right_ascension_of_the_ascending_node) * math.sin(anomaly) *
            math.cos(inclination))


def GetZ(anomaly):
    return ORBIT_RADIUS * math.sin(anomaly) * math.sin(inclination)


def GetShipCoordinates(anomaly):
    return [GetX(anomaly), GetY(anomaly), GetZ(anomaly)]


def IsShipObservable(_laboratory_coordinates, _ship_coordinates):
    lab_x = _laboratory_coordinates[0]
    lab_y = _laboratory_coordinates[1]
    lab_z = _laboratory_coordinates[2]

    ship_x = _ship_coordinates[0] - lab_x
    ship_y = _ship_coordinates[1] - lab_y
    ship_z = _ship_coordinates[2] - lab_z

    lab_abs = math.sqrt(lab_x**2 + lab_y**2 + lab_z**2)
    ship_abs = math.sqrt(ship_x**2 + ship_y**2 + ship_z**2)

    lab_x_norm = lab_x / lab_abs
    lab_y_norm = lab_y / lab_abs
    lab_z_norm = lab_z / lab_abs

    ship_x_norm = ship_x / ship_abs
    ship_y_norm = ship_y / ship_abs
    ship_z_norm = ship_z / ship_abs

    delta_x_norm = lab_x_norm - ship_x_norm
    delta_y_norm = lab_y_norm - ship_y_norm
    delta_z_norm = lab_z_norm - ship_z_norm

    delta_abs_norm = math.sqrt(delta_x_norm**2 + delta_y_norm**2 + delta_z_norm**2)

    if delta_abs_norm < math.sqrt(2):
        return True
    else:
        return False



# print("Введите период наблюдения в формате HH:MM:SS:DD:MM:YY через 'Enter'. Начало и конец.")
# begin_input = input().split(':')
# begin_time = GetTime(begin_input)
#
# end_input = input().split(':')
# end_time = GetTime(end_input)


ax.scatter(laboratory_coordinates[0], laboratory_coordinates[1], laboratory_coordinates[2], c='r', marker='o')
ax.scatter(zero_coordinates[0], zero_coordinates[1], zero_coordinates[2], c='g', marker='o')




# Scattering ship trajectory end
# plt.xlim((-LIMITS, LIMITS))
# plt.ylim((-LIMITS, LIMITS))

epoch_seconds = int(24 * 3600 * epoch)
print(epoch_seconds)

print("Введите день в формате __._____ с 1 января 2022 года - начало")
epoch_second_begin = int(24 * 3600 * float(input()))
print("Введите день в формате __._____ с 1 января 2022 года - конец")
epoch_second_end = int(24 * 3600 * float(input()))


# Scattering ship trajectory begin
x_visible, y_visible, z_visible = [], [], []
x_invisible, y_invisible, z_invisible = [], [], []
is_ship_observable = False

for seconds in range(epoch_seconds, epoch_second_end):
    if seconds > epoch_second_begin:
        _x = GetX(delta_anomaly_per_second * seconds)
        _y = GetX(delta_anomaly_per_second * seconds)
        _z = GetZ(delta_anomaly_per_second * seconds)

        if IsShipObservable(laboratory_coordinates, [_x, _y, _z]):
            x_visible.append(_x)
            y_visible.append(_y)
            z_visible.append(_z)
            if not is_ship_observable:
                is_ship_observable = True
                print("Now ship is observable. Time:", int(seconds / 24 / 60 / 60),
                      int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600),
                      int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) - int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600) * 3600) / 60)
        else:
            x_invisible.append(_x)
            y_invisible.append(_y)
            z_invisible.append(_z)
            if is_ship_observable:
                is_ship_observable = False
                print("Now ship is not observable. Time:", int(seconds / 24 / 60 / 60),
                      int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600),
                      int((seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) - int(
                          (seconds - int(seconds / 24 / 60 / 60) * 24 * 3600) / 3600) * 3600) / 60)

ax.scatter(x_visible, y_visible, z_visible, c='g', marker=".")
ax.scatter(x_invisible, y_invisible, z_invisible, c='y', marker=".")

plt.show()
