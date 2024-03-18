# ODL Reader

This is a Python parser to read Object Description Language labels from NASA PDS3 archives.
[The full standards reference][1]

## Description

There are already numerous readers to parse [PDS ODL labels][2] .
This is a simple, no bloat, no dependency but fault intolerant reader.
To read LBL files or the ODL header in an IMG file, use odl.ODL().


## Use

```python
import odl, json

# Class to read
label_parser = odl.ODL()

# Parse into a dictionary with group elements separated by /'s.
with open('samples/3039ML0158730000507144C00_DRXX.IMG', 'r' ) as infile:
    label = label_parser.parse(infile)
    print( json.dumps(label,indent=2) )

# Items may be fetched with
record_type = label.get( 'RECORD_TYPE' )           # returns "FIXED_LENGTH" 
num_lines   = label.get( 'IMAGES/LINES', cast=int )  # returns 1184 as an integer
```

```
  "PDS_VERSION_ID": "PDS3",
  "RECORD_TYPE": "FIXED_LENGTH",
  "RECORD_BYTES": "2656",
  "FILE_RECORDS": "3563",
  "LABEL_RECORDS": "11",
  "^IMAGE": "12",
  ...
  "IMAGE/INTERCHANGE_FORMAT": "BINARY",
  "IMAGE/LINES": "1184",
  "IMAGE/LINE_SAMPLES": "1328",
  "IMAGE/SAMPLE_TYPE": "MSB_UNSIGNED_INTEGER",
  "IMAGE/SAMPLE_BITS": "16",
  "IMAGE/BANDS": "3",
  "IMAGE/BAND_STORAGE_TYPE": "BAND_SEQUENTIAL",
  "IMAGE/FIRST_LINE": "17",
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
* odl.ISOC() converts times in calendar format like 2021-02-22T20:41:55.833
* odl.ISOD() converts times in day of year format like Sol-03039M14:00:29.161

```
label_parser.get( 'START_TIME', cast=odl.ISOC )
datetime.datetime(2021, 2, 22, 17, 19, 39, 36000)

label_parser.get( 'MSL:LOCAL_MEAN_SOLAR_TIME', cast=odl.ISOD )
(3039, datetime.time(14, 0, 29, 161000))
```

## Get Sample data

You can use samples/get_samples.sh or by hand with

```
curl -O 'https://planetarydata.jpl.nasa.gov/img/data/msl/MSLMST_0031/DATA/RDR/SURFACE/3531/3531ML1023500011404703C00_DRXX.LBL  
curl -O 'https://planetarydata.jpl.nasa.gov/img/data/msl/MSLMST_0031/DATA/RDR/SURFACE/3531/3531ML1023500011404703C00_DRXX.IMG
```


[1]: https://pds.nasa.gov/datastandards/pds3/standards/sr/StdRef_20090227_v3.8.pdf  
[2]: https://ode.rsl.wustl.edu/mars/pagehelp/Content/Introduction/Data_Standards.ht]  
