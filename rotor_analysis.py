import ross as rs
import numpy as np

# import plotly just to guarantee that plots will appear in the docs
import plotly
print(rs.__version__)
from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

def PromptBool(message: str) -> bool:
    value = None;
    while value is None:
        response = input(message + "\nEnter \'y\' or \'n\'\n");
        #print('\n')
        if response == 'y' or response == 'Y':
            value = True
        elif response == 'n' or response == 'N':
            value = False
    print('...\n')
    return value

def PromptInt(message: str, accept_none: bool=False) -> int | None:
    value = None
    APPEND = "\nEnter an integer" + (accept_none and " (optional)" or '') + '\n';
    while value is None:
        response = input(message + APPEND);
        #print('\n')
        try:
            value = int(response)
        except ValueError:
            if accept_none:
                print('...\n')
                return None;
            continue
    print('...\n')
    return value;

pio.renderers.default = "browser"# "vscode"

rotor = rs.Rotor.load("MODEL.json")
rotor_fig = rotor.plot_rotor()
rotor_fig.update_yaxes(scaleanchor="x", scaleratio=1)
rotor_fig.update_xaxes(constrain="domain")

for bearing in rotor.bearing_elements:
    print(bearing.tag + " stiffness: ", bearing.K(0))

if PromptBool("Plot rotor model?"):
    rotor_fig.show()

PLOT_3D = False;
PLOT_2D = False;
PLOT_CAMPBELL = True;

RPM_GRAPH_MAX = float(70E3);
RPM_OP = float(50E3)

def ToAngularFreq(rpm: float) -> float:
    return rpm/60 * 2 * np.pi;

if PromptBool("Run modal?"):
    mode_shapes = PromptInt("How many mode shapes? (Default: 6)", accept_none=True) or 6;

    modal = rotor.run_modal(ToAngularFreq(RPM_OP), num_modes=2*mode_shapes, sparse=True);

    if PromptBool("Plot 3D shapes?"):
        for mode, shape in enumerate(modal.shapes):
            modal.plot_mode_3d(mode, frequency_units="RPM").show();
    elif PromptBool("Plot 2D shapes?"):
        for mode, shape in enumerate(modal.shapes):
            modal.plot_mode_2d(mode, frequency_units="RPM").show();

speed_range = np.linspace(0, ToAngularFreq(RPM_GRAPH_MAX), 1000)

if PromptBool("Run and plot Campbell?"):

    frequencies = PromptInt("Frequencies to run? (Default: 6)", accept_none=True) or 6;

    campbell = rotor.run_campbell(
        speed_range=speed_range,
        frequencies=frequencies,
        torsional_analysis=False,
        frequency_type="wd"
    )
    campbell_fig = campbell.plot()
    campbell_fig.show()

#%% Mass
shaft_mass_sum = 0
mass_sum = 0
for v in rotor.shaft_elements:
    shaft_mass_sum += v.m
for v in rotor.disk_elements:
    mass_sum += v.m
mass_sum += shaft_mass_sum

print(f"Rotor mass: %.3f kg" % mass_sum);