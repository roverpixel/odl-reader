#!/usr/bin/env python

import odl, img
import json


def self_test():

  label_parser = odl.ODL()

  with open('samples/3039ML0158730000507144C00_DRXX.IMG', 'r' ) as infile:
    label = label_parser.parse(infile)
  #print( json.dumps(label,indent=2) )

  sol = label_parser.get( 'PLANET_DAY_NUMBER', cast=int )
  print( f'SOL {sol}' )

  rad = label_parser.get_array( 'PROCESSING_PARMS/RADIANCE_SCALING_FACTOR', cast=float )
  print( f'Radiometric scaling factors: {rad}' )

  start_time = label_parser.get( 'START_TIME', cast=odl.ISOC )
  print( f'Start {start_time}' )

  sol, lmst = label_parser.get( 'MSL:LOCAL_MEAN_SOLAR_TIME', cast=odl.ISOD )
  print( f'Sol {sol}  LMST {lmst}' )

  image = img.read_img( 'samples/3039ML0158730000507144C00_DRXX.IMG' )
  print( f'Image nbands {image.shape[0]} lines {image.shape[1]} samples {image.shape[2]} dtype {image.dtype}' )

  image = img.read_lbl_img( lbl_path='samples/3531ML1023500011404703C00_DRXX.LBL' )
  #image = img.read_lbl_img( lbl_path='samples/3531ML1023500011404703C00_DRXX.LBL', img_path='samples/3531ML1023500011404703C00_DRXX.IMG' )
  print( f'Image nbands {image.shape[0]} lines {image.shape[1]} samples {image.shape[2]} dtype {image.dtype}' )

  from PIL import Image
  #Image.fromarray( (image/5).transpose( 1, 2, 0).astype('uint8') ).save( 'b.png' )

  


if __name__ == '__main__':
  self_test()


