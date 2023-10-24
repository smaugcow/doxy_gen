import os
import sys

# Получить путь, откуда запускается main.py
MAIN_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

INPUT_SOURCES_DIR = MAIN_DIR + "/input/master"

DOXYFILE_FILE = MAIN_DIR + "/input/doxyfile"

DOXYFILE_IMAGES_FILE = MAIN_DIR + "/input/doxyfile_images"

DOXYGEN_OUTPUT_DIR = MAIN_DIR + "/output/output_doxygen"

SKIP_DIR = [".git", "test"]
