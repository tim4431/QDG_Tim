import numpy as np


class FOM_analysis:
    def __init__(self):
        pass

    def _find(self, l, val):
        """return the index of most close value in l
        uni-directional, l must be sorted"""
        idx = np.abs(np.asarray(l) - val).argmin()
        return idx

    def gaussian_curve(self, l, lambda_0, FWHM):
        """theoretical gaussian curve"""
        sigma = FWHM / 1.6651092223153954
        return np.exp(-((l - lambda_0) ** 2) / (sigma**2))

    def T_0(self, l, lambda_0, T):
        index_center = self._find(l, lambda_0)
        T_0 = T[index_center]
        return T_0

    def T_max(self, l, T):
        return np.max(T), l[np.argmax(T)]

    def data_crop(self, l, T, lambda_0, width):
        """get data from lambda_0-width/2 to lambda_0+width/2"""
        assert width > 0, "width must be positive"
        index_leftmost = self._find(l, lambda_0 - width / 2)
        index_rightmost = self._find(l, lambda_0 + width / 2)
        l_crop = l[index_leftmost : index_rightmost + 1]
        T_crop = T[index_leftmost : index_rightmost + 1]
        return l_crop, T_crop

    def cross_correlation(self, f, g):
        assert len(f) == len(g), "f and g must have the same length"
        return np.sum(np.asarray(f) * np.asarray(g))

    def _sum_alpha(self, f, alpha=1):
        return np.sum(np.power(f, alpha))

    def mean_alpha(self, f, alpha=1):
        return np.power(np.mean(np.power(f, alpha)), 1 / alpha)

    def norm_cross_correlation(self, f, g):
        cc = self.cross_correlation(f, g)
        norm_f = np.sqrt(self._sum_alpha(f, 2))
        norm_g = np.sqrt(self._sum_alpha(g, 2))
        return cc / (norm_f * norm_g)

    def mean_CE(self, f):
        return np.mean(10 * np.log10(np.asarray(f)))

    def cw_penalty(self, penalty, lambda_0, lambda_maxT):
        """penalty for center wavelength shifting"""
        _sum = 0
        for p_coeff, lambda_range in penalty:
            _sum += (
                p_coeff * lambda_range / (lambda_range + np.abs(lambda_0 - lambda_maxT))
            )
        return _sum
