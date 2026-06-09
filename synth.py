#simon parker
import sounddevice as sd
import mido
import numpy as np
import threading

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

intro_mask = np.linspace(0., 1., num=callback_buf_size, endpoint=False) #fading in/out
outro_mask = intro_mask[::-1].copy()

'''
def callback(indata, outdata, frames, time, status):
  global note_states, note_phases, intro_mask, outro_mask
  output = np.zeros(shape=(frames,1), dtype=np.float32)
  if np.array_equal(note_states[21], [1,0]): #fade out
  elif np.array_equal(note_states[21], [0,1]): #fade in
  elif np.array_equal(note_states[21], [1,1]): #normal playing
  outdata[:] = output
'''





def midi_listener():
  global envelope_states
  with mido.open_input(mido.get_input_names()[0]) as port:
    for msg in port:
      if msg.type == 'note_on' and msg.velocity > 0:
        envelope_states[msg.note][1] = 1
        print(msg.note, envelope_states[msg.note])
      elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        envelope_states[msg.note][1] = 0
        print(msg.note, envelope_states[msg.note])

# Run MIDI listener in background thread
t = threading.Thread(target=midi_listener, daemon=True)
t.start()
threading.Event().wait()

