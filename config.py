import os
import sys
from collections import OrderedDict

# Получить путь, откуда запускается main.py
MAIN_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

INPUT_SOURCES_DIR = MAIN_DIR + "/input/master"

DOXYFILE_FILE = MAIN_DIR + "/input/doxyfile"

DOXYFILE_IMAGES_FILE = MAIN_DIR + "/input/doxyfile_images"

DOXYGEN_OUTPUT_DIR = MAIN_DIR + "/output/output_doxygen"

IMAGES_OUTPUT_DIR = MAIN_DIR + "/output/output_images"

SKIP_DIR = [".git", "test", ".svn"]

FILE_IMAGES = OrderedDict()
FILE_IMAGES['connect.png'] = 'class_connection__inherit__graph.png'
FILE_IMAGES['device.png'] = 'class_device__inherit__graph.png'
FILE_IMAGES['except.png'] = 'class_ascue_exception__inherit__graph.png'
FILE_IMAGES['proto.png'] = 'class_protocol_1_1_protocol__inherit__graph.png'

LATEX_SOURCES_RES_IMAGES_DIR = MAIN_DIR + "/latex/latex_sources/res/images"
