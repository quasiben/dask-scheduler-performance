import atexit
import cProfile
import os
import sys
import uuid

if not os.path.basename(sys.argv[0]).startswith("gprof2dot"):
    p = cProfile.Profile()
    p.enable()
    atexit.register(p.dump_stats, f"prof_{os.getpid()}.pstat")
