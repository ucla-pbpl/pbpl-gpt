#!/usr/bin/env python
import sys, os
import argparse
from argparse import RawDescriptionHelpFormatter
from tempfile import NamedTemporaryFile
import numpy as np
import h5py
import subprocess
from pbpl.units import *

def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description='Convert GDF to HDF5',
        epilog='Example:\n' +
        '  > pbpl-gpt-convert result.gdf avgz avgG\n' +
        "Reads 'result.hdf' and writes 'result.h5', including fields" +
        "for avgz and avgG")
    parser.add_argument(
        '--output', metavar='HDF5',# default=None,
        help='Specify output filename')
    parser.add_argument(
        'input', metavar='GDF',
        help='GDF input filename')
    parser.add_argument(
        'calc', metavar='CALC', nargs='*',
        help='Optional derived quantities. Legal values: ' +
        'avg (all averaged quantities), std (all rms quantities), ' +
        'avgx, avgy, avgz, avgBx, avgBy, avgBz, avgG, avgp, ' +
        'stdx, stdy, stdz, stdBx, stdBy, stdBz, stdG')
    return parser

def get_args():
    parser = get_parser()
    args = parser.parse_args()
    if args.output == None:
        args.output = os.path.splitext(args.input)[0] + '.h5'
    return args

def scan_unframed_gdf(filename):
    with subprocess.Popen(
            ['gdf2a', '-w 16', filename],
            stdout=subprocess.PIPE, bufsize=1,
            universal_newlines=True) as p:
        fin = p.stdout
        cols = fin.readline().split()[1:]
        N = len(cols)
        cols = dict(zip(cols, range(N)))
        data = np.loadtxt(fin, dtype=np.float32, usecols=range(1,N+1)).T
    return cols, data

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

def scan_framed_gdf(filename):
    time = []
    data = []
    with subprocess.Popen(
            ['gdf2a', '-w 16', filename],
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
    time = np.array(time, dtype=np.float32)
    data = np.rollaxis(np.array(data, dtype=np.float32), 2)
    cols = dict(zip(cols, range(len(cols))))
    return time, cols, data

def main():
    args = get_args()

    time, cols, data = scan_framed_gdf(args.input)

    calc_vars = set(args.calc)
    if len(calc_vars) > 0:
        if 'avg' in calc_vars:
            calc_vars.update(
                ['avg' + x for x in
                 ['x', 'y', 'z', 'r', 'Bx', 'By', 'Bz', 'G']])
            calc_vars.remove('avg')
        if 'std' in calc_vars:
            calc_vars.update(
                ['std' + x for x in
                 ['x', 'y', 'z', 'Bx', 'By', 'Bz', 'G']])
            calc_vars.remove('std')
        f = NamedTemporaryFile()
        calc_filename = f.name
        f.close()
        subprocess.call(
            ['gdfa', '-o ' + calc_filename, args.input,
             'time', *calc_vars])
        calc_cols, calc_data = scan_unframed_gdf(calc_filename)

    fout = h5py.File(args.output, 'w')
    for k, v in cols.items():
        fout[k] = data[v]
    fout['t'] = time
    if len(calc_vars) > 0:
        for k, v in calc_cols.items():
            fout[k] = calc_data[v]
    fout.close()

if __name__ == '__main__':
    sys.exit(main())
