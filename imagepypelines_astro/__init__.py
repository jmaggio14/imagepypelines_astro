# If you need the filenames of data from your data directory, modify the code
# below for your specific filename(s)
import pkg_resources
MOON_FILENAME = pkg_resources.resource_filename(__name__,
                                                        'data/moon.fits')
"""full filename for a fits image of the moon"""
del pkg_resources


# replace these lines with your own imports
from .dataload import moon

from .fits import *

from .stars import *

# import the global variables (unused as of 04/06/20)
from .globals import *
