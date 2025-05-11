## pylint: disable=invalid-name,too-many-arguments,multiple-statements
# multiple-statements,too-many-instance-attributes
# SPDX-FileCopyrightText: Copyright (c) 2023 Tod Kurt
# SPDX-License-Identifier: MIT
"""
`waves`
================================================================================

`Waves` is a set of waveform construction tools for `synthio`.
`Wavetable` uses `Waves` to create a Wavetable waveform for `Instrument`
that can load arbitrary two waveforms and mix between them.

Part of synth_tools.

"""

import random
import ulab.numpy as np
import adafruit_wave


class Waves:
    """
    Generate waveforms for either oscillator or LFO use.
    By default, size is 256, volume is max +-32767
    """

    waveform_types = ("SIN", "SQU", "SAW", "TRI", "SIL", "NZE")

    @staticmethod
    def make_waveform(waveid, size=256, volume=32767):
        """Return a waveform by string name, one of `waveform_types`"""
        waveid = waveid.upper()
        wavef = None
        if waveid in ("SIN", "SINE"):
            wavef = Waves.sine(size, volume)
        elif waveid in ("SQU", "SQUARE"):
            wavef = Waves.square(size, volume)
        elif waveid in ("SAW"):
            wavef = Waves.saw(size, volume)
        elif waveid in ("TRI", "TRIANGLE"):
            wavef = Waves.triangle(size, -volume, volume)
        elif waveid in ("SIL", "SILENCE"):
            wavef = Waves.silence(size)
        elif waveid in ("NZE", "NOISE"):
            wavef = Waves.noise(size, volume)
        else:
            print("unknown wave type", waveid)
        return wavef

    @staticmethod
    def sine(size, volume):
        """Sine waveform"""
        return np.array(
            np.sin(np.linspace(0, 2 * np.pi, size, endpoint=False)) * volume,
            dtype=np.int16,
        )

    @staticmethod
    def square(size, volume):
        """Square waveform"""
        return np.concatenate(
            (
                np.ones(size // 2, dtype=np.int16) * volume,
                np.ones(size // 2, dtype=np.int16) * -volume,
            )
        )

    @staticmethod
    def triangle(size, min_vol, max_vol):
        """Triangle waveform"""
        return np.concatenate(
            (
                np.linspace(min_vol, max_vol, num=size // 2, dtype=np.int16),
                np.linspace(max_vol, min_vol, num=size // 2, dtype=np.int16),
            )
        )

    @staticmethod
    def saw(size, volume):
        """Saw (aka Ramp) waveform"""
        return Waves.saw_down(size, volume)

    @staticmethod
    def saw_down(size, volume):
        """Saw waveform from max to min"""
        return np.linspace(volume, -volume, num=size, dtype=np.int16)

    @staticmethod
    def saw_up(size, volume):
        """Saw waveform from min to max"""
        return np.linspace(-volume, volume, num=size, dtype=np.int16)

    @staticmethod
    def silence(size):
        """All zeros waveform"""
        return np.zeros(size, dtype=np.int16)

    @staticmethod
    def noise(size, volume):
        """White noise waveform (from random.randint)"""
        return np.array(
            [random.randint(-volume, volume) for i in range(size)], dtype=np.int16
        )

    @staticmethod
    def from_list(vals):
        """Waveform from a list of values, useful for LFOs"""
        # print("Waves.from_list: vals=",vals)
        return np.array([int(v) for v in vals], dtype=np.int16)

    @staticmethod
    def lfo_ramp_up_pos():
        """Simple two-element ramp-up waveform for synthio.LFO (which does interpolation)"""
        return np.array((0, 32767), dtype=np.int16)

    @staticmethod
    def lfo_ramp_down_pos():
        """Simple two-element row-downwaveform for synthio.LFO (which does interpolation)"""
        return np.array((32767, 0), dtype=np.int16)

    @staticmethod
    def lfo_triangle_pos():
        """Simple three-element triangle waveform for synthio.LFO (which does interpolation)"""
        return np.array((0, 32767, 0), dtype=np.int16)

    @staticmethod
    def lfo_triangle():
        """Simple four-element triangle waveform for synthio.LFO (which does interpolation)"""
        return np.array((0, 32767, 0, -32767), dtype=np.int16)

    @staticmethod
    def from_ar_times(attack_time=1, release_time=1):
        """
        Generate a fake Attack/Release 'Envelope' using an LFO waveform.
        This is a dumb way of doing it, but since we cannot get .value()
        out of Envelope, we have to fake it with an LFO.
        """
        # s = attack_time + release_time
        a10 = int(attack_time * 10)
        r10 = int(release_time * 10)
        a = [i * 65535 // a10 - 32767 for i in range(a10)]
        r = [32767 - i * 65535 // r10 for i in range(r10)]
        return Waves.from_list( a + [ 32767, ] + r )  # add a max middle

    @staticmethod
    def wav(filepath, size=256, pos=0):
        """Create a waveform from a WAV file using adafruit_wave"""
        with adafruit_wave.open(filepath) as w:
            if w.getsampwidth() != 2 or w.getnchannels() != 1:
                raise ValueError("unsupported format")
            # n = w.getnframes() if size==0 else size
            n = size
            w.setpos(pos)
            return np.frombuffer(w.readframes(n), dtype=np.int16)

    @staticmethod
    def wav_info(filepath):
        """return (nframes,nchannels,sampwidth) from a WAV filename"""
        with adafruit_wave.open(filepath) as w:
            return (w.getnframes(), w.getnchannels(), w.getsampwidth())
