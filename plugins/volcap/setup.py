from distutils.core import setup, Extension

module1 = Extension('capacity',
                    sources=['volCap.c'], libraries=['gfapi'])

setup(name='capacity',
      version='1.0',
      description='Gets the volume capcity Utilization',
      py_modules=['__init__'],
      url='redhat.com',
      ext_modules=[module1])
