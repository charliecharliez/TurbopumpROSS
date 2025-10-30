import ross as rs
import numpy as np
import pint as pt
from ross.units import Q_
# import plotly just to guarantee that plots will appear in the docs
import plotly
from IPython.display import display

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
ss_A286 = rs.Material(name="Stainless-A286", rho=7944.1327, E=1.999e11, Poisson=0.31)

#____________________PRELIMINARY SHAFT______________________
# start from turbine to lox inlet
# SI units

shaft_material = ss_A286;

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

#_________________________ PARTITION SHAFT________________________
insert_nodes = [
    0.00222462, # sleeve nut
    0.00381125, # turbine
    0.01656586 + 0.01/2, # kero bearing 1
    0.0212, #rotor sleeve CoM
    0.01656586 + 0.01 * 3/2, # kero bearing 2,
    0.040674, #kero nut CoM,
    0.06824030, #kero inducer*?
    0.08195875, #kero impeller

    0.13095214, #LOX bearing 1,
    0.13095214 + 0.01, # LOX bearing 2
    0.14871202, # LOX bearing NUT
    0.15892092, # LOX impeller
    0.17353779, # LOX inducer
    0.18690132, # LOX retaining nut
]

full_shaft = simple_shaft.add_nodes(insert_nodes)
shaft_elements = full_shaft.shaft_elements

#______________________________ DISK ELEMENTS _____________________________
# SI units btw

sleeve_nut = rs.DiskElement(
    n=1,
    m=1.3618E-2,
    Id=2.0408E-2,
    Ip=1.5499E-2,
    tag="Sleeve Nut",
    scale_factor=0.25
)

turbine = rs.DiskElement(
    n=2,
    m=0.292578,
    Ip = 3.68819E-4,
    Id=1.85449E-4,
    tag="Turbine",
    scale_factor=2.2,
    );

rotor_sleeve = rs.DiskElement(
    n=4,
    m=0.0903,
    Ip=1.1E-5,
    Id=2.4E-5,
    tag="Rotor Sleeve",
    scale_factor=0.5,
);

kero_nut = rs.DiskElement(
    n=6,
    m=0.024601,
    Ip=2.96E-6,
    Id=1.65E-6,
    tag="Kero Bearing Nut",
    scale_factor=0.5
)

kero_inducer = rs.DiskElement(
    n=7,
    m=2.2054E-2,
    Ip = 1.3141E-6,
    Id = ((1.1675 + 1.8117)/2)*1E-6,
    tag = "Kero Inducer",
    scale_factor=0.75
);

kero_impeller = rs.DiskElement(
    n=8,
    m=6.6809E-2,
    Ip=1.9328E-5,
    Id=1.02705E-5,
    tag="Kero Impeller",
    scale_factor=1.25,
    color="Green"
)

lox_bearing_nut = rs.DiskElement(
    n=13,
    m=1.0346E-2,
    Ip=3.4483E-7,
    Id=(6.9851 + 4.2343)/2*1E-7,
    tag="LOX Bearing Nut",
    scale_factor=0.5
)

lox_impeller = rs.DiskElement(
    n=15,
    m=5.2961E-2,
    Ip=9.9799E-6,
    Id=5.6119E-6,
    tag="LOX Impeller",
    scale_factor=1.25,
    color="Cyan"
)

lox_inducer = rs.DiskElement(
    n=17,
    m=1.8831E-2,
    Ip=1.2175E-6,
    Id=(9.1255 + 8.2006)/2*1E-7,
    tag="LOX Inducer",
    scale_factor=0.75,
)

retaining_nut = rs.DiskElement(
    n=18,
    m=4.491E-3,
    Ip=7.134E-8,
    Id=6.8793E-8,
    tag="Retaining Nut",
    scale_factor=0.25,
)

disk_elements = [
    sleeve_nut,
    turbine,
    rotor_sleeve,
    kero_nut,
    kero_inducer,
    kero_impeller,
    lox_bearing_nut,
    lox_impeller,
    lox_inducer,
    retaining_nut
    ];

#_____________________ BEARING ELEMENTS _____________________
#TODO: find out how positive and negative angle affect simulation
bearing_alpha = np.deg2rad(15);
# bearings are modeled using their centers, not where they start
# back-to-back angular contact

kero_bearing1 = rs.BallBearingElement(
    n=3, n_balls=12, d_balls=5.556E-3,
    fs=140, alpha=bearing_alpha, tag="KeroBearing1")
print(kero_bearing1.K)

kero_bearing2 = rs.BallBearingElement(
    n=5, n_balls=12, d_balls=5.556E-3,
    fs=140, alpha=-bearing_alpha, tag="KeroBearing2")

lox_bearing1 = rs.BallBearingElement(
    n=11, n_balls=5, d_balls=5.556E-3,
    fs=140, alpha=bearing_alpha, tag="LOXBearing1"
)

lox_bearing2 = rs.BallBearingElement(
    n=12, n_balls=5, d_balls=5.556E-3,
    fs=140, alpha=-bearing_alpha, tag="LOXBearing2"
)

bearing_elements = [
    kero_bearing1,
    kero_bearing2,
    lox_bearing1,
    lox_bearing2,
    ];  
#____________________________ ASSEMBLE MODEL __________________________

sum = 0
for v in shaft_elements:
    sum += v.m
print(f"Shaft mass: %.3f kg" % sum);
rotor_model = rs.Rotor(
    shaft_elements=shaft_elements,
    disk_elements=disk_elements,
    bearing_elements=bearing_elements,
    )

fig_rotor = rotor_model.plot_rotor()

RPM_GRAPH_MAX = 70E3
fig_camp = rotor_model.run_campbell(speed_range=np.linspace(0.0, RPM_GRAPH_MAX/60*2 * np.pi)).plot()
display(fig_rotor)
display(fig_camp)