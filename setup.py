from distutils.core import setup
import py2exe
import numpy
import os
import sys


# add any numpy directory containing a dll file to sys.path
def numpy_dll_paths_fix():
    paths = set()
    np_path = numpy.__path__[0]
    for dirpath, _, filenames in os.walk(np_path):
        for item in filenames:
            if item.endswith('.dll'):
                paths.add(dirpath)

    sys.path.append(*list(paths))

numpy_dll_paths_fix()

setup(
    name='PDFSummarizer',
    version='1.0',
    console=['PDFsummarizer.py'],
    url='',
    license='',
    author='Varin_S',
    author_email='',
    description='',
    options={
            "py2exe": {
                    "excludes": ["Tkconstants", "Tkinter", "tcl"]
                }
        },
    data_files=[('stopwords', ['data/stopwords/english.txt', 'data/stopwords/french.txt']),
                ('config', ['pdfparser/config/pdfsummarizer.conf'])]
    )
