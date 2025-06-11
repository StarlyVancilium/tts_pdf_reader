from gtts import gTTS
import os
import tempfile
from pygame import mixer
import threading
import time

from .utils import split_text, concatenate_audio # Import from local utils.py

class TTSManager:
    def __init__(self, app):
        self.app = app # Reference to the main application instance
        mixer.init()
        self.temp_files = [] # To keep track of temporary audio files

    def play_page(self):
        if not self.app.pdf_text:
            self.app.status_var.set("No text to read")
            return
        
        if self.app.is_playing:
            return
        
        try:
            page_num = int(self.app.page_spinbox.get()) - 1
            if 0 <= page_num < self.app.total_pages:
                self.app.pdf_manager.display_page(page_num) # Delegate to PDFManager
                text_to_read = self.app.pdf_text[page_num]
                
                self.app.conversion_progress['value'] = 0
                self.app.playback_progress['value'] = 0
                self.app.conversion_label.config(text="0%")
                self.app.playback_label.config(text="0%")
                
                self.stop_tts_playback() # Ensure previous playback is stopped
                
                self.app.is_playing = True
                self.app.stop_playing = False
                self.app.play_button.config(state=tk.DISABLED)
                self.app.stop_button.config(state=tk.NORMAL)
                
                status_msg = (f"Mengkonversi halaman {page_num + 1} ke audio..." if self.app.language == "id" 
                              else f"Converting page {page_num + 1} to audio...")
                self.app.status_var.set(status_msg)
                
                tts_thread = threading.Thread(target=self._process_and_play, args=(text_to_read, page_num))
                tts_thread.daemon = True
                tts_thread.start()
        except ValueError:
            self.app.status_var.set("Invalid page number")

    def _process_and_play(self, text, page_num):
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                temp_file_path = temp_audio.name
                self.temp_files.append(temp_file_path)
            
            chunks = split_text(text) # Use split_text from utils
            audio_files = []
            
            for i, chunk in enumerate(chunks):
                progress = int(((i + 1) / len(chunks)) * 100) # Ensure 100% for last chunk
                self.app.root.after(0, lambda: self.app.conversion_progress.config(value=progress))
                self.app.root.after(0, lambda: self.app.conversion_label.config(text=f"{progress}%"))
                
                status_text = (f"Mengkonversi halaman {page_num + 1} (bagian {i+1}/{len(chunks)})..." if self.app.language == "id"
                               else f"Converting page {page_num + 1} (part {i+1}/{len(chunks)})...")
                self.app.root.after(0, lambda: self.app.status_var.set(status_text))
                
                try:
                    tts = gTTS(text=chunk, lang=self.app.language, slow=False)
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_chunk:
                        chunk_path = temp_chunk.name
                        tts.save(chunk_path)
                        audio_files.append(chunk_path)
                        self.temp_files.append(chunk_path)
                except Exception as e:
                    print(f"Error converting chunk {i}: {e}")
                    self.app.root.after(0, lambda: self.app.status_var.set(f"Error converting chunk: {str(e)}"))
                    self._on_play_finished()
                    return # Stop processing on error
            
            if len(audio_files) > 1:
                concatenate_audio(audio_files, temp_file_path) # Use concatenate_audio from utils
            elif len(audio_files) == 1:
                os.replace(audio_files[0], temp_file_path)
            
            self.app.root.after(0, lambda: self.app.conversion_progress.config(value=100))
            self.app.root.after(0, lambda: self.app.conversion_label.config(text="100%"))
            
            self._play_audio(temp_file_path, page_num)
            
        except Exception as e:
            self.app.root.after(0, lambda: self.app.status_var.set(f"Error: {str(e)}"))
            self._on_play_finished()

    def _play_audio(self, audio_file, page_num):
        try:
            mixer.music.load(audio_file)
            mixer.music.play()
            
            sound = mixer.Sound(audio_file)
            duration = sound.get_length()
            start_time = time.time()
            
            status_text = (f"Memutar halaman {page_num + 1}" if self.app.language == "id"
                           else f"Playing page {page_num + 1}")
            self.app.root.after(0, lambda: self.app.status_var.set(status_text))
            
            while mixer.music.get_busy() and not self.app.stop_playing:
                elapsed = time.time() - start_time
                if duration > 0:
                    progress = min(100, (elapsed / duration) * 100)
                    self.app.root.after(0, lambda: self.app.playback_progress.config(value=int(progress)))
                    self.app.root.after(0, lambda: self.app.playback_label.config(text=f"{int(progress)}%"))
                
                self.app.root.update()
                time.sleep(0.1)
            
            if not self.app.stop_playing:
                self.app.root.after(0, lambda: self.app.playback_progress.config(value=100))
                self.app.root.after(0, lambda: self.app.playback_label.config(text="100%"))
                completion_msg = ("Pemutaran selesai" if self.app.language == "id" 
                                  else "Playback completed")
                self.app.root.after(0, lambda: self.app.status_var.set(completion_msg))
            
            self._on_play_finished()
            
        except Exception as e:
            self.app.root.after(0, lambda: self.app.status_var.set(f"Error memutar audio: {str(e)}"))
            self._on_play_finished()
    
    def stop_tts_playback(self):
        self.app.stop_playing = True
        mixer.music.stop()
        self._on_play_finished()
        
        status_msg = ("Pemutaran dihentikan" if self.app.language == "id" 
                      else "Playback stopped")
        self.app.status_var.set(status_msg)

    def _on_play_finished(self):
        self.app.is_playing = False
        self.app.stop_playing = False
        self.app.play_button.config(state=tk.NORMAL)
        self.app.stop_button.config(state=tk.DISABLED)

    def cleanup_temp_files(self):
        for file in self.temp_files:
            try:
                os.unlink(file)
            except OSError as e:
                print(f"Error deleting temporary file {file}: {e}")
        self.temp_files.clear()
        
    def quit_mixer(self):
        mixer.quit()