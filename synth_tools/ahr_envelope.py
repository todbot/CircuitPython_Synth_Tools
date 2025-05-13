## pylint: disable=too-many-arguments, too-many-positional-arguments
# SPDX-FileCopyrightText: Copyright (c) 2023 Tod Kurt
# SPDX-License-Identifier: MIT
"""
`ahr_envelope`
================================================================================

`AHREnvelope` is a Attack-Hold-Release envelope usable for filter frequency
in synthio.

Part of synth_tools.

"""

import ulab.numpy as np
import synthio

LINEAR = 0
EXPONENTIAL = 1


class AHREnvelope:
    """Simple AHR envelope for use with filters"""

    def __init__(
        self, smax, smin, attack_time=0.1, release_time=0.1, curve_type=LINEAR
    ):
        self.smax = smax
        self.smin = smin
        self.attack_time = max(0.001, attack_time)
        self.release_time = max(0.001, release_time)
        self.lerp = synthio.LFO(
            once=True, waveform=np.array((0, 32767), dtype=np.int16)
        )
        if curve_type == LINEAR:
            lerp = self.lerp
        else:  #  EXPONENTIAL
            lerp = synthio.Math(synthio.MathOperation.PRODUCT, self.lerp, self.lerp, 1)
        self.env = synthio.Math(
            synthio.MathOperation.CONSTRAINED_LERP, smin, smax, lerp
        )

    def press(self):
        """Call this method right before synth.press()"""
        self.env.a = self.smin
        self.env.b = self.smax
        self.lerp.rate = 1 / self.attack_time
        self.lerp.retrigger()

    def release(self):
        """Call this method right before synth.release()"""
        self.env.a = self.env.value  # curr val is new start value
        self.env.b = self.smin
        self.lerp.rate = 1 / self.release_time
        self.lerp.retrigger()
