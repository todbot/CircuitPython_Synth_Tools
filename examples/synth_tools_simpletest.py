# SPDX-FileCopyrightText: Copyright (c) 2024 Tod Kurt
#
# SPDX-License-Identifier: Unlicense

import time, random
import board
import synthio

from synth_tools.patch import Patch
from synth_tools.instrument import Instrument

# set up synth out on PWM audio with an RC filter
import audiopwmio

audio = audiopwmio.PWMAudioOut(board.GP10)
synth = synthio.Synthesizer(sample_rate=22050)
audio.play(synth)

# create a synth patch
patch1 = Patch("one")
patch1.waveA = "SAW"
patch1.waveB = "NZE"
patch1.wave_mix = 0.5  # mix equal between both saw & noise
patch1.amp_env.attack_time = 0.01
patch1.amp_env.release_time = 0.5
patch1.filt_env.attack_time = 1.1
patch1.filt_env.release_time = 0.8
patch1.filt_env_amount = 0.5
patch1.filt_f = 345
patch1.filt_q = 1.7

instrument = PolyWaveSynth(synth, patch1)

last_note_time = 0
note_num = 0

while True:
    instrument.update()
    if time.monotonic() - last_note_time >= 0.3:
        last_note_time = time.monotonic()
        if not note_num:
            note_num = random.choice(36, 41, 43, 48)
            instrument.note_on(notenum)
        else:
            instrument.note_off(note_num)
            note_num = 0
