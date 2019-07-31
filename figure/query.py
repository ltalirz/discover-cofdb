"""Querying the DB
"""
from __future__ import absolute_import
from bokeh.models.widgets import RangeSlider, CheckboxButtonGroup
from .config import max_points
from six.moves import map
from six.moves import zip
# pylint: disable=too-many-locals
data_empty = dict(x=[0], y=[0], uuid=['1234'], color=[0], name=['no data'])

link_attribute_dict = {
    'opt_out_pe': ['PE', 'WCg', 'WCv', 'Pur'],
    'opt_out_zeopp': ['Density', 'ASA_m^2/g', 'AV_Volume_fraction'],
    'iso_co2': ['henry_coefficient_average'], #TODO: handle also the uptake at 30 bar
    #'iso_n2': ['henry_coefficient_average'], TODO: redesign the query so that this can be added
}

def get_data_aiida(projections, sliders_dict, quantities):
    """Query the AiiDA database"""
    from aiida import load_dbenv, is_dbenv_loaded
    from aiida.backends import settings
    if not is_dbenv_loaded():
        load_dbenv(profile=settings.AIIDADB_PROFILE)
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm.data.parameter import ParameterData
    from aiida.orm.data.structure import StructureData
    from aiida.orm import WorkCalculation, Node

    filters = {}
    
    qb = QueryBuilder()
    qb.append(WorkCalculation, filters={ 'attributes.function_name': {'==': 'collect_outputs'} }, tag='collect')

    for p in projections:
        for link_label in link_attribute_dict:
            if p in link_attribute_dict[link_label]:
               print(p)
               qb.append(ParameterData, project=['attributes.' + p], edge_filters={'label': link_label}, input_of='collect')
    qb.append(StructureData, project=['label', 'uuid'], edge_filters={'label': 'ref_structure'}, input_of='collect')    

    return qb.all()

