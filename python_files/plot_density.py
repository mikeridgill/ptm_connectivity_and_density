#!/usr/bin/env python

''' This programme plots the density of particle locations, using the output from
a particle tracking model (PTM).

In addition to plotting a representation of the density of locations where released
particles have travelled, this programme outputs a MATLAB file with the matrix used to
produce the plot and a summary of the input parameters.

Three MATLAB .mat files are required, as inputs, for this programme to run:
- (1) output from the PTM;
- (2) information describing the release sites; and,
- (3) parameters describing how this programme will run and determine desired output.

The paths to files (1) and (2) should be included in file (3). File (3) should be included when running this
programme, as an argument. For example:

> python plot_density.py parameters.mat

See the associated README.txt file for further information.
'''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from datetime import datetime, date, time, timedelta
import time
import os
import shutil
import sys
import scipy.io
import mat73
import multiprocessing as mp
import utm
from shapely.geometry import Polygon, Point
import geopandas as gpd
import pyproj

# Start
print('Started at: ', datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
start = time.time()

# Configuration
plt.style.use('../config/PaperDoubleFig.mplstyle') # Style for figures

# Functions
def open_matlab_file(mat_file_name):
    ''' Read MATLAB .mat files. Automatically handles if .mat files are version 7.3, or
    not.
    '''
    try:
        mat_load = scipy.io.loadmat(mat_file_name)
    except:
        mat_load = mat73.loadmat(mat_file_name)

    return mat_load

def count_for_location(loc):
    '''Tallies particle counts, for a given location, for all release days and months, and for all time steps. The decision to do this per location was chosen, because this is likely to be the largest dimension and is therefore the most efficient division for multiprocessing.'''

    particle_counts_loc = np.zeros((increments, increments))

    for i in range(np.shape(lats_loop)[1]):
        for j in range(np.shape(lats_loop)[2]):
            for k in range(np.shape(lats_loop)[3]):
                for l1 in range(increments):
                    if lat_grid[l1] - np.divide(lat_increment, 2) <= lats_loop[loc, i, j, k] < lat_grid[l1] + np.divide(lat_increment, 2):
                        for l2 in range(increments):
                            if lon_grid[l2] - np.divide(lon_increment, 2) <= lons_loop[loc, i, j, k] < lon_grid[l2] + np.divide(lon_increment, 2):
                                particle_counts_loc[l1,l2] += 1

    return particle_counts_loc

# Read input parameters .mat file (file (3) in description above) and extract values
parameters_file = str(sys.argv[1])
parameters = open_matlab_file(parameters_file)
ptm_output_file = parameters['ptm_output_file'][0]
release_sites_file = parameters['release_sites_file'][0]
days_indices = np.array(parameters['days_indices']).reshape(np.shape(parameters['days_indices'])[1],)
months_indices = np.array(parameters['months_indices']).reshape(np.shape(parameters['months_indices'])[1],)
time_indices = np.array(parameters['time_indices']).reshape(np.shape(parameters['time_indices'])[1],)
shape_check = parameters['shape_check'].reshape(4,)
fig_lims = parameters['fig_lims'].reshape(4,)
dpi = parameters['dpi'][0][0]
keep_polygon_shapefiles = parameters['keep_polygon_shapefiles'][0][0]
keep_polygon_mats = parameters['keep_polygon_mats'][0][0]
increments = parameters['increments'][0][0]

# Read output from PTM .mat file (file (1) in description above) and extract values
ptm_output = open_matlab_file(ptm_output_file)
xstart = ptm_output['xstart']
ystart = ptm_output['ystart']
nmonth = ptm_output['msave']
ndays = ptm_output['dsave']
DT = ptm_output['DT']
pld = ptm_output['pld']

# Read latsave and lonsave and deal with any potential shape issues
lonsave = np.array(ptm_output['lonsave'])
latsave = np.array(ptm_output['latsave'])

reshape_error_message = 'There is a potential problem with the shape of latsave/lonsave. This programme expects the size of dimension 1 and 4 to be > 1. It should deal with the size of dimension 2 or 3 being = 1, though. Importing MATLAB .mat files into Python can cause problems, when the dimension of an array has a a size of 1, it flattens the array.'

if len(np.shape(latsave)) == 3:
    if shape_check[1] == 1:
        latsave = np.reshape(latsave, (np.shape(latsave)[0], 1, np.shape(latsave)[1], np.shape(latsave)[2]))
        lonsave = np.reshape(lonsave, (np.shape(lonsave)[0], 1, np.shape(lonsave)[1], np.shape(lonsave)[2]))
    elif shape_check[2] == 1:
        latsave = np.reshape(latsave, (np.shape(latsave)[0], np.shape(latsave)[1], 1, np.shape(latsave)[2]))
        lonsave = np.reshape(lonsave, (np.shape(lonsave)[0], np.shape(lonsave)[1], 1, np.shape(lonsave)[2]))
    else:
        print(reshape_error_message)
elif len(np.shape(latsave)) == 2:
    latsave = np.reshape(latsave, (np.shape(latsave)[0], 1, 1, np.shape(latsave)[1]))
    lonsave = np.reshape(lonsave, (np.shape(lonsave)[0], 1, 1, np.shape(lonsave)[1]))
elif len(np.shape(latsave)) == 4:
    pass
else:
    print(reshape_error_message)

# Read release sites .mat file (file (1) in description above) and extract values
release_sites = open_matlab_file(release_sites_file)
nrel = release_sites['np'][0][0]
plat = release_sites['plat'].reshape(np.shape(release_sites['plat'])[0],)
plon = release_sites['plon'].reshape(np.shape(release_sites['plon'])[0],)
xc = release_sites['xc'].reshape(np.shape(release_sites['xc'])[1],)
yc = release_sites['yc'].reshape(np.shape(release_sites['yc'])[1],)
r = release_sites['r'][0][0]
ns = len(xc)
site_utm_x = release_sites['s_xc']
site_utm_y = release_sites['s_yc']

# Print out summary of parameters and values to slurm file
print('Summary of parameters and values read from inputted files:')
print('ptm_output_file: ', ptm_output_file)
print('release_sites_file: ', release_sites_file)
print('days_indices: ', days_indices)
print('months_indices: ', months_indices)
print('time_indices: ', time_indices)
print('shape_check: ', shape_check)
print('fig_lims: ', fig_lims)
print('dpi: ', dpi)
print('keep_polygon_shapefiles: ', keep_polygon_shapefiles)
print('keep_polygon_mats: ', keep_polygon_mats)
print('xstart: ', xstart)
print('ystart: ', ystart)
print('nmonth: ', nmonth)
print('ndays: ', ndays)
print('lonsave: ', lonsave)
print('latsave: ', latsave)
print('DT: ', DT)
print('pld: ', pld)
print('nrel: ', nrel)
print('plat: ', plat)
print('plon: ', plon)
print('xc: ', xc)
print('yc: ', yc)
print('r: ', r)
print('ns: ', ns)
print('site_utm_x: ', site_utm_x)
print('site_utm_y: ', site_utm_y)
print('increments: ', increments)

# Create an output directory
output_dir = '../output/' + datetime.now().strftime('%Y-%m-%dT%H%M') + '_plot_density/'
os.makedirs(output_dir, exist_ok=True)
print('Output directory: ', output_dir)

# Convert polygon coordinates from utm to lat and lon
p = pyproj.Proj(proj='utm', zone=30, ellps='WGS84')
site_lons, site_lats = p(release_sites['s_xc'], release_sites['s_yc'], inverse=True)

# Create an output folder for each site and polygon shapefile
for i in range(ns):
    site_num = i+1
    os.makedirs(output_dir + 'site_' + str(site_num) + '/', exist_ok=True)
    os.makedirs(output_dir + 'site_' + str(site_num) + '/shapefile/', exist_ok=True)
    polygon_geom = Polygon(zip(site_lons[i,:], site_lats[i,:]))
    polygon = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[polygon_geom])
    polygon.to_file(output_dir + 'site_' + str(site_num) + '/shapefile/site_' + str(site_num) + '.shp', driver="ESRI Shapefile")

