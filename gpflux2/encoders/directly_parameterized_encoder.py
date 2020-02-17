# Copyright (C) PROWLER.io 2020 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import tensorflow as tf
import numpy as np

from gpflow.utilities.bijectors import positive
from gpflow import Parameter

from gpflux2.exceptions import EncoderInitializationError
from gpflux2.layers import TrackableLayer


class DirectlyParameterizedNormalDiag(TrackableLayer):
    """
    Directly parameterize the posterior (and prior) of the latent variables associated
    with each data point with a diagonal multivariate Normal distribution.

    No amortization is used; each datapoint element has an associated mean and variance,
    IMPORTANT: Not compatible with minibatches
    """

    def __init__(self, num_data: int, latent_dim: int, means=None):
        """
        :param num_data: The number of data points
        :param latent_dim: The dimensionality of the latent variable
        :param means: The means of the Normal distribution to initialise to.
            Shape [num_data, latent_dim].
        """
        super().__init__()
        if means is None:
            means = np.zeros((num_data, latent_dim))
        else:
            if np.any(tf.shape(means) != (num_data, latent_dim)):
                raise EncoderInitializationError
        # init a small std, has been observed to help fitting.
        std = 1e-5 * np.ones(shape=(num_data, latent_dim), dtype=np.float64)

        self.means = tf.Variable(means, name="w_means")
        self.std = Parameter(std, transform=positive(), name="w_std")

    def call(self, inputs=None, *args, **kwargs):
        if inputs is not None:
            tf.debugging.assert_shapes(
                [(self.means, ["N", "W"]), (inputs, ["N", "D"]),]
            )
        return self.means, self.std
