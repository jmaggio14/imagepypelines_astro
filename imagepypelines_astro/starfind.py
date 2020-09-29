from photoutils import DAOStarFinder, IRAFStarFinder


from .AstroBlock import AstroBlock


class BaseStarFinder(AstroBlock):
    def __init__(self, fwhm, threshold)
