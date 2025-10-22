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

L = [0.086939, 0.027889, 0.017071, 0.018489]
idl = [0] * len(L)
odl = [0.010099, 0.012, 0.009525, 0.006350]

laby_conical_shaft = rs.ShaftElement(
    L=0.03860800,
    idl=0,
    odl=0.016002,
    idr=0,
    odr=0.018796,
    material=shaft_material,
    gyroscopic=True,
    shear_effects=True,
    rotary_inertia=True
    );

shaft_elements = [
    rs.ShaftElement(
        L = L[i],
        idl=idl[i],
        odl=odl[i],
        material=shaft_material,
        gyroscopic=True,
        shear_effects=True,
        rotary_inertia=True
    )
    for i in range(len(L))
];

shaft_elements.insert(1, laby_conical_shaft)

simple_shaft = rs.Rotor(shaft_elements=shaft_elements);

insert_nodes = [
    0.00381125, # turbine
    0.00635125, # rotor sleeve start
    0.01656586 + 0.01/2, # kero bearing 1
    0.01656586 + 0.01 * 3/2, # kero bearing 2
]

full_shaft = simple_shaft.add_nodes(insert_nodes)

# SI units btw
turbine = rs.DiskElement(
    n=1,
    m=0.292578,
    Ip = 3.68819E-4,
    Id=1.85449E-4,
    tag="Turbine"
    );

#TODO: find out how positive and negative angle affect simulation
bearing_alpha = np.deg2rad(-15);
# bearings are modeled using their centers, not where they start
kero_bearing1 = rs.BallBearingElement(
    n=3, n_balls=12, d_balls=5.556E-3,
    fs=0, alpha=bearing_alpha)

kero_bearing2 = rs.BallBearingElement(
    n=4, n_balls=12, d_balls=5.556E-3,
    fs=0, alpha=bearing_alpha)

disk_elements = [turbine];
bearing_elements = [kero_bearing1, kero_bearing2];
rotor_model = rs.Rotor(
    shaft_elements=full_shaft.shaft_elements,
    disk_elements=disk_elements,
    bearing_elements=bearing_elements
    )

rotor_model.plot_rotor()
#print(rs.__version__)