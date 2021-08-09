import os
import logging

import fsspec
from fsspec_reference_maker import hdf
import json
import glob


#%% Consts
FOLDER = '/mnt/hgfs/ssd_tmp/'
OUTDIR = 'results_live/das_h5/'

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

h5_filename = os.path.join(FOLDER, 'das_example.h5')
uri = f'file://{h5_filename}'
logger.info(f'Loading {h5_filename}')
h5_basename = os.path.splitext(os.path.basename(h5_filename))[0]
ref_outfile = os.path.join(OUTDIR, f'{h5_basename}_ref_fs.json')

# Open PH5 file
fs = fsspec.filesystem('file')
h5master_example = fs.open(h5_filename)

# Translate PH5 Master file
h5chunks = hdf.SingleHdf5ToZarr(h5master_example, uri)
h5master_reference_json = h5chunks.translate()

h5master_example.close()

with open (ref_outfile, 'w+') as outfp:
    json.dump(h5master_reference_json, outfp, indent=2, sort_keys=True) # Pretty print json
