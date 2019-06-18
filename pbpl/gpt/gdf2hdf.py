#!/usr/bin/env python
import sys, os
import argparse
from argparse import RawDescriptionHelpFormatter
import numpy as np
import h5py
import subprocess
from pbpl.units import *

def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description='Convert GDF to HDF5',
        epilog='Example:\n' +
        '  > pbpl-gpt-convert result.gdf\n' +
        "Reads 'result.hdf' and writes 'result.h5'")
    parser.add_argument(
        '--output', metavar='HDF5',# default=None,
        help='Specify output filename')
    parser.add_argument(
        'input', metavar='GDF',
        help='GDF input filename')
    return parser

def get_args():
    parser = get_parser()
    args = parser.parse_args()
    if args.output == None:
        args.output = os.path.splitext(args.input)[0] + '.h5'
    return args

def read_frame(f):
    read_ahead = f.readline()
    if read_ahead.strip() == '':
        raise(EOFError)
    time = float(read_ahead[4:])
    cols = f.readline().split()
    data = []
    for x in f:
        x = x.strip()
        if x == '':
            break
        data.append([float(y) for y in x.split()])
    data = np.array(data, dtype=np.float32)
    return time, cols, data

def main():
    args = get_args()
    time = []
    data = []
    with subprocess.Popen(
            ['gdf2a', '-w 16', args.input],
            stdout=subprocess.PIPE, bufsize=1,
            universal_newlines=True) as p:
        fin = p.stdout
        fin.readline()
        fin.readline()
        fin.readline()
        while True:
            try:
                frame_time, cols, frame_data = read_frame(fin)
            except EOFError:
                break
            time.append(frame_time)
            data.append(frame_data)
#    data = np.moveaxis(np.array(data, dtype=np.float32), 0, 1)
    data = np.array(data, dtype=np.float32)
    cols = dict(zip(cols, range(len(cols))))

    fout = h5py.File(args.output, 'w')

    if {'x', 'y', 'z'} <= cols.keys():
        fout['pos'] = np.array(
            (data[:,:,cols['x']],data[:,:,cols['y']],data[:,:,cols['z']])).T

    if {'Bx', 'By', 'Bz'} <= cols.keys():
        fout['beta'] = np.array(
            (data[:,:,cols['Bx']],data[:,:,cols['By']],data[:,:,cols['Bz']])).T

    if {'G'} <= cols.keys():
        fout['gamma'] = np.moveaxis(data[:,:,cols['G']], 0, 1)

    fout.close()

if __name__ == '__main__':
    sys.exit(main())
