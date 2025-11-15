import ross as rs
import numpy as np

# import plotly just to guarantee that plots will appear in the docs
import plotly
print(rs.__version__)
from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"# "vscode"

rotor = rs.Rotor.load("MODEL.json")
rotor_fig = rotor.plot_rotor()
#rotor_fig.show()

rotor_fig.update_yaxes(scaleanchor="x", scaleratio=1)
rotor_fig.update_xaxes(constrain="domain")

RPM_GRAPH_MAX = float(70E3);
RPM_OP = float(50E3)

def ToAngularFreq(rpm: float) -> float:
    return rpm/60 * 2 * np.pi;

speed_range = np.linspace(0, ToAngularFreq(RPM_GRAPH_MAX), 40)

modal = rotor.run_modal(ToAngularFreq(RPM_OP), num_modes=12)
for mode, shape in enumerate(modal.shapes):
    modal.plot_mode_3d(mode, frequency_units="RPM").show();
for mode, shape in enumerate(modal.shapes):
    modal.plot_mode_2d(mode, frequency_units="RPM").show();

campbell = rotor.run_campbell(
    speed_range=speed_range,
    frequencies=6,
    torsional_analysis=False,
    frequency_type="wd"
)
campbell_fig = campbell.plot()
campbell_fig.show()

mass_sum = 0
for v in rotor.shaft_elements:
    mass_sum += v.m
print(f"Shaft mass: %.3f kg" % mass_sum);