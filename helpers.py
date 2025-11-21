import ross as rs

def PlotRotor(rotor: rs.Rotor):
    fig = rotor.plot_rotor(length_units='in', check_sld=False)
    fig.update_layout(
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
    )
    fig.show();
    return fig