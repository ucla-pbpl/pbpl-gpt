# -*- coding: utf-8 -*-
import sys, math, os
import argparse
from argparse import RawDescriptionHelpFormatter
import toml
import asteval
import numpy as np
import h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot
from matplotlib.backends.backend_pdf import PdfPages
from pbpl.units import *
from .core import setup_plot

def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description='Plot phase space',
        epilog='Example:\n' +
        '  > pbpl-gpt-plot-phase-space plot-phase-space.toml result.h5\n' +
        "Reads 'result.h5' and writes 'result.pdf'")
    parser.add_argument(
        '--output', metavar='PDF',# default=None,
        help='Specify output filename')
    parser.add_argument(
        'config_filename', metavar='conf-file',
        help='Configuration file (TOML format)')
    parser.add_argument(
        'input_filename', metavar='in-file',
        help='Input filename (HDF5 format)')
    return parser

def get_args():
    parser = get_parser()
    args = parser.parse_args()
    if args.output == None:
        args.output = os.path.splitext(args.input_filename)[0] + '.pdf'
    args.conf = toml.load(args.config_filename)
    return args

def plot_frame(output, step, xaxis, yaxis, aeval):
    # fig = plot.figure(figsize=(244.0/72, 140.0/72))
    fig = plot.figure(figsize=(160.0/72, 140.0/72))
    ax = fig.add_subplot(1, 1, 1, aspect=1.0)

    ax.plot(
        aeval(xaxis['value']), aeval(yaxis['value']),
        marker='o', ls='', markersize=0.5, markeredgewidth=0,
        color='#0083b8', alpha=0.7)

    ax.set_xlabel(xaxis['title'], labelpad=0.0)
    ax.set_ylabel(yaxis['title'], labelpad=0.0)

    ax.set_xlim(xaxis['min'], xaxis['max'])
    ax.set_ylim(yaxis['min'], yaxis['max'])

    ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())

    ax.text(
        0.05, 0.9,
#        'z = {:.1f} mm'.format(aeval('zavg')/mm),
        aeval("'z = {:.1f} mm'.format(avgz/mm)"),
        transform=ax.transAxes, fontsize=7)

    output.savefig(fig, transparent=True)


def scan_hdf(conf, input_filename):
    i0 = conf['i0']
    i1 = conf['i1']
    if i1 == -1:
        i1 = None
    istep = conf['istep']
    num_particles = conf['num_particles']
    if num_particles == -1:
        num_particles = None

    f = h5py.File(input_filename, 'r')
    result = {}
    for k, v in f.items():
        is_micro = (len(v.shape) == 2)
        if is_micro:
            result[k] = f[k][i0:i1:istep][0:num_particles]
        else:
            result[k] = f[k][i0:i1:istep]
    f.close()
    return result

def main():
    args = get_args()
    conf = args.conf

    data = scan_hdf(conf['input'], args.input_filename)
    num_steps = len(data['t'])

    setup_plot()

    # create safe interpreter for evaluation of scale expressions
    aeval = asteval.Interpreter()
    import pbpl.units
    for x in pbpl.units.__all__:
        aeval.symtable[x] = pbpl.units.__dict__[x]

    output = PdfPages(args.output)
    for i in range(num_steps):
        for k, x in data.items():
            aeval.symtable[k] = x[i]
        plot_frame(
            output, i, conf['xaxis'], conf['yaxis'], aeval)
    output.close()
        # f = h5py.File('{}_{:04}.h5'.format(args.input_path, i), 'r')
        # particles = f['particles'].value.T
        # N = args.input_num_particles
        # if N == -1:
        #     N = particles.shape[1]
        # particles = particles[:, 0:N]

        # # reference particle
        # m0 = f['mass'].value * (GeV/c_light**2)
        # p0 = f['pz'].value * (GeV/c_light)
        # # beta0 = p0 / np.sqrt((m0 * c_light)**2 + p0**2)
        # # gamma0 = 1 / np.sqrt(1 - beta0**2)
        # gamma0 = np.sqrt(1 + (p0/(m0 * c_light))**2)
        # beta0 = np.sqrt(1 - (1/gamma0**2))

        # x = particles[0] * meter
        # px = particles[1] * p0
        # y = particles[2] * meter
        # py = particles[3] * p0
        # cdt = particles[4] * meter
        # deltap = particles[5] * p0
        # zeta = -beta0 * cdt
        # p = p0 + deltap
        # pz = np.sqrt(p**2 - px**2 - py**2)
        # dpz = pz - p0
        # gamma = np.sqrt(1 + (p/(m0 * c_light))**2)
        # beta = np.sqrt(1 - (1/gamma**2))
        # vz = (p0 + deltap) / (gamma * m0)
        # v0 = beta0 * c_light
        # print(px/p0)
        # print(py/p0)
        # print(dpz/p0)

        # aeval.symtable['m0'] = m0
        # aeval.symtable['p0'] = p0
        # aeval.symtable['gamma0'] = gamma0
        # aeval.symtable['beta0'] = beta0

        # aeval.symtable['x'] = x
        # aeval.symtable['px'] = px
        # aeval.symtable['y'] = y
        # aeval.symtable['py'] = py
        # aeval.symtable['zeta'] = zeta
        # aeval.symtable['deltap'] = deltap
        # aeval.symtable['p'] = p
        # aeval.symtable['pz'] = pz
        # aeval.symtable['dpz'] = dpz

        # aeval.symtable['vz'] = vz
        # aeval.symtable['v0'] = v0


if __name__ == '__main__':
    sys.exit(main())
