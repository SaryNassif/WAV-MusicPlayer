import customtkinter
from tkinter import filedialog
import sounddevice as sd
import numpy as np
import struct
from pathlib import Path

#FUNCTIONS
def theme():
    current_theme = customtkinter.get_appearance_mode()
    if current_theme == "Dark":
        customtkinter.set_appearance_mode("Light")
    else:
        customtkinter.set_appearance_mode("Dark")
playback_state ={"paused":False}
def restart_music():
  global audio_data, sample_rate,bits_per_sample,file_path_shortened

  play_audio(audio_data,sample_rate,bits_per_sample)
  playback_state["paused"]= False
  status_label.configure(text=f"Now Restarting {file_path_shortened.name}")

def pause_music():
    global playback_state,sample_rate

    if playback_state["paused"] == False:
        status_label.configure(text="Music Paused")
        sd.stop()
        playback_state["paused"] = True

def select_file():
    global audio_data,sample_rate,bits_per_sample,playback_state,file_path_shortened
    #Find WAV file
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav"), ("All files", "*.*")])
    with open(file_path, 'rb') as file:

        #Parse the riff header of a wav file
        riff_header = file.read(12)
        chunk_id, chunk_size, format_ = struct.unpack('<4sI4s', riff_header)
        
        if chunk_id != b'RIFF' or format_ != b'WAVE': #check if its wav file type
            raise ValueError("NOT a wav file type")
        
        #Parse the fmt subchunk
        fmt_subchunk = file.read(24)
        subchunk_1id, subchunk_1size, audio_format, number_of_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<4sIHHIIHH',fmt_subchunk)

        if subchunk_1id != b'fmt ':
            raise ValueError("Invalid fmt subchunk")
        
        #Parse the data subchunk
        data_subchunk = file.read(8)
        subchunk_2id, subchunk_2size = struct.unpack("<4sI",data_subchunk)

        if subchunk_2id != b'data':
            raise ValueError("Invalid data_subchunk")
        
        audio_data=file.read(subchunk_2size)

        print(f"Audio data size: {subchunk_2size} bytes")
        print(f"Sample rate: {sample_rate} Hz")
        print(f"Bits per sample: {bits_per_sample}")
        print(f"Byte rate: {byte_rate} bytes/second")
        print(f"Block align: {block_align} bytes")
        print(f"Audio data (first 100 bytes): {audio_data[:100]}")

        play_audio(audio_data,sample_rate,bits_per_sample)
        playback_state ={"paused":False}

        file_path_shortened = Path(file_path)
        status_label.configure(text=f"Playing {file_path_shortened.name}")
        
def play_audio(audiodata, samplerate, bitspersample):
    #Convert audio data to numpy array with correct data type
    if bitspersample == 16:
        dtype = np.int16
    elif bitspersample == 24:
        dtype = np.int32  #handle 24-bit audio
    else:
        raise ValueError("Unsupported bits per sample")

    audio_array = np.frombuffer(audiodata, dtype=dtype)
    sd.play(audio_array, samplerate=samplerate)

#GUI
customtkinter.set_default_color_theme("dark-blue")
customtkinter.set_appearance_mode("system")

root = customtkinter.CTk()
root.title("Music Player - Sary Nassif")
root.geometry("400x300")

label = customtkinter.CTkLabel(master=root, text="Music Player")
label.pack(padx=1, pady=1)

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

button = customtkinter.CTkButton(master=frame, text="Select File", command=select_file)
button.pack(pady=10)

button_frame = customtkinter.CTkFrame(master=frame)
button_frame.pack(pady=10)

restart_button = customtkinter.CTkButton(master=button_frame, text="🔁", command=restart_music, width=60, height=60, corner_radius=10)
restart_button.pack(side="left", padx=5)

pause_button = customtkinter.CTkButton(master=button_frame, text="⏸", command=pause_music, width=60, height=60, corner_radius=10)
pause_button.pack(side="left", padx=5)

status_label = customtkinter.CTkLabel(master=frame,text="No music playing")
status_label.pack(pady=5)

theme_button = customtkinter.CTkButton(master=root, text="💡", command=theme)
theme_button.pack(pady=10)

root.mainloop()
