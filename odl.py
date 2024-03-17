# Simple IMG label parser for ODL format
#   parser is intolerant to label syntax errors
#   lines may be any iterable ( file stream, list of lines )


import sys
from datetime import datetime 

def warn(s): print( s, file=sys.stderr )


# ISO 8601 calendar format, 2021-02-22T20:41:55.833
def ISOC( time_str:str ):
  time_str = time_str.replace('"','')
  if '.' in time_str:
    return datetime.strptime( time_str, '%Y-%m-%dT%H:%M:%S.%f' )
  else:
    return datetime.strptime( time_str, '%Y-%m-%dT%H:%M:%S' )

# ISO 8601 Day of year format,  Sol-03039M14:00:29.161
# return sol, time
def ISOD( time_str:str ):
  time_str = time_str.replace('"','')
  if time_str.startswith('Sol-'): time_str = time_str[4:]
  sol = int(time_str[:5])
  return sol, datetime.strptime( time_str[6:], '%H:%M:%S.%f' ).time()


class ODL(object):
  
  def __init__( self, strip_quotes=False, strict_header=False ):
    self.strip_quotes = strip_quotes
    self.strict_header = strict_header
    self.label = None

  def parse(self, lines):
    label = {}
    prefix = []

    # parser catches broken out for clarity
    is_comment     = lambda s: s.startswith('/*')
    is_array_start = lambda w: len(w)==2 and ( w[1].endswith(',') or w[1].startswith('(') )
    is_array_end   = lambda s: s.endswith(')') or (s.endswith(',') and not s.startswith('(') ) 
    is_quote_start = lambda w: len(w) == 2 and w[1].startswith('"')
    is_quote_end   = lambda s: s.endswith('"') 
    is_kv_start    = lambda w: len(w) == 2 and len(w[1]) == 0

    def read_line(f):
      for line in f:
        if is_comment(line): continue # skip comments
        words = line.strip().split('=')
        words = [v.strip() for v in words]
        if is_quote_start(words):     # handle line continuations for quotes
          k,v = words
          while not is_quote_end(v):
            v += ' ' + next(f).strip()
          yield [k,v]
        elif is_array_start(words):   # handle line continuations for arrays
          k,v = words
          while not is_array_end(v):
            v += next(f).strip()
          yield [k,v]
        elif is_kv_start(words):      # key is present, value is on next line
          k,v = words[0], next(f).strip()
          yield [k,v]
        else:                         # simple key/value pair
          yield words

    if self.strict_header:
      first_line = nex( read_line(lines), None )
      if first_line is None or first_line not in ( ['PDS_VERSION_ID','PDS3'], ['ODL_VERSION_ID','ODL3'] ): return None

    for words in read_line(lines):
      if len(words) < 1: continue                    # blank line
      if words[0] == 'END': break                    # EOF
      if len(words) == 1:
        if words[0].startswith('/*'): pass           # skip comments
        elif len(words[0]) == 0: pass               
        else:
          warn( 'Unparsed line: %s' % words )
      elif len(words) == 2:
        k, v = words
        if self.strip_quotes: v = v.replace('"','')
        if k in ( 'GROUP', 'OBJECT' ):               # new grouping
          prefix += [v]
        elif k in ( 'END_GROUP', 'END_OBJECT' ):     # end of grouping
          prefix = prefix[:-1]
        else:
          label['/'.join(prefix+[k])] = v            # value complete
      else:
        warn( 'Unparsed line: %s' % words )

    self.label = label
    return label


  def get( self, item:str, cast=None ):

    if self.label is None: raise IndexError( 'Label content is empty' )
    v = self.label.get(item)
    return cast(v) if cast else v


  def get_array( self, item:str, cast=None ):

    v = self.get(item)
    if v is None: return None  
    items = v[1:-1].split(',')           # strip outer parenthesis
    if cast is None: return items
    return [ cast(v) for v in items ]




