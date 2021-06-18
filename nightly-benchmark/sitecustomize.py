import atexit
import cProfile
import gc
import os
import sys
import uuid


gc.disable()
gc.set_threshold(0)


if not os.path.basename(sys.argv[0]).startswith("gprof2dot"):
    p = cProfile.Profile()
    p.enable()
    atexit.register(p.dump_stats, f"prof_{os.getpid()}.pstat")
