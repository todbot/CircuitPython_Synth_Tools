import time
from supervisor import ticks_ms

class StepSequencer():
    def __init__(self, step_count, bpm, on_func=None, off_func=None, playing=False):
        self.steps_per_beat = 4  # 1 = 1/4 note, 2 = 8th note, 4 = 16th note
        self.step_count = step_count  # how big the sequence is
        self.bpm = bpm  # sets self.step_millis
        self.i = 0  # where in the step sequence we currently are
        
        # our sequence, list of step "objects": ie. list (notenum, vel, gate, on)
        self.steps = [ [0, 127, 0.5, True] for i in range(step_count)]
        
        self.on_func = on_func    # callback to invoke when 'note on' should be sent
        self.off_func = off_func  # callback to invoke when 'note off' should be sent
        self.gate_off_millis = 0  # when in the future our note off should occur
        self.held_note = (0,0,0,0)  # the current note being on, to be turned off
        self.transpose = 0
        self.playing = playing   # is sequence running or not (but use .play()/.pause())

    @property
    def bpm(self):  
        return 60_000 / self.step_millis / self.steps_per_beat
    @bpm.setter
    def bpm(self, bpm):
        """Sets the internal tempo. step_millis is time between steps"""
        self.step_millis = 60_000 / self.steps_per_beat / bpm
        #print("stepseq.set_bpm: %6.2f %d" % (self.step_millis, bpm) )

    def set_gates(self, gate):
        """Set all gates to a specified percentage 0-1"""
        for i in range(self.step_count):
            self.steps[i][2] = gate

    def start(self):
        """Start sequencer going"""
        self.next_millis = ticks_ms()
        self.playing = True
        self.error_millis = 0

    def stop(self):
        """Stop sequencer, turning off any currently-sounding note"""
        self.off_func(*self.held_note)
        self.playing = False
        self.i = 0

    def update(self):
        """Update the sequencer. Call as frequently as possible"""
        if not self.playing:
            return
        
        now = ticks_ms()
        delta_millis = now - self.next_millis
        
        if self.gate_off_millis > 0 and now - self.gate_off_millis >= 0:
            self.off_func(*self.held_note)
            self.gate_off_millis = 0

        if delta_millis >= 0:  # time to play
            print("                      delta_millis:", delta_millis, self.error_millis)
            self.error_millis += delta_millis
            held_note = self.steps[self.i]  # get new note to play
            held_note[0] += self.transpose  # adjust for transpose
            self.held_note = held_note      # save it for when we note_off it
            
            # trigger new note
            self.on_func(*held_note)   # held_note = (note,vel,gate,on)

            # prep for next step in sequence
            self.i = (self.i + 1) % self.step_count
            
            # set up when next note on is, with some error correction
            self.next_millis = now + self.step_millis
            if self.error_millis > 1:
                self.next_millis -= self.error_millis
                self.error_millis =0
            # next note off is some percentage smaller
            self.gate_off_millis = now + self.step_millis * self.held_note[2]


