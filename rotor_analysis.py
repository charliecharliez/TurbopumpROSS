import ross as rs

import numpy as np
import os

from ross.units import Q_

# import plotly just to guarantee that plots will appear in the docs
import plotly
print(rs.__version__)
from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

figures: dict[str: dict] = {};
def SaveFigure(fig, name: str, file_extension: str | None = 'html', append_num: int | None=None) -> None:

    if name in figures:

        if append_num is None:
            append_num = 0;
        append_num += 1;
        # recursive
        return SaveFigure(fig, name + str(append_num), append_num);
    
    figures[name] = {
            'fig': fig,
            'extension': file_extension,
        };

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

for bearing in rotor.bearing_elements:
    print(bearing.tag + " stiffness: ", bearing.K(0))

if PromptBool("Plot rotor model?"):
    rotor_fig = rotor.plot_rotor(check_sld=True, length_units='in');

    rotor_fig.update_layout(
        yaxis=dict(
            showgrid=True,
            dtick=0.5,
            scaleanchor='x',  # link y-axis scale to x-axis
        ),
        xaxis=dict(
            dtick=0.5,
            showgrid=True,
            #scaleratio=1,
            scaleanchor=None,
        ),
        #width=600,
        #height=600  # make figure square so circles look round
    )
    rotor_fig.show()
    SaveFigure(rotor_fig, "RotorModel");

RPM_GRAPH_MAX = float(70E3);
RPM_OP = float(50E3)

def ToAngularFreq(rpm: float) -> float:
    return rpm/60 * 2 * np.pi;

if PromptBool("Run modal?"):
    mode_shapes = PromptInt("How many mode shapes? (Default: 5)", accept_none=True) or 5;

    modal = rotor.run_modal(ToAngularFreq(RPM_OP), num_modes=2*mode_shapes, sparse=True);
    
    shape_figs = [];

    guh = (PromptBool("Plot 3D shapes?") and 3) or (PromptBool("Plot 2D shapes?") and 2) or 0

    if guh != 0:
        for mode, shape in enumerate(modal.shapes):
            if guh == 3:
                fig = modal.plot_mode_3d(mode, frequency_units="RPM");
            else:
                fig = modal.plot_mode_2d(mode, frequency_units="RPM");
            shape_figs.append(fig)
            SaveFigure(fig, name=str(guh) + "D_ShapeMode" + str(mode));

    for fig in shape_figs:
        fig.show()

speed_range = np.linspace(0, ToAngularFreq(RPM_GRAPH_MAX), 70)

if PromptBool("Run and plot Campbell?"):

    frequencies = PromptInt("Frequencies to run? (Default: 5)", accept_none=True) or 5;

    campbell = rotor.run_campbell(
        speed_range=speed_range,
        frequencies=frequencies,
        frequency_type="wd"
    )

    campbell_fig = campbell.plot()
    SaveFigure(campbell_fig, "CampbellDiagram")
    campbell_fig.update_yaxes(range=[0, 90e3]);
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

#%% Save figs
if PromptBool("Save result figures?"):
    folder_name: str = input("Results folder name:?");
    
    if folder_name == "":
        folder_name = 'Default'
    DIR = os.getcwd();
    results_dir = os.path.join(DIR, 'Results');
    folder_path = os.path.join(results_dir, folder_name);

    if not os.path.isdir(folder_path):
        os.makedirs(folder_path);
    #print(figures)
    for name, v in figures.items():
        fig = v['fig'];
        file_extension = v['extension'];

        if file_extension == 'html':
            fig.write_html(folder_path + "/" + name + '.html');
        else:
            fig.write_image(folder_path + '/' + name + '.' + file_extension);