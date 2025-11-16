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

for i, v in enumerate(rotor.bearing_elements):
    print(v.tag, v.K(0))