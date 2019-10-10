# -*- coding: utf-8 -*-
from __future__ import print_function

def plot_isotherm(**kwargs):
    """Plot isotherm figure"""
    from bokeh.plotting import figure
    import bokeh.models as bmd
    from bokeh.layouts import row
    import numpy as np


    tooltips = [
        ("Uptake (mol/kg)", "@q_avg"),
    ]
    hover = bmd.HoverTool(tooltips=tooltips)
    TOOLS = ["pan", "wheel_zoom", "box_zoom", "reset", "save", hover]

    pmax = 30
    p1 = figure(tools=TOOLS, height=350, width=450, x_range=(-1, pmax+1), y_range=(-1,41))
    p1.xaxis.axis_label = 'Pressure (bar)'
    p1.yaxis.axis_label = 'Uptake (mol/kg)'

    p2 = figure(tools=TOOLS, height=350, width=250, x_range=(-51, 0+1), y_range=(-1,41))
    p2.xaxis.axis_label = 'Heat of adsorption (kJ/mol)'
    p2.yaxis.axis_label = 'Uptake (mol/kg)'


    plotcolor={'co2':'red','n2':'blue'}
    plotlabel={'co2':'CO₂','n2':u'N₂'}
    #plotlabel={'co2':'CO2','n2':u'N2'}

    for gas in ['co2', 'n2']:
        pe_res = kwargs['pm_' + gas].get_dict()
        
        if 'henry_coefficient_average' in pe_res.keys(): #porous
            # parse isotherm for plotting
            p = [a[0] for a in pe_res['isotherm_loading']] #(bar)
            q_avg = [a[1] for a in pe_res['isotherm_loading']] #(mol/kg)
            q_dev = [a[2] for a in pe_res['isotherm_loading']] #(mol/kg)
            q_upper = np.array(q_avg) + np.array(q_dev)
            q_lower = np.array(q_avg) - np.array(q_dev)
            h_avg = [a[1] for a in pe_res['isotherm_enthalpy']] #(kJ/mol)
            h_dev = [a[2] for a in pe_res['isotherm_enthalpy']] #(kJ/mol)
            # TRICK: use the enthalpy from widom (energy-RT) which is more accurate that the one at 0.001 bar (and which also is NaN for weakly interacting systems)
            h_avg[0] = pe_res['adsorption_energy_average']-pe_res['temperature']/120.027
            h_dev[0] = pe_res['adsorption_energy_dev']
            h_upper = np.array(h_avg) + np.array(h_dev)
            h_lower = np.array(h_avg) - np.array(h_dev)

        else: #nonporous
            p = [0, pmax]
            q_avg = q_upper = q_lower = h_avg = h_upper = h_lower = [0, 0]
            
        data = dict(p=p, q_avg=q_avg, q_upper=q_upper, q_lower=q_lower, h_avg=h_avg, h_upper=h_upper, h_lower=h_lower)
        source = bmd.ColumnDataSource(data=data)

        p1.line('p', 'q_avg', source=source, line_color=plotcolor[gas], line_width=2, legend=plotlabel[gas])
        p1.circle('p', 'q_avg', source=source, color=plotcolor[gas], size=10, legend=plotlabel[gas])
        p1.add_layout(
            bmd.Whisker(source=source, base="p", upper="q_upper", lower="q_lower") #, level="overlay")
        )

        p2.line('h_avg', 'q_avg', source=source, line_color=plotcolor[gas], line_width=2)
        p2.circle('h_avg', 'q_avg', source=source, color=plotcolor[gas], size=10)
        p2.add_layout(
            bmd.Whisker(source=source, base="h_avg", upper="h_upper", lower="h_lower", dimension='width')  # , level="overlay")
        )

    p1.legend.location = "top_left"

    fig = row(p1, p2)

    return fig
