#!/usr/bin/env python

import odl
import img
import json # For pretty printing the label (optional)
import os # For checking file existence if needed

# Define paths to known existing sample files
SAMPLE_LBL_FILE = 'samples/3531ML1023500011404703C00_DRXX.LBL'
# SAMPLE_IMG_FILE is inferred by read_lbl_img or can be specified by the user

def main():
    print(f"--- Demonstrating odl.py with {SAMPLE_LBL_FILE} ---")

    if not os.path.exists(SAMPLE_LBL_FILE):
        print(f"Error: Sample LBL file not found: {SAMPLE_LBL_FILE}")
        print("Please ensure samples are downloaded (e.g., by running samples/get_samples.sh).")
        return

    label_parser = odl.ODL()

    # Parse the LBL file
    print(f"Parsing {SAMPLE_LBL_FILE}...")
    with open(SAMPLE_LBL_FILE, 'r', encoding='latin-1') as infile:
        label_data = label_parser.parse(infile)

    if not label_data:
        print("Failed to parse label data or label data is empty.")
        return

    # Example: Get specific values using the parser instance
    pds_version = label_parser.get('PDS_VERSION_ID')
    print(f"PDS Version ID: {pds_version}")

    planet_day = label_parser.get('PLANET_DAY_NUMBER', cast=int)
    print(f"Planet Day Number: {planet_day}")

    product_creation_time_str = label_parser.get('PRODUCT_CREATION_TIME')
    # Using a default for ISOC in case the key isn't there, though it should be for this file
    default_dt_isoc = "Unknown"
    product_creation_time_dt = label_parser.get('PRODUCT_CREATION_TIME', cast=odl.ISOC) if product_creation_time_str else default_dt_isoc

    print(f"Product Creation Time (string): {product_creation_time_str}")
    print(f"Product Creation Time (datetime): {product_creation_time_dt}")

    # Example: Get an array
    rover_motion_counter = label_parser.get_array('ROVER_MOTION_COUNTER', cast=int)
    print(f"Rover Motion Counter: {rover_motion_counter}")

    print(f"\n--- Demonstrating img.py with {SAMPLE_LBL_FILE} ---")
    # Read image data using the LBL file (IMG file will be inferred)
    try:
        print(f"Attempting to read image data associated with {SAMPLE_LBL_FILE} using img.read_lbl_img()...")
        image_data = img.read_lbl_img(lbl_path=SAMPLE_LBL_FILE)
        print(f"Image read successfully using read_lbl_img.")
        print(f"Image shape: {image_data.shape} (Bands, Lines, Samples)")
        print(f"Image dtype: {image_data.dtype}")

        # Example of what one might do with the image (requires numpy, which img.py uses)
        if image_data.size > 0:
            print(f"Min value in image: {image_data.min()}")
            print(f"Max value in image: {image_data.max()}")
            print(f"Mean value in image: {image_data.mean()}")

    except FileNotFoundError as fnf_error:
        print(f"FileNotFoundError: {fnf_error}")
        print(f"This likely means the corresponding IMG file for {SAMPLE_LBL_FILE} was not found where expected.")
    except Exception as e:
        print(f"An error occurred while reading the image with read_lbl_img: {e}")

    print("\n--- Demonstrating img.read_img() with an IMG file having an embedded label ---")
    SAMPLE_IMG_WITH_EMBEDDED_LABEL = 'samples/4264MR1062180161604559I01_DXXX.IMG'
    if os.path.exists(SAMPLE_IMG_WITH_EMBEDDED_LABEL):
        try:
            print(f"Attempting to read image and embedded label from {SAMPLE_IMG_WITH_EMBEDDED_LABEL} using img.read_img()...")
            # UnicodeDecodeError warning from odl.py is expected here and normal.
            image_data_from_img = img.read_img(img_path=SAMPLE_IMG_WITH_EMBEDDED_LABEL)
            print(f"Image read successfully using read_img.")
            print(f"Image shape: {image_data_from_img.shape} (Bands, Lines, Samples)")
            print(f"Image dtype: {image_data_from_img.dtype}")
            if image_data_from_img.size > 0:
                print(f"Min value in image: {image_data_from_img.min()}")
                print(f"Max value in image: {image_data_from_img.max()}")
        except FileNotFoundError:
            print(f"Error: Sample IMG file with embedded label not found: {SAMPLE_IMG_WITH_EMBEDDED_LABEL}")
        except Exception as e:
            print(f"An error occurred while reading the image with read_img: {e}")
    else:
        print(f"Skipping img.read_img() demonstration as sample file not found: {SAMPLE_IMG_WITH_EMBEDDED_LABEL}")


if __name__ == '__main__':
    main()
