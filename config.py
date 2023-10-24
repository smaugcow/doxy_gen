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

PRETTY_DOXYGEN_OUTPUT_DIR = MAIN_DIR + "/output/output_pretty_doxygen"

FILES_TO_KEEP = {"device" : ["classDevice.tex", 
                             "classDlmsDevice.tex"],
                 "connection" : ["classConnection.tex",
                                 "classMediumConnection.tex",
                                 "classRealConnection.tex",
                                 "classLoRaWanConnection.tex",
                                 "classTcpServerWaviotConnection.tex",
                                 "classModemResetter.tex"],
                 "readCondition" : ["classReadCondition.tex", 
                                    "classTerminatorReadCondition.tex"]
                }

FILE_IMAGES = OrderedDict()
FILE_IMAGES['connection.png'] = 'class_connection__inherit__graph.png'
FILE_IMAGES['devices.png'] = 'class_device__inherit__graph.png'
FILE_IMAGES['exception.png'] = 'class_ascue_exception__inherit__graph.png'
FILE_IMAGES['lorawan.png'] = 'class_lo_ra_wan_1_1_lo_ra_wan_device__inherit__graph.png'
FILE_IMAGES['protocol.png'] = 'class_protocol_1_1_protocol__inherit__graph.png'
FILE_IMAGES['readCondition.png'] = 'class_read_condition__inherit__graph.png'

LATEX_SOURCES_RES_IMAGES_DIR = MAIN_DIR + "/latex/latex_sources/res/images"
