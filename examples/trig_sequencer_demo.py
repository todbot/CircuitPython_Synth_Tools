import time
import audiocore, audiomixer
from synth_setup import audio, SAMPLE_RATE, BUFFER_SIZE, knobA, knobB, keys
from trig_sequencer import TrigSequencer, ticks_ms

bpm = 120
trig_count = 3
step_count = 16
steps_per_beat = 4 # 2 = 8th note, 4 = 16th note

mixer = audiomixer.Mixer(voice_count=trig_count, channel_count=1,
                         sample_rate=SAMPLE_RATE, buffer_size=BUFFER_SIZE)
audio.play(mixer)

def trig_on(trig_num, wav):
    global last_ms
    mixer.voice[trig_num].play(wav, loop=False)
    print("trig_on:    %d" % (trig_num)) #midi_note, vel, gate, on), ticks_ms())
    
def trig_off(trig_num, wav): # midi_note, vel, gate, on):
    print("  trig_off: %3d" % (trig_num,)) #midi_note, vel, gate, on), int(ticks_ms()-last_ms))


drum_pattern1 = (
    (1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,1),   # bass drum
    (0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0),   # snare
    (1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1),   # hi hat
)

#drum_map = (36, 38, 42, 0, 0, 0, 0, 0)  # general midi drums
drum_map = (36, 48, 72, 0, 0, 0, 0, 0)  # midi notes 
drum_map = (
    audiocore.WaveFile("/kit0_909/00_909kick4.wav"),
    audiocore.WaveFile("/kit0_909/01_909snare2.wav"),
    audiocore.WaveFile("/kit0_909/02_909hatclosed2a.wav"),
)

seq = TrigSequencer(trig_count, step_count, steps_per_beat, on_func=trig_on, off_func=trig_off)
seq.bpm = bpm
seq.set_pattern(drum_pattern1)
seq.set_drum_map(drum_map)
seq.start()

print("step_millis:", seq.step_millis, "bpm:", seq.bpm)
print("pattern:", seq.trigs)

while True:
    seq.update()
    #time.sleep(0.001)


