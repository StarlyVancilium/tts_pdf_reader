import PyPDF2
import tkinter as tk
from tkinter import filedialog

class PDFManager:
    def __init__(self, app):
        self.app = app # Reference to the main application instance

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.app.pdf_path = file_path
            self.app.file_entry.delete(0, tk.END)
            self.app.file_entry.insert(0, file_path)
            self.load_pdf()

    def load_pdf(self):
        try:
            with open(self.app.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                self.app.total_pages = len(pdf_reader.pages)
                self.app.pdf_text = {}
                
                for page_num in range(self.app.total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    self.app.pdf_text[page_num] = text
                
                # Update UI elements via the app instance
                self.app.page_spinbox.config(to=self.app.total_pages)
                self.app.total_pages_label.config(text=f"of {self.app.total_pages}")
                self.app.current_page = 0
                self.display_page(0)
                self.app.status_var.set(f"PDF loaded successfully - {self.app.total_pages} pages")
        except Exception as e:
            self.app.status_var.set(f"Error: {str(e)}")

    def display_page(self, page_num):
        if 0 <= page_num < self.app.total_pages:
            self.app.current_page = page_num
            self.app.page_spinbox.delete(0, tk.END)
            self.app.page_spinbox.insert(0, str(page_num + 1))
            self.app.text_display.delete(1.0, tk.END)
            self.app.text_display.insert(tk.END, self.app.pdf_text.get(page_num, ""))