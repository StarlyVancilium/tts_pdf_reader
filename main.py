import PyPDF2
from gtts import gTTS
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pygame import mixer
import threading
import time

class PDFReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Text-to-Speech Reader")
        self.root.geometry("700x500")
        
        # Variabel
        self.pdf_path = ""
        self.pdf_text = {}
        self.current_page = 0
        self.total_pages = 0
        self.is_playing = False
        self.stop_playing = False
        self.temp_files = []
        self.language = "id"  # Default bahasa Indonesia
        self.language_options = {
            "Indonesia": "id",
            "English": "en"
        }
        
        # Inisialisasi mixer audio
        mixer.init()
        
        # UI Components
        self.create_widgets()
        self.create_menu()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open PDF", command=self.browse_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Menu Language
        language_menu = tk.Menu(menubar, tearoff=0)
        self.language_var = tk.StringVar(value="Indonesia")
        self.language_var.trace_add("write", self._update_language_display)
        for lang in self.language_options:
            language_menu.add_radiobutton(
                label=lang,
                variable=self.language_var,
                value=lang,
                command=self.change_language
            )
        menubar.add_cascade(label="Language", menu=language_menu)
        
        # Menu Help
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _update_language_display(self, *args):
        self.lang_display.config(text=self.language_var.get())
    
    def change_language(self):
        selected_lang = self.language_var.get()
        self.language = self.language_options[selected_lang]
        
        if self.language == "id":
            self.status_var.set("Bahasa diubah ke Indonesia")
        else:
            self.status_var.set("Language changed to English")
    
    def show_about(self):
        about_text = """PDF Text-to-Speech Reader
Version 1.0
Aplikasi untuk membaca PDF dengan text-to-speech
Mendukung bahasa Indonesia dan Inggris"""
        messagebox.showinfo("About", about_text)
    
    def create_widgets(self):
        # Frame utama
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection
        file_frame = tk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(file_frame, text="PDF File:").pack(side=tk.LEFT)
        self.file_entry = tk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT)
        
        # Language display
        lang_frame = tk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=5)
        tk.Label(lang_frame, text="Current Language:").pack(side=tk.LEFT)
        self.lang_display = tk.Label(lang_frame, text="Indonesia", fg="blue")
        self.lang_display.pack(side=tk.LEFT, padx=5)
        
        # Page selection
        page_frame = tk.Frame(main_frame)
        page_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(page_frame, text="Page:").pack(side=tk.LEFT)
        self.page_spinbox = tk.Spinbox(page_frame, from_=1, to=1, width=5)
        self.page_spinbox.pack(side=tk.LEFT, padx=5)
        self.total_pages_label = tk.Label(page_frame, text=f"of {self.total_pages}")
        self.total_pages_label.pack(side=tk.LEFT)
        
        # Text display with scrollbar
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_display = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.text_display.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.text_display.yview)
        
        # Controls - Hanya Play dan Stop
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.play_button = tk.Button(control_frame, text="Play", command=self.play_page)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="Stop", command=self.stop_tts, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        # Conversion progress
        tk.Label(progress_frame, text="Conversion:").pack(side=tk.LEFT)
        self.conversion_progress = ttk.Progressbar(
            progress_frame, 
            orient=tk.HORIZONTAL, 
            length=300, 
            mode='determinate'
        )
        self.conversion_progress.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.conversion_label = tk.Label(progress_frame, text="0%")
        self.conversion_label.pack(side=tk.LEFT)
        
        # Playback progress
        tk.Label(progress_frame, text="Playback:").pack(side=tk.LEFT)
        self.playback_progress = ttk.Progressbar(
            progress_frame, 
            orient=tk.HORIZONTAL, 
            length=300, 
            mode='determinate'
        )
        self.playback_progress.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.playback_label = tk.Label(progress_frame, text="0%")
        self.playback_label.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Please select a PDF file")
        tk.Label(main_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.load_pdf()
    
    def load_pdf(self):
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                self.total_pages = len(pdf_reader.pages)
                self.pdf_text = {}
                
                for page_num in range(self.total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    self.pdf_text[page_num] = text
                
                # Update UI
                self.page_spinbox.config(to=self.total_pages)
                self.total_pages_label.config(text=f"of {self.total_pages}")
                self.current_page = 0
                self.display_page(0)
                self.status_var.set(f"PDF loaded successfully - {self.total_pages} pages")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def display_page(self, page_num):
        if 0 <= page_num < self.total_pages:
            self.current_page = page_num
            self.page_spinbox.delete(0, tk.END)
            self.page_spinbox.insert(0, str(page_num + 1))
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, self.pdf_text.get(page_num, ""))
    
    def play_page(self):
        if not self.pdf_text:
            self.status_var.set("No text to read")
            return
        
        if self.is_playing:
            return
        
        try:
            page_num = int(self.page_spinbox.get()) - 1
            if 0 <= page_num < self.total_pages:
                self.display_page(page_num)
                text_to_read = self.pdf_text[page_num]
                
                # Reset progress bars
                self.conversion_progress['value'] = 0
                self.playback_progress['value'] = 0
                self.conversion_label.config(text="0%")
                self.playback_label.config(text="0%")
                
                # Hentikan pemutaran sebelumnya
                self.stop_tts()
                
                # Update UI
                self.is_playing = True
                self.stop_playing = False
                self.play_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                
                if self.language == "id":
                    self.status_var.set(f"Mengkonversi halaman {page_num + 1} ke audio...")
                else:
                    self.status_var.set(f"Converting page {page_num + 1} to audio...")
                
                # Buat thread untuk konversi dan pemutaran
                tts_thread = threading.Thread(target=self._process_and_play, args=(text_to_read, page_num))
                tts_thread.daemon = True
                tts_thread.start()
        except ValueError:
            self.status_var.set("Invalid page number")
    
    def _process_and_play(self, text, page_num):
        try:
            # Buat file audio sementara
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                temp_file_path = temp_audio.name
                self.temp_files.append(temp_file_path)
            
            # Split teks menjadi chunk untuk menghindari error gTTS
            chunks = self._split_text(text)
            audio_files = []
            
            for i, chunk in enumerate(chunks):
                progress = int((i / len(chunks)) * 100)
                self.root.after(0, self._update_conversion_progress, progress)
                
                if self.language == "id":
                    status_text = f"Mengkonversi halaman {page_num + 1} (bagian {i+1}/{len(chunks)})..."
                else:
                    status_text = f"Converting page {page_num + 1} (part {i+1}/{len(chunks)})..."
                
                self.root.after(0, lambda: self.status_var.set(status_text))
                
                try:
                    tts = gTTS(text=chunk, lang=self.language, slow=False)
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_chunk:
                        chunk_path = temp_chunk.name
                        tts.save(chunk_path)
                        audio_files.append(chunk_path)
                        self.temp_files.append(chunk_path)
                except Exception as e:
                    print(f"Error converting chunk {i}: {e}")
            
            # Gabungkan semua chunk audio jika ada lebih dari satu
            if len(audio_files) > 1:
                self._concatenate_audio(audio_files, temp_file_path)
            elif len(audio_files) == 1:
                os.replace(audio_files[0], temp_file_path)
            
            # Update conversion progress to 100%
            self.root.after(0, self._update_conversion_progress, 100)
            
            # Putar audio
            self._play_audio(temp_file_path, page_num)
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self._on_play_finished()
    
    def _update_conversion_progress(self, value):
        self.conversion_progress['value'] = value
        self.conversion_label.config(text=f"{value}%")
    
    def _update_playback_progress(self, value):
        self.playback_progress['value'] = value
        self.playback_label.config(text=f"{value}%")
    
    def _split_text(self, text, max_length=500):
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _concatenate_audio(self, input_files, output_file):
        from pydub import AudioSegment
        
        combined = AudioSegment.empty()
        for file in input_files:
            sound = AudioSegment.from_mp3(file)
            combined += sound
        
        combined.export(output_file, format="mp3")
    
    def _play_audio(self, audio_file, page_num):
        try:
            mixer.music.load(audio_file)
            mixer.music.play()
            
            # Dapatkan durasi audio
            sound = mixer.Sound(audio_file)
            duration = sound.get_length()  # dalam detik
            
            start_time = time.time()
            
            if self.language == "id":
                status_text = f"Memutar halaman {page_num + 1}"
            else:
                status_text = f"Playing page {page_num + 1}"
            
            self.root.after(0, lambda: self.status_var.set(status_text))
            
            # Update progress pemutaran
            while mixer.music.get_busy() and not self.stop_playing:
                elapsed = time.time() - start_time
                if duration > 0:
                    progress = min(100, (elapsed / duration) * 100)
                    self.root.after(0, self._update_playback_progress, int(progress))
                
                self.root.update()
                time.sleep(0.1)
            
            if not self.stop_playing:
                self.root.after(0, self._update_playback_progress, 100)
                if self.language == "id":
                    self.root.after(0, lambda: self.status_var.set("Pemutaran selesai"))
                else:
                    self.root.after(0, lambda: self.status_var.set("Playback completed"))
            
            self._on_play_finished()
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error memutar audio: {str(e)}"))
            self._on_play_finished()
    
    def stop_tts(self):
        self.stop_playing = True
        mixer.music.stop()
        self._on_play_finished()
        
        if self.language == "id":
            self.status_var.set("Pemutaran dihentikan")
        else:
            self.status_var.set("Playback stopped")
    
    def _on_play_finished(self):
        self.is_playing = False
        self.stop_playing = False
        self.play_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def __del__(self):
        # Bersihkan file temporer
        for file in self.temp_files:
            try:
                os.unlink(file)
            except:
                pass
        mixer.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReaderApp(root)
    root.mainloop()