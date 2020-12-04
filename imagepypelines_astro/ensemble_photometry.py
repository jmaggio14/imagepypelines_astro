from .AstroBlock import AstroBlock, AstroBlockAll
from .imports import import_opencv

import numpy as np
import scipy
import imagepypelines as ip

__all__ = [
            'w'
            'w4'
]
# TEMPORARY
class EnsembleSolve(AstroBlockAll):
    def __init__(self, force_star_mag=True, zero_tolerance=1e-3)
        # TODO: document
        self.force_star_mag = force_star_mag
        super().__init()

    def process(self, all_mags, all_mag_errs):
        """calculate correction magnitudes"""
        n_exposures = len(all_mags)
        all_mags = np.asarray(all_mags)
        all_mag_errs = np.asarray(all_mag_errs)

        # NOTE: variables in this function correspond to the variables
        # used by Ken Honeycutt in his paper "CCD Ensemble Photometry
        # on an Inhomogenus Set of Exposures"
        # (except that I use zero-based indexing)
        ee = all_mags.shape[0]
        ss = all_mags.shape[1]
        m = all_mags

         # ------------------ FILL MATRIX ------------------

        matrix = np.zeros( (ss+ee,ss+ee) )

        w = w1(m, all_mag_errs) * w2(m, all_mag_errs) \
                    * w3(m, all_mag_errs) * w4(m, all_mag_errs)

        # sum image weights for every star
        image_weights = np.sum(w,axis=1)
        # sum star weights for every image
        star_weights = np.sum(w,axis=0)
        # fetch the indices for matrix diagonal. Both for image and star weights
        diag_indices = np.diag_indices(ss+ee)
        diag_image_weight_indices = diag_indices[:ee,:ee]
        diag_star_weight_indices = diag_indices[ee:,ee:]

        # populate matrix diagonals with weight sums
        matrix[diag_image_weight_indices] = image_weights
        matrix[diag_star_weight_indices] = star_weights

        # populate bottom left of matrix with weights, this should be an area of [n_stars,n_images]
        matrix[ee:,:ee] = w.T
        # populate top right of matrix with weights, this should be an area of [n_images,n_stars]
        matrix[:ee,ee:] = w

        # # force the first star to have an instrumental mag of zero
        # if self.force_star_mag:
        #     matrix[ee,:ee]


        # DEBUG
        # make sure this this matrix is orthagonal as a check
        if not np.all(matrix == matrix.T):
            msg = "error in matrix calculation - resultant is non orthagonal"
            self.logger.error(msg)
            raise ValueError(msg)



         # ------------------ FILL bVec ------------------
         bvec = np.zeros( (ss+ee,1) )

         # calculate the magnitude sum along image and star dimensions
         image_m_sum = np.sum(m,axis=0)
         star_m_sum = np.sum(m,axis=1)

         # TODO: this could be sped up if sums are performed first
         # populate the first ee rows with image_weight * stellar_mag for that image
         weighted_mags = m * w

         bvec[:ee] = np.sum(weighted_mags, axis=1)
         bvec[ee:] = np.sum(weighted_mags, axis=0)


         # ------------------ Solve solution using SVD ------------------
         U,S,Vh = np.linalg.svd(matrix)

         # floor values that should be zero, but aren't due to 













        # renaming variable to conform with paper
        m = all_mags
        # average stellar magnitude over all exposures
        m0 = np.mean(m,axis=0)
        # calculate weights according to paper
        # 2020/4/12 - only w4 is calculated

        beta = 0
        for e in ee:
            for s in ss:
                (m[e,s] - em - m0[s])**2 * w[e,s]


        # calculate the magnitude weights according to Ken Honeycutt's
        # paper.
        # for now, only w4 is calculated


        # average magnitude of all stars
        m0 = np.mean(all_mags, axis=0)

        for e in all_mags.shape[0]:
            for s in all




        # for e in range(n_exposures):





    def w1(self, mags, mag_errs):
        """TEMPORARY"""
        return np.ones(mags.shape)

    def w2(self, mags, mag_errs):
        """TEMPORARY"""
        return np.ones(mags.shape)

    def w3(self, mags, mag_errs):
        """TEMPORARY"""
        return np.ones(mags.shape)

    def w4(self, mags, mag_errs):
        return 1 / mag_errs
