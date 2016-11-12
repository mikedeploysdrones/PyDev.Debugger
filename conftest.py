import pytest
import sys


# see: http://goo.gl/kTQMs
SYMBOLS = {
    'customary'     : ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
    'customary_ext' : ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
                       'zetta', 'iotta'),
    'iec'           : ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
    'iec_ext'       : ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi',
                       'zebi', 'yobi'),
}

def bytes2human(n, format='%(value).1f %(symbol)s', symbols='customary'):
    """
    Bytes-to-human / human-to-bytes converter.
    Based on: http://goo.gl/kTQMs
    Working with Python 2.x and 3.x.
    
    Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
    License: MIT
    """
    
    """
    Convert n bytes into a human readable string based on format.
    symbols can be either "customary", "customary_ext", "iec" or "iec_ext",
    see: http://goo.gl/kTQMs

      >>> bytes2human(0)
      '0.0 B'
      >>> bytes2human(0.9)
      '0.0 B'
      >>> bytes2human(1)
      '1.0 B'
      >>> bytes2human(1.9)
      '1.0 B'
      >>> bytes2human(1024)
      '1.0 K'
      >>> bytes2human(1048576)
      '1.0 M'
      >>> bytes2human(1099511627776127398123789121)
      '909.5 Y'

      >>> bytes2human(9856, symbols="customary")
      '9.6 K'
      >>> bytes2human(9856, symbols="customary_ext")
      '9.6 kilo'
      >>> bytes2human(9856, symbols="iec")
      '9.6 Ki'
      >>> bytes2human(9856, symbols="iec_ext")
      '9.6 kibi'

      >>> bytes2human(10000, "%(value).1f %(symbol)s/sec")
      '9.8 K/sec'

      >>> # precision can be adjusted by playing with %f operator
      >>> bytes2human(10000, format="%(value).5f %(symbol)s")
      '9.76562 K'
    """
    n = int(n)
    if n < 0:
        raise ValueError("n < 0")
    symbols = SYMBOLS[symbols]
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)

def format_memory_info(memory_info):
    import psutil
    return 'Total: %s, Available: %s, Used: %s %%, Curr proc: %s' % (
        bytes2human(memory_info.total), bytes2human(memory_info.available), memory_info.percent, format_process_memory_info(psutil.Process().memory_info()))

def format_process_memory_info(proc_memory_info):
    return 'Used: %s' % (bytes2human(proc_memory_info.rss),)
    
@pytest.yield_fixture(autouse=True)
def before_after_each_function(request):
    import psutil
    current_pids = set(proc.pid for proc in psutil.process_iter())
    sys.stdout.write(
'''
===============================================================================
Memory before: %s
%s
===============================================================================
''' % (request.function, format_memory_info(psutil.virtual_memory())))
    yield
    
    processes_info = []
    for proc in psutil.process_iter():
        if proc.pid not in current_pids:
            processes_info.append(
                'New Process: %s(%s) - %s' % (proc.name(), proc.pid, format_process_memory_info(proc.memory_info())))
    
    sys.stdout.write(
'''
===============================================================================
Memory after: %s
%s%s
===============================================================================


''' % (request.function, format_memory_info(psutil.virtual_memory()), '' if not processes_info else '\nLeaked processes:\n'+'\n'.join(processes_info)))
