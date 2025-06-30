#!/bin/bash

# Ensure script exits on error
set -e

# Create the samples directory if it doesn't exist
# And change into it to download files there
mkdir -p samples
cd samples

echo "Downloading sample files required for testing..."

# Used by test_odl.py and test_img.py (detached label and its image)
curl -O https://planetarydata.jpl.nasa.gov/img/data/msl/MSLMST_0031/DATA/RDR/SURFACE/3531/3531ML1023500011404703C00_DRXX.LBL
curl -O https://planetarydata.jpl.nasa.gov/img/data/msl/MSLMST_0031/DATA/RDR/SURFACE/3531/3531ML1023500011404703C00_DRXX.IMG

# Used by test_odl.py and test_img.py (IMG file with embedded label)
curl -O https://planetarydata.jpl.nasa.gov/img/data/msl/msl_mmm/data_MSLMST/volume_0038_raw/SURFACE/4264/4264MR1062180161604559I01_DXXX.IMG

echo "Sample files downloaded."

# Return to the original directory
cd ..
