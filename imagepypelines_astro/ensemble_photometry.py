from .AstroBlock import AstroBlockAll

import numpy as np

__all__ = [
            'EnsemblePhotometry'
            ]
# TEMPORARY
class EnsemblePhotometry(AstroBlockAll):
    def __init__(self, force_star_mag=False, n_stars=50):
        # TODO: document
        self.force_star_mag = force_star_mag
        self.n_stars = n_stars

        super().__init__()

    def process(self, all_mags, all_mag_errs):
        """calculate correction magnitudes"""
        n_exposures = len(all_mags)
        all_mags = np.asarray(all_mags)
        all_mag_errs = np.asarray(all_mag_errs)


        # NOTE: variables in this function correspond to the variables
        # used by Ken Honeycutt in his paper "CCD Ensemble Photometry
        # on an Inhomogenus Set of Exposures"
        # (except that I use zero-based indexing)

        # sort the stars brightest to smallest, only choose the brightest n
        # stars for the solution
        n_stars = min(ss,self.n_stars)
        avg_mags = np.mean(all_mags,axis=0)
        brightest_star_indices = np.argsort(avg_mags)[-n_stars:]


        m = all_mags[:,brightest_star_indices]
        ee = m.shape[0] # number of exposures
        ss = m.shape[1] # number of stars



        # ------------------ FILL MATRIX ------------------

        matrix = np.zeros( (ss+ee,ss+ee) )


        w1 = np.ones(all_mags.shape,dtype=bool)
        w2 = np.zeros(all_mags.shape,dtype=bool)
        w2[:,brightest_star_indices] = 1
        w3 = np.ones(all_mags.shape,dtype=bool)
        w4 = self.w4(m, all_mag_errs)

        w = w1[brightest_star_indices] * w2[brightest_star_indices] \
            * w3[brightest_star_indices] * w4[brightest_star_indices]

        # sum image weights for every star
        image_weights = np.sum(w,axis=1)
        # sum star weights for every image
        star_weights = np.sum(w,axis=0)
        # fetch the indices for matrix diagonal. Both for image and star weights
        diag_indices = np.diag_indices(ss+ee)
        diag_image_weight_indices = (diag_indices[0][:ee],diag_indices[1][:ee])
        diag_star_weight_indices = (diag_indices[0][ee:],diag_indices[1][ee:])

        # populate matrix diagonals with weight sums
        matrix[diag_image_weight_indices] = image_weights
        matrix[diag_star_weight_indices] = star_weights

        # populate bottom left of matrix with weights, this should be an area of [n_stars,n_images]
        matrix[ee:,:ee] = w.T
        # populate top right of matrix with weights, this should be an area of [n_images,n_stars]
        matrix[:ee,ee:] = w

        # force the first star to have an instrumental mag of zero
        # this can help the solution
        if self.force_star_mag:
            matrix[:,ee] = 0.0
            matrix[ee,:] = 0.0


        # DEBUG
        # # make sure this this matrix is orthagonal as a check
        # if not np.all(matrix == matrix.T):
        #     msg = "error in matrix calculation - resultant is non orthagonal"
        #     self.logger.error(msg)
        #     raise ValueError(msg)


         # ------------------ FILL bVec ------------------
        bvec = np.zeros( (ss+ee,1) )

        # calculate the magnitude sum along image and star dimensions
        image_m_sum = np.sum(m,axis=0)
        star_m_sum = np.sum(m,axis=1)

        # TODO: this could be sped up if sums are performed first
        # populate the first ee rows with image_weight * stellar_mag for that image
        weighted_mags = m * w
        bvec[:ee,0] = np.sum(weighted_mags, axis=1)
        bvec[ee:,0] = np.sum(weighted_mags, axis=0)


        # ------------------ Solve solution using SVD ------------------
        # U,S,Vh = np.linalg.svd(matrix)
        #
        # # floor values that should be zero, but aren't due to floating point errors
        # S[ S < self.zero_tolerance] = 0

        # compute the least squares solution for the corrected magnitude vectors
        # in other words, solve for x in the matrix*x = bvec
        self.logger.info("beginning least squares ensemble correction...")
        x,residuals,rank,_ = np.linalg.lstsq(matrix,bvec,rcond=None)

        # x is a vector.
        # first ee rows are image correction factor em(0), em(1), ...
        # last ss rows are stellar mean magnitudes m0(0), m0(1), ...

        # First star's magnitude is unconstrained, so we have to set it to 0.0
        if self.force_star_mag:
            x[ee] = 0.0

        # image correction factors
        em = x[:ee]
        # mean magnitudes
        m0 = x[ee:]

        # ------------ Calculate corrected magnitude and error ------------

        # stellar magnitudes - corrected with correction factors
        # em is a vector here, and m is 2D. numpy just does broadcasting magic
        M = all_mags + em

        # calculate the stellar mean magnitude from as a weighted average using w4
        mean_mags = np.sum(M * w4, axis=0) /  np.sum(w4, axis=0)
        # however, for the brightest stars we just replace them from the solution
        mean_mags[brightest_star_indices] = m0


        # calculate error of magnitude correction factors
        # again, python broadcasting magic...
        weighted_sq_residual = (all_mags - em.reshape((ee,1)) - mean_mags.reshape((1,None)))**2 * w4


        # calculate error of image correction
        numerator = ss * np.sum(weighted_sq_residual, axis=1)
        denominator = (ss - 1) * image_weights

        sigma2_em = numerator / denominator

        # calculate error of stellar mean magnitude
        numerator = ee * np.sum(weighted_sq_residual, axis=0)
        denominator = (ee - 1) * np.sum(w4,axis=0)

        sigma2_m0 = numerator / denominator





        # rename these to be more explicit
        corrected_magnitudes = M # [n_images, n_stars]
        image_correction_factors = em # [n_images,]
        image_correction_error = sigma2_em # [n_images ]
        mean_stellar_magnitude = mean_mags # [n_stars,]
        mean_stellar_mag_error = sigma2_m0 # [n_stars,]

        return corrected_magnitudes, image_correction_factors, \
                image_correction_error, mean_stellar_magnitude, mean_stellar_mag_error


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