# Read shapefile to plot coastline
europe_shape_file = '../coastline_shapefile/Europe_coastline_poly.shp'
europe_shape = gpd.read_file(europe_shape_file).to_crs('EPSG:4326')

# Plot polygons
fig1 = plt.figure()
ax1 = fig1.add_subplot(111)

for i in range(ns):
    site_num = i+1
    polygon_file = output_dir + 'site_' + str(site_num) + '/shapefile/site_' + str(site_num) + '.shp'
    site_polygon = gpd.read_file(polygon_file).to_crs('EPSG:4326')
    site_polygon.plot(ax=ax1, facecolor='#4363d8', alpha=0.4, edgecolor='black', linewidth=0.5)

europe_shape.plot(ax=ax1, facecolor='#9A6324', alpha=0.4, edgecolor='black', linewidth=0.5)
ax1.set_xlim([fig_lims[0], fig_lims[1]])
ax1.set_ylim([fig_lims[2], fig_lims[3]])
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.savefig(output_dir + 'polygon_locations.png', dpi=dpi)

# Slice latsave and lonsave to give desired perspective
lats = latsave[:, days_indices-1, :, :]
lats = lats[:, :, months_indices-1, :]
lats = lats[:, :, :, time_indices-1]

lons = lonsave[:, days_indices-1, :, :]
lons = lons[:, :, months_indices-1, :]
lons = lons[:, :, :, time_indices-1]

