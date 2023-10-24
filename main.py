from input.doxy_gen import doxy_gen

import config

def main():

    dox = doxy_gen(config.INPUT_SOURCES_DIR,
                   config.LATEX_SOURCES_RES_IMAGES_DIR,
                   config.DOXYFILE_FILE,
                   config.DOXYFILE_IMAGES_FILE,
                   config.DOXYGEN_OUTPUT_DIR,
                   config.IMAGES_OUTPUT_DIR,
                   config.SKIP_DIR,
                   config.FILE_IMAGES)
    dox.run()

    print("\n")


if __name__ == "__main__":
    main()
