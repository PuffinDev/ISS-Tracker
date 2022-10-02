from ursina import *
from sgp4.api import Satrec
from sgp4.conveniences import jday_datetime
from datetime import datetime, timedelta
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import TEME, CartesianDifferential, CartesianRepresentation, ITRS
from utils import latlon_to_coords
from functools import partial
from skyfield.api import EarthSatellite, load, Topos, utc
import requests
import json

TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544"

SCALAR = 1/12713

def calculate_pos(s, t):
    satellite = Satrec.twoline2rv(s, t)
    t = Time(datetime.utcnow().isoformat(), format='isot')
    e, r, v = satellite.sgp4(t.jd1, t.jd2)
    return r, v, t

resp = requests.get(TLE_URL)
if resp.status_code == 200:
    tle = resp.text
else:
    print("Failed to retrieve TLE data.")

N, S, T = tle.split("\n")[:3]

with open("resources/ground_stations.json") as f:
    ground_stations = json.load(f)
 
app = Ursina()

earth = Entity(model='sphere', texture='resources/earthmap4k.jpg', rotation=(0, 90, 0))
iss = Entity(model='resources/ISS_stationary.glb',  scale=(0.0005, 0.0005, 0.0005))

for station in ground_stations:
    station_entity = Entity(model='sphere', color=color.red, scale=(0.005, 0.005, 0.005), position=latlon_to_coords(*station["coords"]))
    station_entity.collider = SphereCollider(station_entity, center=station_entity.position, radius=0.5)
    station_entity.on_click = partial(print, "Selected: " + station['name'])

x_ref = Entity(position=(10, 0, 0))

camera = EditorCamera()

window.borderless = False
window.fps_counter.enabled = True
window.exit_button.enabled = False

i = 10
def update():
    global i
    r, v, t = calculate_pos(S, T)

    r = CartesianRepresentation(r*u.km)
    v = CartesianDifferential(v*u.km/u.s)
    teme = TEME(r.with_differentials(v), obstime=t)

    itrs = teme.transform_to(ITRS(obstime=t))
    location = itrs.earth_location

    z, x, y = location.x.value, location.y.value, location.z.value

    iss.position = (x*SCALAR, y*SCALAR, z*SCALAR*-1)
    iss.look_at(x_ref)

    i += time.dt

    if i >= 10:
        now = datetime.utcnow()
        ts = load.timescale()
        skyfield_time = ts.utc(now.replace(tzinfo=utc))
        skyfield_sat = EarthSatellite(S, T, N, ts)

        for station in ground_stations:
            lat, lon = station["coords"]

            lat = str(-lat) + " S" if lat < 0.0 else str(lat) + " N" 
            lon = str(-lon) + " W" if lon < 0.0 else str(lon) + " E"

            ground_station = Topos(lat, lon)
            difference = skyfield_sat - ground_station
            topocentric = difference.at(skyfield_time)
            alt, az, distance = topocentric.altaz()

            if alt.degrees >= 0:
                print("Line of sight with ground station in", station["name"])
                print(round(alt.degrees, 3), " degrees above the horizon")
                print("\n")
        
        i = 0

app.run()
