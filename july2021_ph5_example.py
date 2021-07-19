import os
import logging

import fsspec
from fsspec_reference_maker import hdf, ph5
import json
import glob


#%% Consts
PH5_FOLDER = '/mnt/hgfs/ssd_tmp/ph5_19-003_example/'
OUTDIR = 'results_20210718/ph5_19-003_example/'

# PH5_FOLDER = '/mnt/hgfs/ssd_tmp/ph5_example/'
# OUTDIR = 'results_20210718/ph5_example/'
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)

# Some nicer logging
DEBUG_LOG = os.path.join(OUTDIR, 'debug.log')
if os.path.exists(DEBUG_LOG):
    os.remove(DEBUG_LOG) # remove old log

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.DEBUG,
                    handlers=[
                        logging.FileHandler(DEBUG_LOG),
                        logging.StreamHandler()
                    ]
                    )
logger = logging.getLogger(__name__)

for ph5_filename in glob.glob(PH5_FOLDER+'*.ph5'):
    logger.info(f'Loading {ph5_filename}')
    ph5_basename = os.path.splitext(os.path.basename(ph5_filename))[0]
    ref_outfile = os.path.join(OUTDIR, f'{ph5_basename}_ref_fs.json')

    # Open PH5 file
    fs = fsspec.filesystem('file')
    ph5master_example = fs.open(ph5_filename)

    # Translate PH5 Master file
    # h5chunks = hdf.SingleHdf5ToZarr(ph5master_example, '') # Throws error decoding metadata: 0

    # Use simple clone of hdf.py but skipping nested and zero strucures
    h5chunks = ph5.SingleHdf5ToZarr(ph5master_example, '')
    ph5master_reference_json = h5chunks.translate()

    ph5master_example.close()

    with open (ref_outfile, 'w+') as outfp:
        json.dump(ph5master_reference_json, outfp, indent=2, sort_keys=True) # Pretty print json

    # #%% Future debug
    # recv_keys = h5chunks._h5f['Experiment_g']['Receivers_g'].keys() # do see the Das keys
    # # das_obj = h5chunks._h5f['Experiment_g']['Receivers_g']['Das_g_1X101']
    # # Throws 'KeyError: "Unable to open object (unable to open external file, external link file name = './miniPH5_00001.ph5')"'
