# ODL Reader

This is a Python parser to read Object Description Language labels from NASA PDS3 archives.
[The full standards reference][1]

## Description

There are already numerous readers to parse [PDS ODL labels][2] .
This is a simple, no bloat, no dependency but fault intolerant reader.
The `odl.ODL()` class can parse ODL labels, whether they are in standalone `.LBL` files or embedded at the beginning of `.IMG` (image) files. The related `img.py` module provides functions to read the associated image data.


## Use

The primary class for parsing labels is `odl.ODL`.

### Parsing a standalone .LBL file:
```python
import odl, json

label_parser = odl.ODL()

# Example with a detached .LBL file
lbl_file_path = 'samples/3531ML1023500011404703C00_DRXX.LBL'
# (ensure this file is downloaded via samples/get_samples.sh)

with open(lbl_file_path, 'r') as infile:
    label_dict = label_parser.parse(infile)
    # print(json.dumps(label_dict, indent=2))

# Accessing values is shown further below.
```

### Parsing an .IMG file with an embedded label:
```python
import odl, json

label_parser_for_img = odl.ODL()

# Example with an .IMG file containing an embedded label
img_file_embedded_label_path = 'samples/4264MR1062180161604559I01_DXXX.IMG'
# (ensure this file is downloaded via samples/get_samples.sh)

with open(img_file_embedded_label_path, 'r') as infile:
    # The parser will read the text label and stop before the binary image data
    label_from_img = label_parser_for_img.parse(infile)
    # print(json.dumps(label_from_img, indent=2))

# Accessing values is similar for both types of parsed labels.
# For example, to get PRODUCT_ID from the label parsed from the IMG file:
# product_id = label_parser_for_img.get('PRODUCT_ID')
# print(f"Product ID from IMG: {product_id}")
```

<details>
<summary>Sample parse to JSON</summary>

## ODL label
```
PDS_VERSION_ID                    = PDS3

/* FILE DATA ELEMENTS */

RECORD_TYPE                         = FIXED_LENGTH
RECORD_BYTES                        = 2656
FILE_RECORDS                        = 3563
LABEL_RECORDS                       = 11
/* Pointers to Data Objects */

^IMAGE = 12


/* Identification Data Elements */

MSL:ACTIVE_FLIGHT_STRING_ID         = "B"
DATA_SET_ID                         = "MSL-M-MASTCAM-4-RDR-IMG-V1.0"
DATA_SET_NAME                       = "MSL MARS MAST CAMERA 4 RDR IMAGE V1.0"
COMMAND_SEQUENCE_NUMBER             = 0
GEOMETRY_PROJECTION_TYPE            = RAW
IMAGE_ID                            = "3039ML0158730000507144C00"
IMAGE_TYPE                          = REGULAR
MSL:IMAGE_ACQUIRE_MODE              = IMAGE
INSTRUMENT_HOST_ID                  = MSL
INSTRUMENT_HOST_NAME                = "MARS SCIENCE LABORATORY"
INSTRUMENT_ID                       = MAST_LEFT
INSTRUMENT_NAME                     = "MAST CAMERA LEFT"
INSTRUMENT_SERIAL_NUMBER            = "3003"
FLIGHT_SOFTWARE_VERSION_ID          = "1105031458"
INSTRUMENT_TYPE                     = "IMAGING CAMERA"
INSTRUMENT_VERSION_ID               = FM
MSL:LOCAL_MEAN_SOLAR_TIME           = "Sol-03039M14:00:29.161"
LOCAL_TRUE_SOLAR_TIME               = "13:23:54"
MISSION_NAME                        = "MARS SCIENCE LABORATORY"
MISSION_PHASE_NAME                  = "EXTENDED SURFACE MISSION"
OBSERVATION_ID                      = "NULL"
PLANET_DAY_NUMBER                   = 3039
INSTITUTION_NAME                    = "MALIN SPACE SCIENCE SYSTEMS"
PRODUCT_CREATION_TIME               = 2021-02-22T20:41:55.833
PRODUCT_VERSION_ID                  = "V1.0"
PRODUCT_ID                          = "3039ML0158730000507144C00_DRXX"
SOURCE_PRODUCT_ID                   = "McamLImage_0667283696-56760-1"
MSL:INPUT_PRODUCT_ID                = "1"

...


/* IMAGE DATA ELEMENTS */

OBJECT                            = IMAGE
  INTERCHANGE_FORMAT              = BINARY
  LINES                           = 1184
  LINE_SAMPLES                    = 1328
  SAMPLE_TYPE                     = MSB_UNSIGNED_INTEGER
  SAMPLE_BITS                     = 16
  BANDS                           = 3
  BAND_STORAGE_TYPE               = BAND_SEQUENTIAL
  FIRST_LINE                      = 17
  FIRST_LINE_SAMPLE               = 161
  INVALID_CONSTANT                = "NULL"
  MINIMUM                         = "NULL"
  MAXIMUM                         = "NULL"
  MEAN                            = "NULL"
  MEDIAN                          = "NULL"
  STANDARD_DEVIATION              = "NULL"
  MISSING_CONSTANT                = "NULL"
  SAMPLE_BIT_MASK                 = 2#0000111111111111#
  SAMPLE_BIT_MODE_ID              = MMM_LUT0
  SAMPLE_BIT_METHOD               = "HARDWARE"
END_OBJECT                        = IMAGE

END
```

