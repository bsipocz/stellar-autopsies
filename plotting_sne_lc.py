# Light curve plotter script for Stellar Autopsies
#

import datetime
import json
import requests
import logging
import matplotlib.pylab as plt
import numpy as np

from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import Distance

timestamp = datetime.datetime.today().strftime("%Y-%m-%d_%H%M")

logger = logging.getLogger()
log_handler = logging.StreamHandler()
log_handler.setLevel(logging.DEBUG)
logfile_handler = logging.FileHandler('logs/plotting_' + timestamp + '.log')
logfile_handler.setLevel(logging.DEBUG)
logfile_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(message)s"))
logger.setLevel(logging.DEBUG)
log_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(message)s"))

logger.addHandler(log_handler)
logger.addHandler(logfile_handler)

sample = Table.read('OpenSupernovaCatalog.csv')

bands = ['R', 'r', "r'"]

write_text_lc = False
plot_figure = False

time_range = (-20, 100)
mag_range = (-15, -20)

mindata = 10


for name in sample['Name']:
    # We assume that the data files are already downloaded and available as
    # json files and if not we download them from the website
    # https://sne.space/
    try:
        with open('data/all_sne/{0}.json'.format(name)) as data_file:
            sne = json.load(data_file)
    except FileNotFoundError:
        logger.warning("{0} datafile is missing locally".format(name))
        sne = requests.get('http://sne.space/sne/{0}.json'.format(name)).json()

    for sn in sne:
        sn = sne[sn]
    name = sn['name']

    lc = sn.get('photometry')

    if lc is None:
        logger.warning("There is no photometry for {0}".format(name))

    try:
        zSn = float(sn['redshift'][0]['value'])
    except KeyError:
        logger.warning("There is no redshift for {0}, using z=0".format(name))
        zSn = 0
    muSn = Distance(z=zSn).distmod.value

    try:
        maxdate = Time('-'.join(sn['maxdate'][0]['value'].split('/'))).mjd
    except KeyError:
        logger.warning("No maxdate for {0}".format(name))
        continue

    for band in bands:
        mags = np.array([float(lc[i]['magnitude']) for i in range(len(lc))
                         if lc[i].get('band') == band])
        time = np.array([float(lc[i]['time']) - maxdate for i in range(len(lc))
                         if lc[i].get('band') == band])
        lc_table = Table([time, mags], names=['time', 'mags'])

        if len(mags) == 0:
            continue

        if ((time >= time_range[0]) & (time <= time_range[1])).sum() < mindata:

            logger.warning("There is less than {0} data points in time range "
                           "{1} days. Skipping {2} band {3}"
                           .format(mindata, time_range, name, band))

        if plot_figure:
            plt.clf()
            plt.scatter(lc_table['time'] / (1 + zSn), lc_table['mags'] - muSn)
            plt.ylim(-15, -20)
            plt.xlim(-20, 100)
            plt.xlabel('Days after maximum')
            plt.ylabel('Absolute magnitude')
            plt.grid()
            plt.minorticks_on()
            plt.savefig("plots/{0}_{1}".format(name, band))

        if write_text_lc:
            lc_table.write('{0}_{1}.txt'.format(name, band),
                           format='ascii.no_header')
