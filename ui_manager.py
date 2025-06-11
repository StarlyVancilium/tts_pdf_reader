import tkinter as tk
from tkinter import filedialog, ttk, messagebox

class UIManager:
    def __init__(self, app):
        self.app = app # Reference to the main application instance
        self.root = app.root
        
        self.create_menu()
        self.create_widgets()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open PDF", command=self.app.browse_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        language_menu = tk.Menu(menubar, tearoff=0)
        # self.app.language_var is handled in app.py, but connected here
        for lang_name in self.app.language_options:
            language_menu.add_radiobutton(
                label=lang_name,
                variable=self.app.language_var,
                value=lang_name,
                command=self.app.change_language
            )
        menubar.add_cascade(label="Language", menu=language_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.app.show_about) # Call through app instance
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        file_frame = tk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        tk.Label(file_frame, text="PDF File:").pack(side=tk.LEFT)
        self.app.file_entry = tk.Entry(file_frame, width=50)
        self.app.file_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Button(file_frame, text="Browse", command=self.app.browse_file).pack(side=tk.LEFT)
        
        lang_frame = tk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=5)
        tk.Label(lang_frame, text="Current Language:").pack(side=tk.LEFT)
        self.app.lang_display = tk.Label(lang_frame, text="Indonesia", fg="blue")
        self.app.lang_display.pack(side=tk.LEFT, padx=5)
        
        page_frame = tk.Frame(main_frame)
        page_frame.pack(fill=tk.X, pady=5)
        tk.Label(page_frame, text="Page:").pack(side=tk.LEFT)
        self.app.page_spinbox = tk.Spinbox(page_frame, from_=1, to=1, width=5)
        self.app.page_spinbox.pack(side=tk.LEFT, padx=5)
        self.app.total_pages_label = tk.Label(page_frame, text=f"of {self.app.total_pages}")
        self.app.total_pages_label.pack(side=tk.LEFT)
        
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.app.text_display = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.app.text_display.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.app.text_display.yview)
        
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        self.app.play_button = tk.Button(control_frame, text="Play", command=self.app.play_page)
        self.app.play_button.pack(side=tk.LEFT, padx=5)
        self.app.stop_button = tk.Button(control_frame, text="Stop", command=self.app.stop_tts, state=tk.DISABLED)
        self.app.stop_button.pack(side=tk.LEFT, padx=5)
        
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        tk.Label(progress_frame, text="Conversion:").pack(side=tk.LEFT)
        self.app.conversion_progress = ttk.Progressbar(
            progress_frame, orient=tk.HORIZONTAL, length=300, mode='determinate'
        )
        self.app.conversion_progress.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.app.conversion_label = tk.Label(progress_frame, text="0%")
        self.app.conversion_label.pack(side=tk.LEFT)
        
        tk.Label(progress_frame, text="Playback:").pack(side=tk.LEFT)
        self.app.playback_progress = ttk.Progressbar(
            progress_frame, orient=tk.HORIZONTAL, length=300, mode='determinate'
        )
        self.app.playback_progress.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.app.playback_label = tk.Label(progress_frame, text="0%")
        self.app.playback_label.pack(side=tk.LEFT)
        
        self.app.status_var = tk.StringVar()
        self.app.status_var.set("Please select a PDF file")
        tk.Label(main_frame, textvariable=self.app.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X)