# Light curve plotter script for Stellar Autopsies
#

import json
import logging
import matplotlib.pylab as plt

from astropy.table import Table
from astropy.time import Time
from astropy.coordinates import Distance

logger = logging.getLogger()
log_handler = logging.StreamHandler()
log_handler.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
log_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(message)s"))
logger.addHandler(log_handler)


sample = Table.read('OpenSupernovaCatalog.csv')

bands = ['R', 'r', "r'"]

for name in sample['Name']:
    try:
        with open('data/all_sne/{0}.json'.format(name)) as data_file:
            sne = json.load(data_file)
    except FileNotFoundError:
        logger.warning("{0} datafile is missing".format(name))
        continue

    for sn in sne:
        sn = sne[sn]
    name = sn['name']

    lc = sn.get('photometry')

    if lc is None:
        logger.warning("There is no photometry for {0}".format(name))

    try:
        zSn = float(sn['redshift'][0]['value'])
    except KeyError:
        logger.warning("There is no redshift for {0}, using z=0 instead".format(name))
        zSn = 0
    muSn = Distance(z=zSn).distmod.value

    try:
        maxdate = Time('-'.join(sn['maxdate'][0]['value'].split('/'))).mjd
    except KeyError:
        logger.warning("No maxdate for {0}".format(name))
        continue

    for band in bands:
        mags = [float(lc[i]['magnitude']) for i in range(len(lc))
                if lc[i].get('band') == band]
        time = [float(lc[i]['time']) - maxdate for i in range(len(lc))
                if lc[i].get('band') == band]
        lc_table = Table([time, mags], names=['time', 'mags'])

        if len(mags) == 0:
            continue
        plt.clf()
        plt.scatter(lc_table['time'] / (1 + zSn), lc_table['mags'] - muSn)
        plt.ylim(-15, -20)
        plt.xlim(-20, 100)
        plt.xlabel('Days after maximum')
        plt.ylabel('Absolute magnitude')
        plt.grid()
        plt.minorticks_on()
        plt.savefig("plots/{0}_{1}".format(name, band))
