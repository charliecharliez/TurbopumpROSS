import ross as rs
import numpy as np
import math

from ross.units import Q_
# import plotly just to guarantee that plots will appear in the docs
import plotly

from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio


pio.renderers.default = "browser"# "vscode"

def safe_int(x: float, tol: float = 1e-9) -> int:
    rounded = round(x);
    return int(rounded) if math.isclose(x, rounded, abs_tol=tol) else int(rounded);

# turbine operating temperature is ~750 Fahrenheit, could be higher, using 800 deg F
# https://www.specialmetals.com/documents/technical-bulletins/inconel/inconel-alloy-718.pdf

inco_718 = rs.Material(name="Inconel-718", rho=8193, E = 1.77885e11, Poisson=0.271)
#print(inco_718)
#print("="*36) # takes a while

# https://asm.matweb.com/search/specificmaterial.asp?bassnum=mq304a
ss_304 = rs.Material(name="Stainless-304", rho = 8000, E = 1.93e11, Poisson=0.29);

#print(rs.Material.available_materials())
#print("="*36) # takes a while
ss_A286 = rs.Material(name="Stainless-A286", rho=7944.1327, E=1.999e11, Poisson=0.31)

#%%____________________PRELIMINARY SHAFT______________________
# start from turbine to lox inlet

pre_list = []

def ShaftSection(L: float, odl: float, odr: float | None = None) -> None:
    if odr is None:
        odr = odl;
    pre_list.append({"L": L, "odl": odl, "odr": odr});

def PartitionedSection(L: float, odl: float, partitions: int, odr: float | None = None):
    if odr is None:
        odr = odl;
    SECTION_LENGTH = L / partitions;
    SLOPE = (odr - odl) / L;
    for i in range(partitions):
        if odl == odr:
            ShaftSection(SECTION_LENGTH, odl=odl, odr=odr)
        else:
            this_odl = odl + SLOPE*i*SECTION_LENGTH;
            this_odr = this_odl + SLOPE*SECTION_LENGTH;
            ShaftSection(SECTION_LENGTH, odl=this_odl, odr=this_odr);

def ThreadSection(L: float, major_d: float, minor_d: float, tpi: int | float, num_threads: int | None, thread_right: bool=False) -> None:
    extra = abs(L - (num_threads / tpi))

    if thread_right and extra > 1e-9:
        ShaftSection(L=extra, odl=major_d);
    
    THREAD_HALF_WIDTH = 1.0 / (2 * tpi);
    for i in range(num_threads * 2):
        if i % 2 == 0:
            ShaftSection(L=THREAD_HALF_WIDTH, odl=minor_d, odr=major_d);
        else:
            ShaftSection(L=THREAD_HALF_WIDTH, odl=major_d, odr=minor_d);
    if not thread_right and extra > 1e-9:
        ShaftSection(L=extra, odl=major_d);

# UNC 3/8-16 threads
ThreadSection(L=0.38,
            major_d=3/8,
            minor_d=0.3005,
            tpi=16,
            num_threads=5)

PartitionedSection(L=3.0428, odl=0.3976, partitions=13);

# LABY SECTION
ShaftSection(L=0.08, odl=0.63)
NOTCH_WIDTH = 0.01; #in
GAP_WIDTH = 0.031; #in
GAP_DEPTH = 0.031; #in
STEP_WIDTH = 0.04; #in
STEP_SIZE = 0.011; #in

laby_od_temp = 0.63; #in
STEP_COUNT = 6;
GAPS_PER_STEP = 5;
'''
for i in range(STEP_COUNT):
    for j in range(GAPS_PER_STEP):
        ShaftSection(L=NOTCH_WIDTH,odl=laby_od_temp);
        ShaftSection(L=GAP_WIDTH,odl=laby_od_temp - 2*GAP_DEPTH)
        
        if j == GAPS_PER_STEP - 1: # last gap before next step
            if i == STEP_COUNT - 1: # last step
                ShaftSection(L=NOTCH_WIDTH,odl=laby_od_temp);
            else:
                ShaftSection(L=STEP_WIDTH,odl=laby_od_temp);

    laby_od_temp += 2*STEP_SIZE;
'''
# Just average the diameters
PartitionedSection(L=1.4301, partitions=5, odl=0.63 - GAP_DEPTH, odr=0.74 - GAP_DEPTH)
# END OF LABY

PartitionedSection(L=1.098,odl=0.47244, partitions=4);
PartitionedSection(L=0.6721,odl=0.375, partitions=3);
ThreadSection(L=0.7279,
            major_d=1/4,
            minor_d=0.1905,
            tpi=20,
            num_threads=5, thread_right=True);

#%% SIMPLE SHAFT
lengths = [];
odr = [];
odl = [];
for section in pre_list:
    lengths.append(Q_(section["L"], 'in'));
    odl.append(Q_(section["odl"], 'in'));
    odr.append(Q_(section["odr"], 'in'));

shaft_elements = [
    rs.ShaftElement(
        L = lengths[i],
        idl=0,
        odl=odl[i],
        odr=odr[i],
        material=ss_A286,
        gyroscopic=True,
        shear_effects=True,
        rotary_inertia=True
    )
    for i in range(len(pre_list))
];

