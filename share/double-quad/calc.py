#!/usr/bin/env python
from pbpl.common.units import *
import numpy as np

E0 = 3.5*MeV
gamma0 = (me*c_light**2 + E0)/(me*c_light**2)
p0 = gamma0 * me * c_light

quad_f = 250*mm
quad_length = 10*mm
quad_gradient = p0 / (quad_f * quad_length * eplus)
print('gradient = ', quad_gradient / (tesla/meter))

Ld = quad_f * (np.sqrt(5)-1) / 5
print('Ld = ', Ld/mm)

#quad_K = eplus * quad_gradient / p0  # K = kappa0^2
