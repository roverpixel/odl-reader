# Simple IMG label parser for ODL format
#   parser is intolerant to label syntax errors
#   lines may be any iterable ( file stream, list of lines )


import sys
from datetime import datetime 

def warn(s): print( s, file=sys.stderr )


# ISO 8601 calendar format, 2021-02-22T20:41:55.833
def ISOC( time_str:str ):
  time_str = time_str.replace('"','')
  if time_str.endswith('Z'):
    time_str = time_str[:-1] # Remove trailing 'Z'

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
        # Removed the try-except UnicodeDecodeError from here.
        # Let the error propagate to be caught by the caller's loop if f is a text-opened binary.
        for line in f:
            if is_comment(line): continue # skip comments
            words = line.strip().split('=')
            words = [v.strip() for v in words]
            if is_quote_start(words):     # handle line continuations for quotes
                k,v = words
                while not is_quote_end(v):
                    try:
                        v += ' ' + next(f).strip()
                    except StopIteration: # End of file during continuation
                        break
                    # If UnicodeDecodeError happens on next(f), it will propagate out of read_line
                yield [k,v]
            elif is_array_start(words):   # handle line continuations for arrays
                k,v = words
                while not is_array_end(v):
                    try:
                        v += next(f).strip()
                    except StopIteration:
                        break
                    # If UnicodeDecodeError happens on next(f), it will propagate
                yield [k,v]
            elif is_kv_start(words):      # key is present, value is on next line
                try:
                    k,v = words[0], next(f).strip()
                    yield [k,v]
                except StopIteration:
                    warn(f"EOF or missing value line after key: {words[0]}")
                    return # Stop generation for this key
                # If UnicodeDecodeError happens on next(f), it will propagate
            else:                         # simple key/value pair
                yield words

    if self.strict_header:
      first_line = next( read_line(lines), None )
      if first_line is None or first_line not in ( ['PDS_VERSION_ID','PDS3'], ['ODL_VERSION_ID','ODL3'] ): return None

    try:
      for words in read_line(lines):
        if len(words) < 1: continue                    # blank line
        if words[0] == 'END':
          # If not in any group or object, this is the final END
          if not prefix:
            break                    # EOF for the label
          # Else, it's an END within a group/object, handled by END_GROUP/END_OBJECT

        if len(words) == 1:
          if words[0].startswith('/*'): pass           # skip comments
          elif len(words[0]) == 0: pass
          else:
            # Could be an END statement that wasn't caught if prefix logic is complex
            # For now, assume other single-word lines are issues or need specific handling
            if words[0] != 'END': # Avoid warning for END if it was part of a group
                warn( 'Unparsed line: %s' % words )
        elif len(words) == 2:
          k, v = words
          if self.strip_quotes: v = v.replace('"','')
          if k in ( 'GROUP', 'OBJECT' ):               # new grouping
            prefix += [v]
          elif k in ( 'END_GROUP', 'END_OBJECT' ):     # end of grouping
            if prefix and prefix[-1] == v: # Ensure it matches the current group/object
                prefix = prefix[:-1]
            else:
                warn(f"Mismatched END_GROUP/END_OBJECT: Expected {prefix[-1] if prefix else 'None'}, got {v}")
          else:
            label['/'.join(prefix+[k])] = v            # value complete
        else:
          warn( 'Unparsed line: %s' % words )
    except UnicodeDecodeError:
        warn("UnicodeDecodeError encountered while parsing. Assuming end of text label in binary file.")
    except Exception as e:
        warn(f"An unexpected error occurred during parsing: {e}")


    self.label = label
    return label


  def get( self, item:str, cast=None ):

    if self.label is None: raise IndexError( 'Label content is empty' )
    v = self.label.get(item)
    return cast(v) if cast else v


  def get_array( self, item:str, cast=None ):
    v = self.get(item)
    if not isinstance(v, str) or not (v.startswith('(') and v.endswith(')')):
      # Not a string or doesn't look like an ODL sequence (e.g. "(A,B,C)")
      # This addresses test_get_array_on_scalar_value
      # Depending on desired strictness, could raise ValueError or return None/empty list
      # For now, let's return None if it's not a sequence string.
      return None

    if v == '()': # Handle empty sequence
        return []

    # Strip outer parenthesis and then split by comma
    items_str = v[1:-1].split(',')

    processed_items = []
    for item_s in items_str:
        processed_s = item_s.strip() # Strip whitespace
        # If casting to string or no cast, remove enclosing quotes if present
        if cast is None or cast is str:
            if processed_s.startswith('"') and processed_s.endswith('"'):
                processed_s = processed_s[1:-1]
            elif processed_s.startswith("'") and processed_s.endswith("'"): # Support single quotes too
                processed_s = processed_s[1:-1]

        if cast:
            processed_items.append(cast(processed_s))
        else:
            processed_items.append(processed_s) # No cast, keep as (processed) string

    return processed_items




