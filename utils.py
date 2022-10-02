from math import radians, tan, atan, cos, sin
import numpy as np

KM = 1/12742
RAD = 0.5

# def latlon_to_coords(lat, lon, alt):
#     lat = radians(lat-90)
#     lon = radians(lon)
#     alt = alt*KM

#     f  = 0
#     ls = atan((1 - f)**2 * tan(lat))

#     x = RAD * cos(ls) * cos(lon) + alt * cos(lat) * cos(lon)
#     y = RAD * cos(ls) * sin(lon) + alt * cos(lat) * sin(lon)
#     z = RAD * sin(ls) + alt * sin(lat)

#     return x, y, z

def latlon_to_coords(lat, lon):
    lon -= 90
    lat, lon = np.deg2rad(lat), np.deg2rad(lon)
    x = RAD * np.cos(lat) * np.cos(lon)
    z = RAD * np.cos(lat) * np.sin(lon)
    y = RAD * np.sin(lat)
    return x, y, z

