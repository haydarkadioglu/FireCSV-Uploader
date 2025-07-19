"""
Upload CSV tab UI components
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from datetime import datetime
from typing import Optional, Callable


class UploadTab:
    """Upload CSV tab UI and functionality"""
    
    def __init__(self, parent, firebase_manager, csv_processor):
        self.parent = parent
        self.firebase_manager = firebase_manager
        self.csv_processor = csv_processor
        
        # Variables
        self.csv_path: Optional[str] = None
        self.subcol_mode = tk.StringVar(value="manual")
        self.batch_size_var = tk.StringVar(value="500")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the upload tab UI"""
        # Firebase Settings
        firebase_frame = ttk.LabelFrame(self.parent, text="Firebase Settings", padding="10")
        firebase_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(firebase_frame, text="Service Account Key JSON:").grid(row=0, column=0, sticky=tk.W)
        self.cred_label = ttk.Label(firebase_frame, text="No file selected", foreground="red")
        self.cred_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Button(firebase_frame, text="Select JSON File", 
                  command=self.select_credentials).grid(row=0, column=2, padx=(10, 0))
        
        ttk.Button(firebase_frame, text="Connect to Firebase", 
                  command=self.connect_firebase).grid(row=0, column=3, padx=(10, 0))
        
        self.connection_status = ttk.Label(firebase_frame, text="Not connected", foreground="red")
        self.connection_status.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # CSV Settings
        csv_frame = ttk.LabelFrame(self.parent, text="CSV Settings", padding="10")
        csv_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(csv_frame, text="CSV File:").grid(row=0, column=0, sticky=tk.W)
        self.csv_label = ttk.Label(csv_frame, text="No file selected", foreground="red")
        self.csv_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Button(csv_frame, text="Select CSV File", 
                  command=self.select_csv).grid(row=0, column=2, padx=(10, 0))
        
        ttk.Label(csv_frame, text="Collection Name:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.collection_entry = ttk.Entry(csv_frame, width=30)
        self.collection_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        self.collection_entry.bind('<KeyRelease>', lambda event: self.check_ready_to_upload())
        
        ttk.Label(csv_frame, text="Sub-Collection (Optional):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.subcollection_entry = ttk.Entry(csv_frame, width=30)
        self.subcollection_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        self.subcollection_entry.bind('<KeyRelease>', lambda event: self.check_ready_to_upload())
        
        # Sub-collection options
        subcol_options_frame = ttk.Frame(csv_frame)
        subcol_options_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(5, 10))
        
        ttk.Radiobutton(subcol_options_frame, text="Manual entry", variable=self.subcol_mode, 
                       value="manual", command=self.update_subcol_mode).grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(subcol_options_frame, text="From CSV filename", variable=self.subcol_mode, 
                       value="filename", command=self.update_subcol_mode).grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(subcol_options_frame, text="Add date", variable=self.subcol_mode, 
                       value="date", command=self.update_subcol_mode).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Label(csv_frame, text="Batch Size:").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        batch_size_spinbox = ttk.Spinbox(csv_frame, from_=1, to=500, 
                                        textvariable=self.batch_size_var, width=10)
        batch_size_spinbox.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # Preview
        preview_frame = ttk.LabelFrame(self.parent, text="CSV Preview", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=8, width=70)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Upload Control
        upload_control_frame = ttk.LabelFrame(self.parent, text="Upload", padding="10")
        upload_control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.upload_button = ttk.Button(upload_control_frame, text="Upload CSV to Firestore", 
                                       command=self.start_upload, state="disabled")
        self.upload_button.grid(row=0, column=0, padx=(0, 10))
        
        self.progress = ttk.Progressbar(upload_control_frame, mode='determinate')
        self.progress.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        self.status_label = ttk.Label(upload_control_frame, text="Ready")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(2, weight=1)
        firebase_frame.columnconfigure(1, weight=1)
        csv_frame.columnconfigure(1, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        upload_control_frame.columnconfigure(1, weight=1)
    
    def select_credentials(self):
        """Select Firebase service account JSON file"""
        file_path = filedialog.askopenfilename(
            title="Select Service Account Key JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.firebase_manager.cred_path = file_path
            self.cred_label.config(text=os.path.basename(file_path), foreground="green")
            self.check_ready_to_upload()
    
    def select_csv(self):
        """Select CSV file and show preview"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.csv_path = file_path
            self.csv_label.config(text=os.path.basename(file_path), foreground="green")
            self.preview_csv()
            self.update_subcol_mode()
            self.check_ready_to_upload()
    
    def update_subcol_mode(self):
        """Update sub-collection field based on mode"""
        mode = self.subcol_mode.get()
        
        if mode == "filename" and self.csv_path:
            filename = os.path.splitext(os.path.basename(self.csv_path))[0]
            self.subcollection_entry.delete(0, tk.END)
            self.subcollection_entry.insert(0, filename)
            self.subcollection_entry.config(state="readonly")
            
        elif mode == "date":
            today = datetime.now().strftime("%Y%m%d")
            current_text = self.subcollection_entry.get()
            if not current_text.endswith(today):
                self.subcollection_entry.delete(0, tk.END)
                base_name = current_text.replace(f"_{today}", "").replace(today, "")
                if base_name:
                    self.subcollection_entry.insert(0, f"{base_name}_{today}")
                else:
                    self.subcollection_entry.insert(0, today)
            self.subcollection_entry.config(state="readonly")
            
        else:  # manual
            self.subcollection_entry.config(state="normal")
    
    def get_final_collection_path(self) -> str:
        """Return final collection path"""
        main_collection = self.collection_entry.get().strip()
        sub_collection = self.subcollection_entry.get().strip()
        
        if sub_collection:
            return f"{main_collection}/{sub_collection}"
        return main_collection
    
    def preview_csv(self):
        """Show CSV file preview"""
        if not self.csv_path:
            return
        
        try:
            collection_path = self.get_final_collection_path()
            preview = f"Target Collection: {collection_path}\n\n"
            preview += self.csv_processor.preview_csv(self.csv_path)
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview)
            
        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"Error: {str(e)}")
    
    def connect_firebase(self):
        """Connect to Firebase"""
        if not self.firebase_manager.cred_path:
            messagebox.showerror("Error", "Please select service account JSON file first!")
            return
        
        if self.firebase_manager.connect(self.firebase_manager.cred_path):
            self.connection_status.config(text="Successfully connected!", foreground="green")
            self.check_ready_to_upload()
        else:
            self.connection_status.config(text="Connection failed!", foreground="red")
            messagebox.showerror("Firebase Connection Error", "Failed to connect to Firebase")
    
    def check_ready_to_upload(self):
        """Check if ready to upload"""
        if (self.firebase_manager.is_connected() and 
            self.csv_path and 
            self.collection_entry.get().strip()):
            self.upload_button.config(state="normal")
        else:
            self.upload_button.config(state="disabled")
    
    def start_upload(self):
        """Start upload process"""
        collection_name = self.collection_entry.get().strip()
        if not collection_name:
            messagebox.showerror("Error", "Please enter collection name!")
            return
        
        final_collection_path = self.get_final_collection_path()
        
        result = messagebox.askyesno(
            "Confirmation", 
            f"CSV file will be uploaded to:\n'{final_collection_path}'\n\nDo you want to continue?"
        )
        
        if result:
            self.upload_button.config(state="disabled")
            thread = threading.Thread(target=self.upload_csv, args=(final_collection_path,))
            thread.daemon = True
            thread.start()
    
    def upload_csv(self, collection_path: str):
        """Upload CSV file to Firestore"""
        def progress_callback(current: int, total: int):
            self.progress.config(maximum=total, value=current)
        
        def status_callback(status: str):
            self.status_label.config(text=status)
        
        try:
            self.csv_processor.db = self.firebase_manager.get_client()
            
            success = self.csv_processor.upload_csv(
                self.csv_path,
                collection_path,
                int(self.batch_size_var.get()),
                progress_callback,
                status_callback
            )
            
            if success:
                messagebox.showinfo("Success", f"CSV uploaded successfully to '{collection_path}'!")
            else:
                messagebox.showerror("Upload Error", "Failed to upload CSV file")
                
        except Exception as e:
            messagebox.showerror("Upload Error", str(e))
        
        finally:
            self.upload_button.config(state="normal")
            self.progress.config(value=0)
