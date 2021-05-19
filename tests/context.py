import os
import sys

# We need to insert at the beginning to override the system path
# lookup. This will enable the tests to import the local packages.
sys.path.insert(
    0, 
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from some_module2 import not_quite_some_fun, is_valid as better_is_valid
from nethelper import calc_subnet_mask
