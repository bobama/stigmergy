
from distutils.core import setup, Extension

module1 = Extension('hec',
                    libraries = ['gmp'],
                    sources = ['hec.c'])

setup (name = 'hec',
       version = '1.0',
       description = 'Homomorphic encryption of counters',
       ext_modules = [module1])
