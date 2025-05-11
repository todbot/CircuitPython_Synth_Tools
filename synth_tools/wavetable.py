# simple wavetable class for synthio
# part of todbot circuitpython synthio tutorial
# 10 Feb 2025 - @todbot / Tod Kurt
#

"""Wavetable class for synthio"""

import ulab.numpy as np
import adafruit_wave

class Wavetable:
    """ A 'waveform' for synthio.Note uses a WAV containing a wavetable
    and provides a scannable wave position."""
    def __init__(self, filepath, wave_len=256):
        self.w = adafruit_wave.open(filepath)
        self.wave_len = wave_len  # how many samples in each wave
        if self.w.getsampwidth() != 2 or self.w.getnchannels() != 1:
            raise ValueError("unsupported WAV format")
        # empty buffer we'll copy into
        self.waveform = np.zeros(wave_len, dtype=np.int16)
        self.num_waves = self.w.getnframes() // self.wave_len
        self.num_samples = self.w.getnframes()
        self.sample_rate = self.w.getframerate()
        self.wave_pos = 0

    @property
    def wave_pos(self):
        """return current position, 0-wave_len-1"""
        return self._wave_pos

    @wave_pos.setter
    def wave_pos(self, pos):
        """Pick where in wavetable to be, morphing between waves"""
        pos = min(max(pos, 0), self.num_waves-1)  # constrain
        samp_pos = int(pos) * self.wave_len  # get sample position
        self.w.setpos(samp_pos)
        wave_a = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        self.w.setpos(samp_pos + self.wave_len)  # one wave up
        wave_b = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        pos_frac = pos - int(pos)  # fractional position between wave A & B
        # mix waveforms A & B
        self.waveform[:] = Wavetable.lerp(wave_a, wave_b, pos_frac)
        self._wave_pos = pos

    @staticmethod
    def lerp(a, b, t):  # pylint: disable=invalid-name
        """Mix between values a and b, works with numpy arrays too, t ranges 0-1"""
        return (1-t)*a + t*b
