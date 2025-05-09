import time
#from adafruit_ticks import ticks_less, ticks_ms
try:
    from supervisor import ticks_ms
except:
    def ticks_ms():  # fallback when testing in CPython
        return time.monotonic_ns() // 1_000_000   

patterns = (
     (0, 4, 7, 12),
     (0, 3, 7, 10),
     (0, 3, 6, 3),    # FIXME
     (0, 5, 7, 12),
     (0, 12, 0, -12),
     (0, -12, -12, 0),
     (0, 0, 0, 0),
)
pattern_names = ('major', 'minor7', 'diminished',
                 'suspend4', 'octaves', 'octaves2', 'root', )

class Arpeggiator():
    def __init__(self, bpm=120, on_func=None, off_func=None):
        self.gate = 0.5
        self.rate = 2  # 1 = 1/4 note, 2 = 1/8th note, 4 = 16th note
        self.distance = 12  #
        self.steps = 1  # number of self.distance to do
        self.step = 0
        self.set_bpm(bpm)
        self.on_func = on_func
        self.off_func = off_func
        self.notes = []  # the list of notes currently pressed
        self.transpose = 0
        self.i = 0   # where in the notes list
        self.on = False
        self.held_note = None

    def set_bpm(self, bpm, rate=2):
        self.bpm = bpm
        self.rate = rate
        self.step_millis = 60_000 / self.rate / self.bpm
        
    def add_note(self, note):
        if note not in self.notes:
            self.notes.append(note)
            
    def del_note(self,note):
        if note in self.notes:
            self.notes.remove(note)
            if self.i >= len(self.notes):
                self.i = 0

    def start(self):
        self.next_millis = ticks_ms()
        self.on = True
    
    def stop(self):
        self.on = False
        self.off_func(self.held_note)  # turn off any held note
        
    def update(self):
        if not self.on:
            return
        now = ticks_ms()

        # trigger note-off after gate time
        if self.held_note and now - self.held_millis > 0:
            self.off_func(self.held_note)
            self.held_note = None

        # trigger note-on on if time to do so
        delta_millis = now - self.next_millis
        if delta_millis >= 0 and len(self.notes):  # time for new note
            note = self.notes[self.i] + self.distance * self.step
            #print("\t\t\t\t\t", "delta:",delta_millis)
            
            # trigger new note
            self.on_func(note)
            self.held_note = note  # save for note-off

            # set up when note off and next note happens
            self.held_millis = now + (self.step_millis * self.gate)
            self.next_millis = now + self.step_millis - delta_millis//2

            # go to next note
            self.i = (self.i+1) % len(self.notes)
            if self.i == 0:
                self.step = (self.step + 1) % self.steps
                
            
