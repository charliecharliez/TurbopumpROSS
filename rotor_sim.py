import ross as rs
import numpy as np
import pint as pt
# import plotly just to guarantee that plots will appear in the docs
import plotly

from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"# "vscode"

# turbine operating temperature is ~750 Fahrenheit, could be higher, using 800 deg F
# https://www.specialmetals.com/documents/technical-bulletins/inconel/inconel-alloy-718.pdf
inco_718_turbine = rs.Material(name="Inconel-718", rho=8193, E = 1.77885e11, Poisson=0.271)
#print(inco_718_turbine)
#print("="*36) # takes a while

# https://asm.matweb.com/search/specificmaterial.asp?bassnum=mq304a
ss_304 = rs.Material(name="Stainless-304", rho = 8000, E = 1.93e11, Poisson=0.29);

#print(rs.Material.available_materials())
#print("="*36) # takes a while

steel = rs.Material(name="Steel", rho=7810, E=211e9, G_s=81.2e9)

# start from turbine to lox inlet
# SI units

shaft_material = ss_304;

# turbine start
shaft1 = rs.ShaftElement(n=0,
    L=0.086939,
    idl=0,
    odl=0.010099,
    material=shaft_material,
    gyroscopic=True
    );

# laby section
shaft2 = rs.ShaftElement(
    L=0.03860800,
    idl=0,
    odl=0.016002,
    idr=0,
    odr=0.018796,
    material=shaft_material,
    gyroscopic=True
    );

# LOX bearing section
shaft3 = rs.ShaftElement(
    L=0.027889,
    idl=0,
    odl=0.012,
    material=shaft_material,
    gyroscopic=True
)

# LOX impeller section
shaft4 = rs.ShaftElement(
    L=0.017071,
    idl=0,
    odl=0.009525,
    material=shaft_material,
    gyroscopic=True
)

# LOX retaining nut section
shaft4 = rs.ShaftElement(
    L=0.018489,
    idl=0,
    odl=0.006350,
    material=shaft_material,
    gyroscopic=True
)

# SI units btw
turbine = rs.DiskElement(n=0, m=0.292578, Ip = 3.68819E-4, Id=1.85449E-4, tag="Turbine");

bearing_alpha = np.deg2rad(-15);

kero_bearing1 = rs.BallBearingElement(
    n=1, n_balls=12, d_balls=5.556E-3,
    fs=0, alpha=bearing_alpha)

shaft_elements = [shaft1, shaft2, shaft3, shaft4];
disk_elements = [turbine];
bearing_elements = [kero_bearing1];

rotor = rs.Rotor(
    shaft_elements=shaft_elements,
    disk_elements=disk_elements,
    bearing_elements=bearing_elements
)

rotor.plot_rotor()