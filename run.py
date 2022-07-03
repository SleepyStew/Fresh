import sys, os

from fresh.run import run
try:
    # get sys args
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        debug = False
        if len(sys.argv) > 2:
            debug = sys.argv[2]
            if debug == "--debug":
                debug = True
        # check if file exists
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                text = f.read()
                result, error = run(filename, text, debug)
                if error:
                    print(error.as_string())
        else:
            sys.exit(0)
    else:
        import shell
except KeyboardInterrupt:
    sys.exit(0)