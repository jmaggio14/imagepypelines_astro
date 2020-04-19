import imagepypelines as ip
# astropy
from astropy.io import fits

# Define the base class for all Astronomy
################################################################################
class AstroBlock(ip.Block):
    """Special Block made for astronomy with a predefined IO inputs and useful
    properties

    """
    def __init__(self):
        """instantiates the ImageBlock"""
        # NOTE: add default input types
        super().__init__(batch_type="each")
        self.tags.add("astronomy")

################################################################################
class FitsLoader(AstroBlock):
    def process(self, fname):
        fits.open(fname)
