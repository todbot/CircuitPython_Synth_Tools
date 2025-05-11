# simple wavetable class for synthio
# part of todbot circuitpython synthio tutorial
# 10 Feb 2025 - @todbot / Tod Kurt
#

"""Wavetable class for synthio"""

import ulab.numpy as np
import adafruit_wave

def lerp(a, b, t):  # pylint: disable=invalid-name
    """Mix between values a and b, works with numpy arrays too, t ranges 0-1"""
    return (1-t)*a + t*b

class Wavetable:
    """
    A 'waveform' for synthio.Note that uses a wavetable with a scannable
    wave position. A wavetable is usually a collection of harmonically-related
    single-cycle waveforms. Often the waveforms are 256 samples long and
    the wavetable containing 64 waves. This wavetable oscillator lets the
    user pick which of those 64 waves to use, usually allowing one to mix
    between two waves.

    Some example wavetables usable by this classs: https://waveeditonline.com/

    In this implementation, you select a wave position (wave_pos) that can be
    fractional, and the fractional part allows for mixing of the waves
    """
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
        """
        Pick where in wavetable to be, morphing between waves.
        wave_pos integer part of specifies which wave from 0-num_waves,
        and fractional part specifies mix between wave and wave next to it
        (e.g. wave_pos=15.66 chooses 1/3 of waveform 15 and 2/3 of waveform 16)
        """
        pos = min(max(pos, 0), self.num_waves-1)  # constrain
        samp_pos = int(pos) * self.wave_len  # get sample position
        self.w.setpos(samp_pos)
        wave_a = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        self.w.setpos(samp_pos + self.wave_len)  # one wave up
        wave_b = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        pos_frac = pos - int(pos)  # fractional position between wave A & B
        # mix waveforms A & B
        self.waveform[:] = lerp(wave_a, wave_b, pos_frac)
        self._wave_pos = pos