# Convert zeros to NaNs
lats = lats.astype('float')
lats[lats==0] = np.nan
lons = lons.astype('float')
lons[lons==0] = np.nan

# Construct a grid
lat_min = np.nanmin(lats)
lat_max = np.nanmax(lats)
lon_min = np.nanmin(lons)
lon_max = np.nanmax(lons)
lat_increment = np.divide(lat_max - lat_min, increments)
lon_increment = np.divide(lon_max - lon_min, increments)
lat_grid = np.arange(lat_min, lat_max, lat_increment)
lon_grid = np.arange(lon_min, lon_max, lon_increment)

# Calculate density
sites_list = np.arange(np.shape(latsave)[0])
num_cores = mp.cpu_count() # Needed to determine number of cores can be used for multiprocessing
particle_counts_all = np.zeros((increments, increments)) # matrix to hold counts of particles

for i in range(ns):
    site_num = i+1
    print('Processing site: ', site_num)

    # Isolate release site
    sites_indices = sites_list[i*nrel:(i+1)*nrel]
    lats_loop = lats[sites_indices, :, :, :]
    lons_loop = lons[sites_indices, :, :, :]

    # Create density plot for particles released from this site
    particle_counts_loop = np.zeros((increments, increments)) # matrix to hold counts of particles

    # Determine density for this site
    pool = mp.Pool(num_cores)
    particle_counts_catch_loop = pool.map(count_for_location, range(np.shape(lats_loop)[0]))
    pool.close()

    # Sum counts
    particle_counts_loop = np.nansum(particle_counts_catch_loop, axis=0)
    particle_counts_all += particle_counts_loop # Add to running total for final density plot

    # Check whether this polygon is all just NaNs. This crashes the programme.
    sum_check = np.sum(particle_counts_loop)
    print('sum_check: ', sum_check)
    if sum_check == 0:
        print('Warning, no particles have been counted for site ' + str(site_num))

    # Save date to .mat file in folder and plot density, for this site, if keep_polygon_mats=1
    if keep_polygon_mats == 1:
        dict_data = {
            'particle_counts_density': particle_counts_loop,
        }

        scipy.io.savemat(output_dir + 'site_' + str(site_num) + '/density_for_site_' + str(site_num) + '.mat', dict_data)

        # Plot density plot
        if sum_check != 0:
            fig2 = plt.figure()
            ax2 = fig2.add_subplot(111)
            plt.imshow(particle_counts_loop, extent=[lon_min, lon_max, lat_max, lat_min], norm=colors.LogNorm())
            plt.colorbar(label='Particle count')
            europe_shape.plot(ax=ax2, facecolor='#9A6324', alpha=0.4, edgecolor='black', linewidth=0.5)

            for n in range(ns):
                if n!=i:
                    site_num_n = n+1
                    polygon_file = output_dir + 'site_' + str(site_num_n) + '/shapefile/site_' + str(site_num_n) + '.shp'
                    site_polygon = gpd.read_file(polygon_file).to_crs('EPSG:4326')
                    site_polygon.plot(ax=ax2, facecolor='#4363d8', alpha=0.4, edgecolor='black', linewidth=0.5)

            polygon_file = output_dir + 'site_' + str(site_num) + '/shapefile/site_' + str(site_num) + '.shp'
            site_polygon = gpd.read_file(polygon_file).to_crs('EPSG:4326')
            site_polygon.plot(ax=ax2, facecolor='#e6194b', alpha=0.4, edgecolor='black', linewidth=0.5)
            ax2.set_xlim([fig_lims[0], fig_lims[1]])
            ax2.set_ylim([fig_lims[2], fig_lims[3]])
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.savefig(output_dir + 'site_' + str(site_num) + '/density_plot_for_site_' + str(site_num) + '.png', dpi=dpi)
            plt.close()

