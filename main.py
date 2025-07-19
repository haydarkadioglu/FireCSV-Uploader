"""
FireCSV Uploader - Main Application
A modern, modular Firebase CSV management tool
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from firebase.firebase_manager import FirebaseManager
from firebase.collection_manager import CollectionManager
from utils.csv_processor import CSVProcessor
from ui.upload_tab import UploadTab
from ui.browse_tab import BrowseTab


class FireCSVUploader:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("FireCSV Uploader v2.0")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Initialize managers
        self.firebase_manager = FirebaseManager()
        self.collection_manager = CollectionManager(None)  # Will be set when connected
        self.csv_processor = CSVProcessor(None)  # Will be set when connected
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Upload Tab
        upload_frame = ttk.Frame(notebook, padding="10")
        notebook.add(upload_frame, text="Upload CSV")
        
        # Browse Tab
        browse_frame = ttk.Frame(notebook, padding="10")
        notebook.add(browse_frame, text="Browse Collections")
        
        # Initialize tabs
        self.upload_tab = UploadTab(upload_frame, self.firebase_manager, self.csv_processor)
        self.browse_tab = BrowseTab(browse_frame, self.firebase_manager, self.collection_manager)
        
        # Grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Root grid settings
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Setup close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """Handle application closing"""
        self.firebase_manager.disconnect()
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = FireCSVUploader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
