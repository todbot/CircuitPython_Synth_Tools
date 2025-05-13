# SPDX-FileCopyrightText: Copyright (c) 2023 Tod Kurt
# SPDX-License-Identifier: MIT
"""
`pitch_glider`
================================================================================

`Glider` is a portamento feature for synthio.Notes. Attach to note.bend.

Part of synth_tools.

"""

import synthio
import ulab.numpy as np

def bend_amount(old_midi_note, new_midi_note):
    """Calculate how much note.bend has to happen between two notes"""
    return (new_midi_note - old_midi_note)  * (1/12)

class Glider:
    """Attach a Glider to note.bend to implement portamento"""
    def __init__(self, glide_time, midi_note):
        self.pos = synthio.LFO(once=True, rate=1/glide_time,
                               waveform=np.array((0,32767), dtype=np.int16))
        self.lerp = synthio.Math(synthio.MathOperation.CONSTRAINED_LERP,
                                 0, 0, self.pos)
        self.midi_note = midi_note

    def update(self, new_midi_note):
        """Update the glide destination based on new midi note"""
        self.lerp.a = bend_amount(new_midi_note, self.midi_note)
        self.lerp.b = 0  # end on the new note
        self.pos.retrigger()  # restart the lerp
        #print("bend_amount:", self.bend_amount(self.midi_note, new_midi_note),
        #      "old", self.midi_note, "new:", new_midi_note, self.lerp.a, self.lerp.b)
        self.midi_note = new_midi_note

    @property
    def glide_time(self):
        """Return glide time in seconds"""
        return 1/self.pos.rate
    @glide_time.setter
    def glide_time(self, glide_time):
        """Set glide time in seconds, sets the rate of underlying LFO"""
        self.pos.rate = 1/glide_time
