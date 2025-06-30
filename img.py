import os
import odl
import numpy as np



def odl_type_to_numpy_dtype( sample_type, sample_bits ):

  # Define a dictionary to map PDS3 sample types to numpy dtypes
  sample_type_map = {
      'UNSIGNED_INTEGER':     '>u',
      'MSB_UNSIGNED_INTEGER': '>u',
      'LSB_UNSIGNED_INTEGER': '<u',
      'MSB_SIGNED_INTEGER':   '>i',
      'LSB_SIGNED_INTEGER':   '<i',
      'IEEE_REAL':            '>f',
      'IEEE_DOUBLE':          '>f',
  }

  dtype_prefix = sample_type_map.get( sample_type )
  if dtype_prefix is None:
    raise ValueError(f"Unknown PDS sample type: {sample_type}")
  return f'{dtype_prefix}{sample_bits//8}'



def read_img( img_path:str ):

  label_parser = odl.ODL()
  with open( img_path, 'r' ) as infile: label_parser.parse( infile )

  record_size   = label_parser.get( 'RECORD_BYTES', int )
  image_ptr     = label_parser.get( '^IMAGE', int )
  num_bands     = label_parser.get( 'IMAGE/BANDS', int )
  sample_type   = label_parser.get( 'IMAGE/SAMPLE_TYPE' )
  sample_bits   = label_parser.get( 'IMAGE/SAMPLE_BITS', int )
  lines         = label_parser.get( 'IMAGE/LINES', int )
  samples       = label_parser.get( 'IMAGE/LINE_SAMPLES', int )
  band_storage  = label_parser.get( 'IMAGE/BAND_STORAGE_TYPE' )

  dtype = odl_type_to_numpy_dtype(sample_type,sample_bits) 
  data = np.fromfile( img_path, dtype, count=lines*samples*num_bands, offset=(image_ptr-1)*record_size )
  return data.reshape( (num_bands, lines, samples) )


def read_lbl_img( lbl_path:str, img_path:str = None ):

  label_parser = odl.ODL()
  with open( lbl_path, 'r' ) as infile: label_parser.parse( infile )

  record_size   = label_parser.get( 'RECORD_BYTES', int )
  image_ptr     = label_parser.get( '^IMAGE', str )
  num_bands     = label_parser.get( 'IMAGE/BANDS', int )
  sample_type   = label_parser.get( 'IMAGE/SAMPLE_TYPE' )
  sample_bits   = label_parser.get( 'IMAGE/SAMPLE_BITS', int )
  lines         = label_parser.get( 'IMAGE/LINES', int )
  samples       = label_parser.get( 'IMAGE/LINE_SAMPLES', int )
  band_storage  = label_parser.get( 'IMAGE/BAND_STORAGE_TYPE' )


  img_path = img_path or lbl_path[:-4]+'.IMG'
  dtype = odl_type_to_numpy_dtype(sample_type,sample_bits) 
  data = np.fromfile( img_path, dtype=dtype, count=lines*samples*num_bands, offset=0 )
  return data.reshape( (num_bands, lines, samples) )
