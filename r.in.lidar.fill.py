#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################################
#
# MODULE:       r.in.lidar.fill
# AUTHOR(S):    Anna Petrasova
# PURPOSE:      Wrapper for r.in.lidar
# COPYRIGHT:    (C) 2017 by Anna Petrasova, and the GRASS Development Team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
############################################################################

#%module
#% description: Creates a DEM map from LAS LiDAR and fills empty cells.
#% keyword: raster, import, LIDAR, statistics, conversion, binning
#%end
#%option
#% key: input
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% label: LAS input file
#% description: LiDAR input files in LAS format (*.las or *.laz)
#% gisprompt: old,bin,file
#% guisection: Input
#%end
#%flag
#% key: p
#% label: Preserve original cell values
#% description: By default original values are smoothed
#%end
#%flag
#% key: o
#% label: Override projection check (use current location's projection)
#% description: Assume that the dataset has same projection as the current location
#%end
#%flag
#% key: s
#% description: Scan data file for extent then exit
#%end
#%flag
#% key: e
#% label: Use the extent of the input for the raster extent
#% description: Set internally computational region extents based on the point cloud
#% guisection: Output
#%end
#%option
#% key: output
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% description: Name for output raster map
#% gisprompt: new,cell,raster
#% guisection: Output
#%end
#%option
#% key: file
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% label: File containing names of LAS input files
#% description: LiDAR input files in LAS format (*.las or *.laz)
#% gisprompt: old,file,file
#% guisection: Input
#%end
#%option
#% key: zrange
#% type: double
#% required: no
#% multiple: no
#% key_desc: min,max
#% label: Filter range for Z data (min,max)
#% description: Applied after base_raster transformation step
#%end
#%option
#% key: resolution
#% type: double
#% required: no
#% multiple: no
#% description: Output raster resolution
#% guisection: Output
#%end
#%option
#% key: return_filter
#% type: string
#% required: no
#% multiple: no
#% options: first,last,mid
#% label: Only import points of selected return type
#% description: If not specified, all points are imported
#%end
#%option
#% key: class_filter
#% type: integer
#% required: no
#% multiple: yes
#% label: Only import points of selected class(es)
#% description: Input is comma separated integers. If not specified, all points are imported.
#%end
#%option
#% key: distance
#% type: double
#% required: yes
#% multiple: no
#% key_desc: value
#% description: Distance threshold in cells for interpolation of larger gaps
#% answer: 3
#% guisection: Interpolation
#%end
#%option
#% key: power
#% type: double
#% required: yes
#% multiple: no
#% key_desc: value
#% description: Power coefficient for IDW interpolation for larger gaps
#% answer: 5.0
#% guisection: Interpolation
#%end
import sys
import atexit

import grass.script as gscript

TMP = []


def cleanup():
    if TMP:
        gscript.run_command('g.remove', type='raster', name=TMP, flags='f')


def main():
    out = options.pop('output')
    fill_distance = options.pop('distance')
    power = options.pop('power')
    tmpout = 'r_in_lidar_fill_tmp'
    tmpout2 = 'r_in_lidar_fill_tmp2'
    TMP.append(tmpout)
    TMP.append(tmpout2)
    fl = ''
    pflag = ''
    for flag in flags:
        if flag == 'p':
            pflag = 'p'
            continue
        if flags[flag]:
            fl += flag

    op = {}
    for key in options:
        if options[key]:
            op.update({key: options[key]})

    gscript.run_command('r.in.lidar', output=tmpout, flags=fl, **op)
    gscript.use_temp_region()
    gscript.run_command('g.region', raster=tmpout)
    gscript.run_command('r.fill.gaps', input=tmpout, output=tmpout2, flags=pflag)
    gscript.run_command('r.fill.gaps', input=tmpout2, output=out, power=power,
                        distance=fill_distance, flags='p')

    return 0

if __name__ == "__main__":
    options, flags = gscript.parser()
    atexit.register(cleanup)
    sys.exit(main())
