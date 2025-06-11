import tkinter as tk
from pygame import mixer
import os

from .ui_manager import UIManager
from .pdf_manager import PDFManager
from .tts_manager import TTSManager
from .utils import show_about_info # Import the standalone function

class PDFReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Text-to-Speech Reader")
        self.root.geometry("700x500")
        
        # Application state variables
        self.pdf_path = ""
        self.pdf_text = {}
        self.current_page = 0
        self.total_pages = 0
        self.is_playing = False
        self.stop_playing = False
        self.language = "id"  # Default bahasa Indonesia
        self.language_options = {
            "Indonesia": "id",
            "English": "en"
        }
        
        # Tkinter variables (to be connected by UIManager)
        self.file_entry = None
        self.lang_display = None
        self.page_spinbox = None
        self.total_pages_label = None
        self.text_display = None
        self.play_button = None
        self.stop_button = None
        self.conversion_progress = None
        self.conversion_label = None
        self.playback_progress = None
        self.playback_label = None
        self.status_var = None
        
        # Tkinter StringVar for language selection
        self.language_var = tk.StringVar(value="Indonesia")
        # Trace for immediate UI update on language change
        self.language_var.trace_add("write", self._update_language_display)
        
        # Initialize manager classes, passing self (the app instance)
        self.ui_manager = UIManager(self)
        self.pdf_manager = PDFManager(self)
        self.tts_manager = TTSManager(self)
        
        # Bind methods for UI callbacks (some are handled in UIManager, some here)
        self.browse_file = self.pdf_manager.browse_file
        self.play_page = self.tts_manager.play_page
        self.stop_tts = self.tts_manager.stop_tts_playback
        self.show_about = show_about_info # Call the standalone function
        
    def _update_language_display(self, *args):
        # This method is part of the app's state and UI connection
        # It updates the language display label in the UI
        if self.lang_display: # Ensure the widget is created
            self.lang_display.config(text=self.language_var.get())
    
    def change_language(self):
        selected_lang_name = self.language_var.get()
        self.language = self.language_options.get(selected_lang_name, "id") # Safely get language code
        
        if self.language == "id":
            self.status_var.set("Bahasa diubah ke Indonesia")
        else:
            self.status_var.set("Language changed to English")
    
    def on_closing(self):
        # Perform cleanup before closing the application
        self.tts_manager.cleanup_temp_files()
        self.tts_manager.quit_mixer()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReaderApp(root)
    # Register the cleanup function to be called when the window is closed
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()