simple_shaft = rs.Rotor(shaft_elements=shaft_elements);

add_nodes = [];
position_map = {};

def Mark(object: any, position_inch: float):
    position_m = position_inch * 0.0254;
    add_nodes.append(position_m);
    position_map[position_m] = object;

sleeve_nut = rs.DiskElement(
    n=0,
    m=1.3618E-2,
    Id=2.0408E-2,
    Ip=1.5499E-2,
    tag="Sleeve Nut",
    scale_factor=0.25
)
Mark(sleeve_nut, 0.08758354);

turbine = rs.DiskElement(
    n=0,
    m=0.292578,
    Ip = 3.68819E-4,
    Id=1.85449E-4,
    tag="Turbine",
    scale_factor=2.2,
    );
Mark(turbine, 0.15098510);

rotor_sleeve = rs.DiskElement(
    n=0,
    m=0.0903,
    Ip=1.1E-5,
    Id=2.4E-5,
    tag="Rotor Sleeve",
    scale_factor=0.5,
);
Mark(rotor_sleeve, 0.834645669);

kero_nut = rs.DiskElement(
    n=0,
    m=0.024601,
    Ip=2.96E-6,
    Id=1.65E-6,
    tag="Kero Bearing Nut",
    scale_factor=0.5
)
Mark(kero_nut, 1.6013385827);

kero_inducer = rs.DiskElement(
    n=0,
    m=2.2054E-2,
    Ip = 1.3141E-6,
    Id = ((1.1675 + 1.8117)/2)*1E-6,
    tag = "Kero Inducer",
    scale_factor=0.75
);
Mark(kero_inducer, 2.68662598425);

kero_impeller = rs.DiskElement(
    n=0,
    m=6.6809E-2,
    Ip=1.9328E-5,
    Id=1.02705E-5,
    tag="Kero Impeller",
    scale_factor=1.25,
    color="Green"
)
Mark(kero_impeller, 3.226722440945);

lox_bearing_nut = rs.DiskElement(
    n=0,
    m=1.0346E-2,
    Ip=3.4483E-7,
    Id=(6.9851 + 4.2343)/2*1E-7,
    tag="LOX Bearing Nut",
    scale_factor=0.5
)
Mark(lox_bearing_nut, 5.854803937008);

lox_impeller = rs.DiskElement(
    n=0,
    m=5.2961E-2,
    Ip=9.9799E-6,
    Id=5.6119E-6,
    tag="LOX Impeller",
    scale_factor=1.25,
    color="Cyan"
)
Mark(lox_impeller, 6.256729133858);

lox_inducer = rs.DiskElement(
    n=0,
    m=1.8831E-2,
    Ip=1.2175E-6,
    Id=(9.1255 + 8.2006)/2*1E-7,
    tag="LOX Inducer",
    scale_factor=0.75,
)
Mark(lox_inducer, 6.832196456693);

retaining_nut = rs.DiskElement(
    n=0,
    m=4.491E-3,
    Ip=7.134E-8,
    Id=6.8793E-8,
    tag="Retaining Nut",
    scale_factor=0.25,
)
Mark(retaining_nut, 7.358319685039);

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
]

bearing_alpha = 15 * np.pi / 180;

l_preload = 100; #N
k_preload = 100; #N   

kero_bearing1 = rs.BallBearingElement(
    n=0, n_balls=12, d_balls=5.556E-3,
    fs=k_preload, alpha=bearing_alpha, tag="KeroBearing1")

Mark(kero_bearing1, 0.84904964),

kero_bearing2 = rs.BallBearingElement(
    n=0, n_balls=12, d_balls=5.556E-3,
    fs=k_preload, alpha=bearing_alpha, tag="KeroBearing2")
Mark(kero_bearing2, 1.24275043),

lox_bearing1 = rs.BallBearingElement(
    n=0, n_balls=10, d_balls=5.556E-3,
    fs=l_preload, alpha=bearing_alpha, tag="LOXBearing1"
)
Mark(lox_bearing1, 5.13965039);

lox_bearing2 = rs.BallBearingElement(
    n=0, n_balls=10, d_balls=5.556E-3,
    fs=l_preload, alpha=bearing_alpha, tag="LOXBearing2"
)
Mark(lox_bearing2, 5.53335118);

bearing_elements = [
    kero_bearing1,
    kero_bearing2,
    lox_bearing1,
    lox_bearing2
]

node_shaft = simple_shaft.add_nodes(add_nodes);
shaft_elements = node_shaft.shaft_elements;

def FindClose(from_list: any, value: float) -> float | None:
    for v in from_list:
        if abs(value - v) < 1e-9:
            return v

for i in range(len(node_shaft.nodes_pos)):
    position = node_shaft.nodes_pos[i];
    key = FindClose(position_map.keys(), position);
    if key is None: continue
    element = position_map[key]
    element.n = i;

rotor_model = rs.Rotor(
    shaft_elements=shaft_elements,
    disk_elements=disk_elements,
    bearing_elements=bearing_elements)

rotor_model.plot_rotor().show()
rotor_model.save("MODEL.json")