## JSON output
```json
{
  "PDS_VERSION_ID": "PDS3",
  "RECORD_TYPE": "FIXED_LENGTH",
  "RECORD_BYTES": "2656",
  "FILE_RECORDS": "3563",
  "LABEL_RECORDS": "11",
  "^IMAGE": "12",
  "MSL:ACTIVE_FLIGHT_STRING_ID": "\"B\"",
  "DATA_SET_ID": "\"MSL-M-MASTCAM-4-RDR-IMG-V1.0\"",
  "DATA_SET_NAME": "\"MSL MARS MAST CAMERA 4 RDR IMAGE V1.0\"",
  "COMMAND_SEQUENCE_NUMBER": "0",
  "GEOMETRY_PROJECTION_TYPE": "RAW",
  "IMAGE_ID": "\"3039ML0158730000507144C00\"",
  "IMAGE_TYPE": "REGULAR",
  "MSL:IMAGE_ACQUIRE_MODE": "IMAGE",
  "INSTRUMENT_HOST_ID": "MSL",
  "INSTRUMENT_HOST_NAME": "\"MARS SCIENCE LABORATORY\"",
  "INSTRUMENT_ID": "MAST_LEFT",
  "INSTRUMENT_NAME": "\"MAST CAMERA LEFT\"",
  "INSTRUMENT_SERIAL_NUMBER": "\"3003\"",
  "FLIGHT_SOFTWARE_VERSION_ID": "\"1105031458\"",
  "INSTRUMENT_TYPE": "\"IMAGING CAMERA\"",
  "INSTRUMENT_VERSION_ID": "FM",
  "MSL:LOCAL_MEAN_SOLAR_TIME": "\"Sol-03039M14:00:29.161\"",
  "LOCAL_TRUE_SOLAR_TIME": "\"13:23:54\"",
  "MISSION_NAME": "\"MARS SCIENCE LABORATORY\"",
  "MISSION_PHASE_NAME": "\"EXTENDED SURFACE MISSION\"",
  "OBSERVATION_ID": "\"NULL\"",
  "PLANET_DAY_NUMBER": "3039",
  "INSTITUTION_NAME": "\"MALIN SPACE SCIENCE SYSTEMS\"",
  "PRODUCT_CREATION_TIME": "2021-02-22T20:41:55.833",
  "PRODUCT_VERSION_ID": "\"V1.0\"",
  "PRODUCT_ID": "\"3039ML0158730000507144C00_DRXX\"",
  "SOURCE_PRODUCT_ID": "\"McamLImage_0667283696-56760-1\"",
  "MSL:INPUT_PRODUCT_ID": "\"1\"",


  "IMAGE/INTERCHANGE_FORMAT": "BINARY",
  "IMAGE/LINES": "1184",
  "IMAGE/LINE_SAMPLES": "1328",
  "IMAGE/SAMPLE_TYPE": "MSB_UNSIGNED_INTEGER",
  "IMAGE/SAMPLE_BITS": "16",
  "IMAGE/BANDS": "3",
  "IMAGE/BAND_STORAGE_TYPE": "BAND_SEQUENTIAL",
  "IMAGE/FIRST_LINE": "17",
  "IMAGE/FIRST_LINE_SAMPLE": "161",
  "IMAGE/INVALID_CONSTANT": "\"NULL\"",
  "IMAGE/MINIMUM": "\"NULL\"",
  "IMAGE/MAXIMUM": "\"NULL\"",
  "IMAGE/MEAN": "\"NULL\"",
  "IMAGE/MEDIAN": "\"NULL\"",
  "IMAGE/STANDARD_DEVIATION": "\"NULL\"",
  "IMAGE/MISSING_CONSTANT": "\"NULL\"",
  "IMAGE/SAMPLE_BIT_MASK": "2#0000111111111111#",
  "IMAGE/SAMPLE_BIT_MODE_ID": "MMM_LUT0",
  "IMAGE/SAMPLE_BIT_METHOD": "\"HARDWARE\""
}
```

</details>

## Reading Image Data

The `img.py` module provides helper functions to read the actual image data associated with a PDS3 label.

