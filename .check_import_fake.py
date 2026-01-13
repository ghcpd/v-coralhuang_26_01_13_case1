import importlib, traceback
try:
    m = importlib.import_module('fake')
    print('loaded fake from', getattr(m, '__file__', '<unknown>'))
    print('first 200 bytes:')
    with open(m.__file__, 'rb') as f:
        print(f.read(200))
except Exception as e:
    print('ERROR', e)
    traceback.print_exc()