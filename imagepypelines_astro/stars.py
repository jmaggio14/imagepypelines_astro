from .AstroBlock import AstroBlock
from .imports import import_opencv

cv2 = import_opencv()
import random
import numpy as np
import matplotlib.pyplot as plt
from imagepypelines import Block

from astropy.stats import sigma_clipped_stats, SigmaClip
from astropy.modeling.fitting import LevMarLSQFitter
from astropy.table import Table

from photutils import DAOStarFinder as photutilsDAOStarFinder
from photutils import IRAFStarFinder as photutilsIRAFStarFinder
from photutils.psf import IntegratedGaussianPRF, DAOPhotPSFPhotometry
from photutils.psf import IterativelySubtractedPSFPhotometry, DAOGroup
from photutils.background import MMMBackground
from photutils.aperture import CircularAperture, CircularAnnulus, aperture_photometry

__all__ = [
            'DAOStarFinder',
            'IRAFStarFinder',
            'NSample',
            'FractionSample',
            'DrawSourceOutlines',
            # 'DAOPhotometry',
            'AperturesAndAnnuli',
            'AperturePhotometry',
            'InstrumentalMag',
            'InstrumentalMagWithExposure',
            'Stack',
            ]


class Stack(Block):
    def __init__(self, mode='median'):
        super().__init__(batch_type='all')
        assert mode in ('median', 'mean')
        self.mode = mode

    def process(self, images):
        n_images = len(images)
        all_images = np.stack(images, axis=0)

        if self.mode == 'median':
            stacked = np.median(all_images, axis=0)
        else:
            stacked = np.mean(all_images, axis=0)

        return [stacked]



################################################################################
class StarFinder(AstroBlock):

    def __init__(self, finder_obj, mask, **finder_kwargs):
        self.finder = finder_obj(**finder_kwargs)
        self.mask = mask
        super().__init__()
        self.enforce('image', np.ndarray, [(None,None)])

    def __make_border_mask(self, image, width):
        """by default create
        """
        upper = width
        lower = image.shape[0] - width
        left = width
        right = image.shape[1] - width
        mask = np.ones(image.shape, dtype=bool)
        mask[upper:lower,left:right] = 0
        return mask

    def process(self, image):
        if isinstance(self.mask,int):
            mask = self.__make_border_mask(image, self.mask)
        elif isinstance(self.mask, np.ndarray):
            mask = self.mask
        else:
            mask = None

        sources = self.finder(image, mask=mask)
        return sources
################################################################################
class DAOStarFinder(StarFinder):
    """

    """
    def __init__(self, mask=None, **daofind_kwargs):
        """

        Args:
            **daofind_kwargs : keyword arguments for the DAOStarFinder_
                object by astropy. Some examples include 'threshold' and 'fwhm'

        .. _DAOStarFinder: https://photutils.readthedocs.io/en/stable/api/photutils.detection.DAOStarFinder.html#photutils.detection.DAOStarFinder
        """
        super().__init__(photutilsDAOStarFinder, mask=mask, **daofind_kwargs)
################################################################################
class IRAFStarFinder(StarFinder):
    """

    """
    def __init__(self, mask=None, **iraffind_kwargs):
        """

        Args:
            **iraffind_kwargs : keyword arguments for the DAOStarFinder_
                object by astropy. Some examples include 'threshold' and 'fwhm'

        .. _IRAFStarFinder:https://photutils.readthedocs.io/en/stable/api/photutils.detection.IRAFStarFinder.html#photutils.detection.IRAFStarFinder
        """
        super().__init__(photutilsIRAFStarFinder, mask=mask, **iraffind_kwargs)
################################################################################
class AperturesAndAnnuli(AstroBlock):
    def __init__(self, radius, annulus_inner, annulus_outer):
        self.radius = radius
        self.annulus_inner = annulus_inner
        self.annulus_outer = annulus_outer
        super().__init__()

    def process(self, sources):
        positions = np.transpose( (sources['xcentroid'], sources['ycentroid']) )

        apertures = CircularAperture(positions, self.radius)
        annuli = CircularAnnulus(positions, self.annulus_inner, self.annulus_outer)

        return apertures, annuli

################################################################################
class AperturePhotometry(AstroBlock):
    def __init__(self, median_sigma_clip=3.0):
        self.median_sigma_clip = median_sigma_clip
        super().__init__()

    def process(self, image, apertures, annuli):
        # get the sums within the circular apertures for each source
        integrated = aperture_photometry(image, apertures)['aperture_sum']

        # fetch the annulus sigma-clipped median for local background subtraction
        annuli_masks  = annuli.to_mask(method='center')
        # fetch the background arrays
        background_data = [m.multiply(image)[m.data > 0] for m in annuli_masks]

        # calculate the median of the backgrounds for flux subtraction
        background_medians = [sigma_clipped_stats(bd,sigma=self.median_sigma_clip)[1] for bd in background_data]

        # sum up background subtracted flux in counts
        counts = np.asarray(integrated) - np.asarray(background_medians)

        # WARNING: this needs to be vetted
        # calculate error as quadature sum of read noise, shot noise, and background noise
        # calculate shot noise as the sqrt of the counts
        shot_noise = np.sqrt(counts)
        # calculate sky noise as the variance of the background
        background_noise = np.asarray([np.var(b) for b in background_data])
        # WARNING: this assumes background noise accounts for sky, read, and dark noise
        err = shot_noise + background_noise

        return counts, err

