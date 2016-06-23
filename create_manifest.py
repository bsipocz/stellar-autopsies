# Manifest file generator for Stellar Autopsies
#

import os
from astropy.table import Table

lcs = os.listdir('plots')
sample = Table.read('OpenSupernovaCatalog.csv')

meta = []
metanames = ['subject_id', 'image_name', '#Type', '#RA', '#Dec']

for i, lcname in enumerate(lcs):
    name = lcname.split('_')[0]
    ty = sample[sample['Name'] == name]['Type'][0]
    ra = sample[sample['Name'] == name]['R.A.'][0].split(',')[0]
    dec = sample[sample['Name'] == name]['Dec.'][0].split(',')[0]

    meta.append((i + 1, lcname, ty, ra, dec))

metatable = Table(rows=meta, names=metanames)

metatable.write('plots/manifest.csv', format='csv')