# Plot density plot for all sites
fig3 = plt.figure()
ax3 = fig3.add_subplot(111)
plt.imshow(particle_counts_all, extent=[lon_min, lon_max, lat_max, lat_min], norm=colors.LogNorm())
plt.colorbar(label='Particle count')
europe_shape.plot(ax=ax3, facecolor='#9A6324', alpha=0.4, edgecolor='black', linewidth=0.5)

for n in range(ns):
    site_num_n = n+1
    polygon_file = output_dir + 'site_' + str(site_num_n) + '/shapefile/site_' + str(site_num_n) + '.shp'
    site_polygon = gpd.read_file(polygon_file).to_crs('EPSG:4326')
    site_polygon.plot(ax=ax3, facecolor='#4363d8', alpha=0.4, edgecolor='black', linewidth=0.5)

ax3.set_xlim([fig_lims[0], fig_lims[1]])
ax3.set_ylim([fig_lims[2], fig_lims[3]])
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.savefig(output_dir + 'density_plot.png', dpi=dpi)

# create an overall data output .mat file
dict_data_all = {
    'particle_counts_density': particle_counts_all,
    'increments': increments,
    'days_indices': days_indices,
    'months_indices': months_indices,
    'time_indices': time_indices,
    'ns' : ns,
    'nrel' : nrel,
    'nmonth' : nmonth,
    'ndays' : ndays,
    'xstart' : xstart,
    'ystart' : ystart,
    'DT' : DT,
    'pld' : pld,
    'plat' : plat,
    'plon' : plon,
    'xc' : xc,
    'yc' : yc,
    's_xc' : site_utm_x,
    's_yc' : site_utm_y,
    'r' : r,
}

scipy.io.savemat(output_dir + '/data_density.mat', dict_data_all)

# Remove polygon shapefiles, if keep_polygon_shapefiles=0
if keep_polygon_shapefiles == 0:
    for i in range(ns):
        site_num = i+1
        shutil.rmtree(output_dir + 'site_' + str(site_num) + '/shapefile/')

# Remove polygon directories if not required
if (keep_polygon_mats == 0) & (keep_polygon_shapefiles == 0):
    for i in range(ns):
        site_num = i+1
        shutil.rmtree(output_dir + 'site_' + str(site_num) + '/')

# Complete script and output duration data
print('Completed at: ', datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
seconds_period = time.time()-start
print('Finished in: {:.2f}s'.format(seconds_period))
print('In H:MM:SS.SSSSSS format: ', str(timedelta(seconds=seconds_period)))
