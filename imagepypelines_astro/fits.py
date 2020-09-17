import imagepypelines as ip
from .AstroBlock import AstroBlock
# astropy
from astropy.io import fits

DEFAULT_MEMMAP = True

# setup base class for all HDU loading
################################################################################
class HduLoader(AstroBlock):
    """Loads the header and data from the specified HDU. Use of memory mapping (memmap)
    is optional

    Attributes:
        hdu_index (str,int): the integer index or str extension name for the hdu
            that will be loaded from the fits file. Usually this is simply
            "primary", or 0
        use_memmap (bool): whether or not this block is using memory mapping.

    Default Enforcement:
        1) fname
            type: str
            shapes: None

    Batch Size:
        "each"
    """
    # __________________________________________________________________________
    def __init__(self, hdu_index, use_memmap=DEFAULT_MEMMAP):
        """instantiates the HduLoader for the given hdu_index

        Args:
            hdu_index: The integer index or str extension name for the hdu
                that you want to load from the fits file. Usually this is simply
                "primary" or 0
            use_memmap(bool): Whether or not to use memory mapping (memmap).
                Leaving as True will reduce memory footprint, but this will
                sometimes sacrifice speed and can lock access to the file.
                False is reccomended if you have adequate memory available.
        """
        self.hdu_index = hdu_index
        self.use_memmap = use_memmap

    # __________________________________________________________________________
    def process(self, fname):
        """loads the desired header and data from the fits file
        """
        hdul = fits.open(fname, memmap=self.use_memmap)
        hdu = hdul[self.hdu_index]
        return hdu.header,


################################################################################
class LoadPrimaryHDU(HduLoader):
    """loads the primary HDU of a fits file and loads the header and data into memory

    Default Enforcement:
        1) fname
            type: str
            shapes: None

    Batch Size:
        "each"
    """
    # __________________________________________________________________________
    def __init__(self, use_memmap=DEFAULT_MEMMAP):
        """instantiates the PrimaryFitsLoader

        Args:
            use_memmap(bool): Whether or not to use memory mapping (memmap).
                Leaving as True will reduce memory footprint, but this will
                sometimes sacrifice speed and can lock access to the file.
                False is reccomended if you have adequate memory available.
        """
        super().__init__("PRIMARY", use_memmap)


################################################################################
class LoadHDU0(HduLoader):
        # __________________________________________________________________________
        def __init__(self, use_memmap=DEFAULT_MEMMAP):
            """instantiates the LoadHDU0

            Args:
                use_memmap(bool): Whether or not to use memory mapping (memmap).
                    Leaving as True will reduce memory footprint, but this will
                    sometimes sacrifice speed and can lock access to the file.
                    False is reccomended if you have adequate memory available.
            """
            super().__init__(0, use_memmap)


################################################################################
class LoadHDU1(HduLoader):
        # __________________________________________________________________________
        def __init__(self, use_memmap=DEFAULT_MEMMAP):
            """instantiates the LoadHDU1

            Args:
                use_memmap(bool): Whether or not to use memory mapping (memmap).
                    Leaving as True will reduce memory footprint, but this will
                    sometimes sacrifice speed and can lock access to the file.
                    False is reccomended if you have adequate memory available.
            """
            super().__init__(1, use_memmap)


################################################################################
class LoadHDU2(HduLoader):
        # __________________________________________________________________________
        def __init__(self, use_memmap=DEFAULT_MEMMAP):
            """instantiates the LoadHDU2

            Args:
                use_memmap(bool): Whether or not to use memory mapping (memmap).
                    Leaving as True will reduce memory footprint, but this will
                    sometimes sacrifice speed and can lock access to the file.
                    False is reccomended if you have adequate memory available.
            """
            super().__init__(2, use_memmap)
