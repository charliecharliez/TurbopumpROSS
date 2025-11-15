import ross as rs
import numpy as np
import math
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"# "vscode"

from ross.units import Q_

rotor = rs.Rotor.load("MODEL.json")
n = 0
n_balls= 10
d_balls = 0.005
alpha = 15 * np.pi / 180
fs = 1000
tag = "ballbearing"
bearing = rs.BallBearingElement(n=n, n_balls=n_balls, d_balls=d_balls,
                             fs=fs, alpha=alpha, tag=tag)
#print(bearing.K(0))
#print(bearing.K(50000 / 60))
print(rotor.bearing_elements[0].K(0))
print(rotor.bearing_elements[0].K(5000))