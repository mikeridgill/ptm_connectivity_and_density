
# Table of Contents

1.  [Introduction](#orgb4d5fd3)
2.  [Accompanying input files](#org2d719f7)
    1.  [The dimensions of latsave/lonsave](#orgd9b028e)
    2.  [Specifying the shape of latsave/lonsave](#org0b70a20)
    3.  [Python and MATLAB indexing](#org2157bd8)
    4.  [Choosing whether to save release site-specific information](#org637d97a)
3.  [Running on SCW](#org4052c97)
    1.  [Slurm input files](#org48ecd67)
    2.  [Slurm output files](#orgb3d899c)



<a id="orgb4d5fd3"></a>

# Introduction

The contents of this repository have been written to work with specific outputs from a particle tracking model (PTM), as used by the [School of Ocean Sciences](https://www.bangor.ac.uk/oceansciences/index.php.en), Bangor University.

This README file describes the use of the following Python programmes:

1.  plot_connectivity.py
2.  plot<sub>density.py</sub>

As their names suggest, these programmes aim to determine and represent the connectivity between different release sites and the density of particle counts, using the output from a PTM. Connectivity is a count of the number of released particles, from one release site, that spend any amount of time in the area of another release site, during the period of interest. The density of particle counts is a measure of how many particles spend any amount of time in a grid cell, within a spatial domain, of a specified spatial resolution, during the period of interest. In each case, these measurements of connectivity and density can be considered either per release site, or all together.

Given the large size of this output, these Python programmes are accompanied with slurm files to aid running them on high-performance computation hardware, like Supercomputing Wales (SCW).


<a id="org2d719f7"></a>

# Accompanying input files

Each programme requires 3 accompanying MATLAB .mat files:

1.  output from the PTM;
2.  information describing the release sites; and,
3.  parameters describing how this programme will run and determine desired output.

The programmes will read these accompanying files when running. The paths to the first two files in the list should be included within the third file in the list, which is included as an argument when running this
programme. For example:

    python plot_connectivity.py parameters.mat

An example of the parameters file, called parameters.mat, is included in the directory input<sub>files</sub>, which can be used as a template to create a file that suits your requirements, using MATLAB. The table below summarises what is in this file.

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Parameter</th>
<th scope="col" class="org-left">Description</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">ptm<sub>output</sub><sub>file</sub></td>
<td class="org-left">String with path to the output from PTM.</td>
</tr>


<tr>
<td class="org-left">release<sub>sites</sub><sub>file</sub></td>
<td class="org-left">String with path to the information describing release sites.</td>
</tr>


<tr>
<td class="org-left">days<sub>indices</sub></td>
<td class="org-left">An array of the indices of interest for dimension 2 of latsave/lonsave.</td>
</tr>


<tr>
<td class="org-left">months<sub>indices</sub></td>
<td class="org-left">An array of the indices of interest for dimension 3 of latsave/lonsave.</td>
</tr>


<tr>
<td class="org-left">time<sub>indices</sub></td>
<td class="org-left">An array of the indices of interest for dimension 4 of latsave/lonsave.</td>
</tr>


<tr>
<td class="org-left">shape<sub>check</sub></td>
<td class="org-left">An array confirming the shape of the 4 dimensions of latsave/lonsave.</td>
</tr>


<tr>
<td class="org-left">dpi</td>
<td class="org-left">Dots per inch for figures produced.</td>
</tr>


<tr>
<td class="org-left">fig<sub>lims</sub></td>
<td class="org-left">Lats and lons for cropping figures [x<sub>left</sub>, x<sub>right</sub>, y<sub>down</sub>, y<sub>up</sub>].</td>
</tr>


<tr>
<td class="org-left">keep<sub>polygon</sub><sub>mats</sub></td>
<td class="org-left">1 to keep the release site-specific matrices/plots. 0 to not keep.</td>
</tr>


<tr>
<td class="org-left">keep<sub>polygon</sub><sub>shapefiles</sub></td>
<td class="org-left">1 to keep the release site-specific shapefiles. 0 to not keep.</td>
</tr>


<tr>
<td class="org-left">increments</td>
<td class="org-left">Resolution for density plots. Number of cells in x and y direction.</td>
</tr>
</tbody>
</table>


<a id="orgd9b028e"></a>

## The dimensions of latsave/lonsave

The matrices latsave and lonsave are in the output from the PTM. They have 4 dimensions:

[no. of particles x no. of release days x no. of release months x no. of units of time]

The parameters days<sub>indices</sub>, months<sub>indices</sub> and time<sub>indices</sub> include the indices of latsave/lonsave that are of interest and are used to 'slice' these matrices.


<a id="org0b70a20"></a>

## Specifying the shape of latsave/lonsave

The parameter shape<sub>check</sub> should express the dimensions, as described above, and is required by the Python programmes to aid reading the MATLAB .mat files. The Python package used to achieve this can 'flatten' matrices and this avoids any unwanted problems.


<a id="org2157bd8"></a>

## Python and MATLAB indexing

A difference between MATLAB and Python is that the former uses indices that start from 1, whereas the latter starts from 0. This can cause problems. For the parameters days<sub>indices</sub>, months<sub>indices</sub> and time<sub>indices</sub> use the MATLAB method of indexing (starting from 1). The Python programmes will convert these to Python appropriate indexing.


<a id="org637d97a"></a>

## Choosing whether to save release site-specific information

If both keep<sub>polygon</sub><sub>mats</sub> and keep<sub>polygon</sub><sub>shapefiles</sub> are set to 0, the directories created for each release site, which will contain the shapefiles created during running, will be deleted. If either, or both, are set to 1, they will be left in place to hold what you have specified retaining. 


<a id="org4052c97"></a>

# Running on SCW

A slurm file is required to run a programme on SCW. It is run using a command like

    sbatch run_plot_connectivity.slurm

It then enters a queue, until the requested resources are available to run the programme. To see if it is running, type

    squeue -u [your user id]


<a id="org48ecd67"></a>

## Slurm input files

Slurm files are included, which can be used to run the python programmes. The table below summarises relevant parameters that can be edited. Tweaking these parameters is a balancing act of optimising the performance of your programme and not getting stuck in the queue waiting for resources to be come available.

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Parameter</th>
<th scope="col" class="org-left">Description</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">cpus-per-task</td>
<td class="org-left">Number of processors per task.</td>
</tr>


<tr>
<td class="org-left">mem</td>
<td class="org-left">The amount of RAM (memory). The G stands for gigabytes.</td>
</tr>


<tr>
<td class="org-left">time</td>
<td class="org-left">The number of time required, in format HH:MM:SS.</td>
</tr>
</tbody>
</table>

The time parameter is difficult to set, because until you have run the programme, you don't know how long it will take. Once you have run it a few times you will have a better idea. Enter too short an amount of time and your programme will stop before it finishes, but the more time you request, the longer you will queue. If you don't enter a time, the default is 3 days, which is also the upper limit. Request too much resources and you might be stuck in the queue for days. So effort to optimise this is worth while.

At the bottom of the file is the command to run the Python programme, with the final argument referring to the parameters input file.


<a id="orgb3d899c"></a>

## Slurm output files

For each run, two output files are created and can be found in the directory called slurm<sub>output</sub>. One contains any output from the programme (print commands) and the other holds any error messages.

