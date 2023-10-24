from input.doxy_gen import doxy_gen

import config

def main():

    dox = doxy_gen(config.INPUT_SOURCES_DIR,
                   config.DOXYFILE_FILE, 
                   config.DOXYGEN_OUTPUT_DIR, 
                   config.SKIP_DIR)
    dox.run()

    print("\n")


if __name__ == "__main__":
    main()