*   `img.read_lbl_img(lbl_path, [img_path])`: Use this when you have a detached label (an `.LBL` file). It parses the label file to get image parameters and then reads the image data from the corresponding `.IMG` file. If `img_path` is not provided, it infers the `.IMG` filename from the `lbl_path`.
    ```python
    import img
    # Assuming lbl_file_path = 'samples/3531ML1023500011404703C00_DRXX.LBL'
    # Ensure the corresponding .IMG file (3531ML1023500011404703C00_DRXX.IMG) is also in samples/
    # image_array = img.read_lbl_img(lbl_path=lbl_file_path)
    # print(f"Shape of image from LBL: {image_array.shape}, dtype: {image_array.dtype}")
    ```

*   `img.read_img(img_path)`: Use this when the ODL label is embedded within the `.IMG` file itself. This function first parses the embedded label from the `.IMG` file and then reads the image data from the same file, using pointers from the label (like `^IMAGE` and `RECORD_BYTES`) to locate the start of the image data.
    ```python
    import img
    # Assuming img_file_embedded_label_path = 'samples/4264MR1062180161604559I01_DXXX.IMG'
    # image_array_from_img = img.read_img(img_path=img_file_embedded_label_path)
    # print(f"Shape of image from IMG: {image_array_from_img.shape}, dtype: {image_array_from_img.dtype}")
    ```

## Value retrieval
After parsing a label (either from an `.LBL` or an embedded label in `.IMG`) into a dictionary using `odl.ODL().parse()`, you can retrieve values:

### Using the returned dictionary
(Assuming `label_dict` holds the parsed label from examples above)
```python
record_type = label_dict.get( 'RECORD_TYPE' )  # returns "FIXED_LENGTH"
# num_lines   = label_dict.get( 'IMAGE/LINES') # Note: Grouped items are like 'IMAGE/LINES'
```

### Or using ODL object with optional type conversion
```python
record_type = label.get( 'RECORD_TYPE' )             # returns "FIXED_LENGTH" 
num_lines   = label.get( 'IMAGES/LINES', cast=int )  # returns 1184 as an integer
```

## Data Types

While the return of parse() is a dictionary, it might be useful to fetch the values with a cast on retrieval.
This is especially useful if the values are an array.  All elements are converted.
Use the parser instead of the dictionary.
```
label_parser.get_array( 'PROCESSING_PARMS/RADIANCE_SCALING_FACTOR', cast=float )
[0.0001693, 0.0001568, 0.0001463]
```

There are two functions that will convert ISO 8660 time strings (common in PDS3 archive labels).  
* odl.ISOC converts times in calendar format like 2021-02-22T20:41:55.833
* odl.ISOD converts times in day of year format like Sol-03039M14:00:29.161

```python
label_parser.get( 'START_TIME', cast=odl.ISOC )
datetime.datetime(2021, 2, 22, 17, 19, 39, 36000)

label_parser.get( 'MSL:LOCAL_MEAN_SOLAR_TIME', cast=odl.ISOD )
(3039, datetime.time(14, 0, 29, 161000))
```

## Get Sample data

The `samples/get_samples.sh` script is provided to download the necessary sample files for testing and examples. Run it from the root of the repository:
```bash
bash samples/get_samples.sh
```
This script will download:
*   `samples/3531ML1023500011404703C00_DRXX.LBL` (a detached label file)
*   `samples/3531ML1023500011404703C00_DRXX.IMG` (the image data file for the LBL above)
*   `samples/4264MR1062180161604559I01_DXXX.IMG` (an image file with an embedded ODL label)

Alternatively, you can download them manually:
```
# Detached label and its corresponding image file
curl -o samples/3531ML1023500011404703C00_DRXX.LBL https://planetarydata.jpl.nasa.gov/img/data/msl/MSLMST_0031/DATA/RDR/SURFACE/3531/3531ML1023500011404703C00_DRXX.LBL
curl -o samples/3531ML1023500011404703C00_DRXX.IMG https://planetarydata.jpl.nasa.gov/img/data/msl/MSLMST_0031/DATA/RDR/SURFACE/3531/3531ML1023500011404703C00_DRXX.IMG

# Image file with an embedded label
curl -o samples/4264MR1062180161604559I01_DXXX.IMG https://planetarydata.jpl.nasa.gov/img/data/msl/msl_mmm/data_MSLMST/volume_0038_raw/SURFACE/4264/4264MR1062180161604559I01_DXXX.IMG
```
(Ensure the `samples/` directory exists if downloading manually.)


[1]: https://pds.nasa.gov/datastandards/pds3/standards/sr/StdRef_20090227_v3.8.pdf  
[2]: https://ode.rsl.wustl.edu/mars/pagehelp/Content/Introduction/Data_Standards.htm
