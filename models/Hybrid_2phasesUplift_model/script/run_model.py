import os
import math
import numpy as np
import pandas as pd

from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter

from scripts import badInput as tools

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

from badlands.model import Model as badlandsModel

# initialise model
model = badlandsModel()

# Define the XmL input file
model.load_xml('input_paleo2-depo-isoFlex.xml')


keepgoing = True

changeTe_t =  np.arange(0,70+1,1)*-1000000
flex = []

while(keepgoing):

    next_time = model.tNow + model.input.tDisplay

    if next_time > model.input.tEnd:
        model.run_to_time(model.input.tEnd)
        keepgoing = False
    else:
        if next_time in changeTe_t:
            print("#######-------change Te map: " + str(next_time/-1000000) + " Ma -------------########")
            elastic_file = "../../badlands_constant_input/elastic_thickness_map/Te"+str(int(next_time/-1000000))+".csv"
            datae = pd.read_csv(elastic_file, sep=" ", header = None, engine='c', na_filter=False, \
                               dtype=np.float, low_memory=False)

            tmp_te = np.reshape(datae.values, (ny, nx))
            model.flex.Te =  tmp_te
            changeTe_t = np.delete(changeTe_t, np.where(changeTe_t==next_time/-1000000))

        if next_time == -5000000.0:
            forward_erodep_5Ma_original = tools.mapSim2Reg(model.FVmesh.node_coords[:, :2],
                              model.cumdiff, rXY, nx, ny)
            forward_topo_5Ma = tools.mapSim2Reg(model.FVmesh.node_coords[:, :2],
                              model.elevation, rXY, nx, ny)

            print("saved 5 Ma")

        if next_time == -3000000.0:
            # use stream poewr law's erodibility
            model.input.SPLero = 6e-7

        flex.append(tools.mapSim2Reg(model.FVmesh.node_coords[:, :2],
                              model.tinFlex, rXY, nx, ny))
        model.run_to_time(next_time)
