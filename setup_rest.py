from distutils.core import setup
import py2exe
import numpy
import os
import sys


# add any numpy directory containing a dll file to sys.path
def numpy_dll_paths_fix():
    paths = set()
    np_path = numpy.__path__[0]
    for dir_path, _, file_names in os.walk(np_path):
        for item in file_names:
            if item.endswith('.dll'):
                paths.add(dir_path)

    sys.path.append(*list(paths))

numpy_dll_paths_fix()

setup(
    name='REST_PDF_Summarizer',
    version='1.0',
    console=['run_rest_api.py'],
    url='',
    license='',
    author='OECD',
    author_email='',
    description='REST service used to generate summaries from pdf files.',
    options={
            "py2exe": {
                    "excludes": ["Tkconstants", "Tkinter", "tcl", "jinja2.asyncsupport"],
                    "skip_archive": True
                }
        },
    data_files=[('stopwords', ['data/stopwords/english.txt', 'data/stopwords/french.txt']),
                ('config', ['pdfparser/config/pdfsummarizer.conf']),
                ('static', ['static/index.html'])]
    )