################################################################################
class InstrumentalMag(AstroBlock):
    def __init__(self, offset=0.0):
        self.offset = offset
        super().__init__()
        self.enforce('fluxes', np.ndarray)

    def process(self, fluxes):
        mag = self.offset - (2.5 * np.log10( fluxes ))
        return mag

################################################################################
class InstrumentalMagWithExposure(AstroBlock):
    def __init__(self, offset=0.0):
        self.offset = offset
        super().__init__()
        self.enforce('fluxes', np.ndarray)
        self.enforce('exp_time', float)


    def process(self, fluxes, exp_time):
        mag = self.offset - (2.5 * np.log10( fluxes / exp_time ))
        return mag





################################################################################


################################################################################
# class DAOPhotometry(AstroBlock):
#     def __init__(self, crit_separation, threshold, fwhm, psf_model, fitshape,
#                  sigma=3., ratio=1.0, theta=0.0, sigma_radius=1.5,
#                  sharplo=0.2, sharphi=1.0, roundlo=-1.0, roundhi=1.0,
#                  fitter=LevMarLSQFitter(),
#                  niters=3, aperture_radius=None,
#                  extra_output_cols=None, peakmax=None):
#
#         super().__init__()
#         self.crit_separation = crit_separation
#         self.threshold = threshold
#         self.fwhm = fwhm
#         self.sigma = sigma
#         self.ratio = ratio
#         self.theta = theta
#         self.sigma_radius = sigma_radius
#         self.sharplo = sharplo
#         self.sharphi = sharphi
#         self.roundlo = roundlo
#         self.roundhi = roundhi
#         self.peakmax = peakmax
#
#         self.logger.info("building photometer...")
#
#         group_maker = DAOGroup(crit_separation=self.crit_separation)
#         bkg_estimator = MMMBackground(sigma_clip=SigmaClip(sigma=self.sigma))
#         finder = DAOStarFinder(threshold=self.threshold,
#                                 fwhm=self.fwhm,
#                                 ratio=self.ratio,
#                                 theta=self.theta,
#                                 sigma_radius=self.sigma_radius,
#                                 sharplo=self.sharplo,
#                                 sharphi=self.sharphi,
#                                 roundlo=self.roundlo,
#                                 roundhi=self.roundhi,
#                                 peakmax=self.peakmax,
#                                 exclude_border=True,
#                                 )
#
#         self.photometer = IterativelySubtractedPSFPhotometry(group_maker=group_maker,
#                                                              bkg_estimator=bkg_estimator,
#                                                              psf_model=psf_model,
#                                                              fitshape=fitshape,
#                                                              finder=finder,
#                                                              fitter=fitter,
#                                                              niters=niters,
#                                                              aperture_radius=aperture_radius,
#                                                              extra_output_cols=extra_output_cols)
#
#         self.enforce('image', np.ndarray, [(None,None)])
    #
    # def process(self, image):
    #     phot = self.photometer.do_photometry(image)
    #     ids = phot['id']
    #     fluxes = phot['flux_fit']
    #     flux_unc = phot['flux_unc']
    #     # residual = self.photometer.get_residual_image()
    #     return phot
################################################################################
class DrawSourceOutlines(AstroBlock):
    __COLORS = {
                # red
                'r':(255,0,0),
                'red':(255,0,0),
                # green
                'g':(0,255,0),
                'green':(0,255,0),
                # blue
                'b':(0,0,255),
                'blue':(0,0,255),
                }
    def __init__(self, radius, color='red', thickness=2, x_key=None, y_key=None):
        self.radius = radius
        self.thickness = thickness

        # reverse color to make it compatible with opencv BGR format
        self.color = self.__COLORS.get(color,color)[::-1]

        self.x_key = x_key
        self.y_key = y_key

        super().__init__()
        self.enforce('image', np.ndarray, [(None,None,3)])
        self.enforce('sources', Table)

    def process(self, image, sources):
        # copy the image so we don't modify it in place
        image = image.copy()

        # check if 'xcentroid' exists, otherwise default to 'x_0'
        x_key = self.x_key
        if self.x_key is None:
             x_key = 'xcentroid' if ('xcentroid' in sources.colnames) else 'x_0'

        # check if 'ycentroid' exists, otherwise default to 'y_0'
        y_key = self.y_key
        if self.y_key is None:
             y_key = 'ycentroid' if ('ycentroid' in sources.colnames) else 'y_0'


        for x,y in zip(sources[x_key], sources[y_key]):
            # NOTE - this modifies the array in place!
            cv2.circle(image, (int(x),int(y)), self.radius, self.color, self.thickness)


        return image
################################################################################
class NSample(Block):
    def __init__(self, n_samples=1):
        super().__init__(batch_type='all')
        self.n_samples = n_samples

    def process(self, images):
        samples = random.sample(images, self.n_samples)
        return samples
################################################################################
class FractionSample(Block):
    def __init__(self, fraction=0.5):
        super().__init__(batch_type='all')
        self.fraction = fraction

    def process(self, images):
        n_samples = int(self.fraction * len(images))
        samples = random.sample(images, n_samples)
        return samples
