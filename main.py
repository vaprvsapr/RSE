import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import math

EARTH_RADIUS = 6371


ax = plt.axes(projection="3d")

# Earth model begin
# Рисуем землю
earth_coordinates = [[], [], []]

n = 18
for i in range(n):
    theta = math.pi / n * i
    for j in range(n):
        phi = 2 * math.pi / n * j

        x = EARTH_RADIUS * math.sin(theta) * math.cos(phi)
        y = EARTH_RADIUS * math.sin(theta) * math.sin(phi)
        z = EARTH_RADIUS * math.cos(theta)

        earth_coordinates[0].append(x)
        earth_coordinates[1].append(y)
        earth_coordinates[2].append(z)

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

print("Введите период наблюдения в формате HH:MM:SS:DD:MM:YY через 'Enter'. Начало и конец.")
begin_input = input().split(':')
begin_days = int(begin_input[3])

if begin_input[5] != 0:
    for year in range(0, int(begin_input[5])):
        if year % 4 == 0:
            begin_days += YEAR_SUM_0
        elif year % 4 != 0:
            begin_days += YEAR_SUM

if begin_input[4] != 0:
    for month in range(0, int(begin_input[4])):
        if begin_input[5] % 4 == 0:
            begin_days += MONTH_0[month]
        elif begin_input[5] % 4 != 0:
            begin_days += MONTH_0

print(begin_days)


begin_time = begin_input[0] * 3600 + begin_input[1] * 60 + begin_input[2] + begin_input[3] * 3600 * 24


# end_input = input().split(':')


ax.scatter(laboratory_coordinates[0], laboratory_coordinates[1], laboratory_coordinates[2], c='r', marker='o')
ax.scatter(zero_coordinates[0], zero_coordinates[1], zero_coordinates[2], c='g', marker='o')

plt.show()
