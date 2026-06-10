#simon parker
import sounddevice as sd
import mido
import numpy as np
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()

sample_rate = 48000.
temporal_resolution = 0.01 #seconds of sound sent to callback function. 
                            #also length of envelope 
callback_buf_size = int(sample_rate * temporal_resolution)
volume = 0.708 #-3db

note_states = np.zeros(shape=(128,2), dtype=np.float32) 
#each entry is a note. [x, y], where x represents current state of the note, 
#y represents most recent midi event for that note
#ex. [1,0] means the note is playing, and we receive an off event. so we fade out, then set the note to [0,0]

note_phases = np.zeros(shape=(128,1), dtype=np.float32) #for keeping track of phase info for each note

intro_mask = np.linspace(0., 1., num=callback_buf_size, endpoint=False).reshape(-1, 1) #fading in/out
outro_mask = intro_mask[::-1].copy()


#takes midi note number and returns a frequency
def num_to_freq(n):
  return 440 * (2 ** ((n - 69) / (12)))


def callback(outdata, frames, time, status):
  global note_states, note_phases, intro_mask, outro_mask, volume
  output = np.zeros(shape=(frames,1), dtype=np.float32)
  active_notes = 0
  for i in range(128): #for each note
    if np.array_equal(note_states[i], [0,0]):
      continue 
    active_notes += 1
    freq = num_to_freq(i)
    sawtooth = (note_phases[i] + np.arange(frames).reshape(-1, 1) * (freq / sample_rate)) % 1.0
    note_phases[i] = (note_phases[i] + frames * (freq / sample_rate)) % 1.0
    if np.array_equal(note_states[i], [1,0]): #fade out
      output += sawtooth * volume * outro_mask
      note_states[i][0] = 0;
    elif np.array_equal(note_states[i], [0,1]): #fade in
      output += sawtooth * volume * intro_mask
      note_states[i][0] = 1;
    elif np.array_equal(note_states[i], [1,1]): #normal playing
      output += sawtooth * volume 
  if active_notes > 0:
    output /= active_notes
  outdata[:] = output


def midi_listener():
  global note_states
  with mido.open_input(mido.get_input_names()[0]) as port:
    for msg in port:
      if msg.type == 'note_on' and msg.velocity > 0:
        if args.verbose:
          print(msg.note, " ON")
        note_states[msg.note][1] = 1
      elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        if args.verbose:
          print(msg.note, " OFF")
        note_states[msg.note][1] = 0

# Run MIDI listener in background thread
t = threading.Thread(target=midi_listener, daemon=True)
t.start()
with sd.OutputStream(samplerate=sample_rate, blocksize=callback_buf_size,
                     channels=1, dtype='float32', callback=callback):
    print("Synth On")
    threading.Event().wait()  

