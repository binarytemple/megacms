import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))

sys.path[0:0] = [os.path.join(HERE, x) for x in ['main', 'lib', 'devlib',]]