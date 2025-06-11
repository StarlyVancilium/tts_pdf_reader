import os
from pydub import AudioSegment

def split_text(text, max_length=500):
    """
    Splits text into smaller chunks to avoid gTTS errors with long texts.
    """
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Add back the period and space for proper sentences
        sentence_with_period = sentence + '. ' if not sentence.endswith('.') else sentence + ' '
        
        if len(current_chunk) + len(sentence_with_period) < max_length:
            current_chunk += sentence_with_period
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence_with_period
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def concatenate_audio(input_files, output_file):
    """
    Concatenates multiple MP3 audio files into a single MP3 file.
    Requires pydub to be installed.
    """
    combined = AudioSegment.empty()
    for file in input_files:
        try:
            sound = AudioSegment.from_mp3(file)
            combined += sound
        except Exception as e:
            print(f"Error loading audio file {file}: {e}")
            # Optionally, handle corrupted files or skip them
            continue
    
    combined.export(output_file, format="mp3")

def show_about_info():
    """
    Displays the application's about information.
    """
    import tkinter as tk
    from tkinter import messagebox
    
    about_text = """PDF Text-to-Speech Reader
Version 1.0
Aplikasi untuk membaca PDF dengan text-to-speech
Mendukung bahasa Indonesia dan Inggris"""
    messagebox.showinfo("About", about_text)