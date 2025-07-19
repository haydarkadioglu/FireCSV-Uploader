import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import csv
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import threading
from datetime import datetime

class FireCSVUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("Firebase CSV Uploader")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Firebase variables
        self.db = None
        self.cred_path = None
        self.csv_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
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
        
        # Setup upload tab
        self.setup_upload_tab(upload_frame)
        
        # Setup browse tab
        self.setup_browse_tab(browse_frame)
        
        # Grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Root grid settings
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def setup_upload_tab(self, parent):
        # Firebase Settings
        firebase_frame = ttk.LabelFrame(parent, text="Firebase Settings", padding="10")
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
        csv_frame = ttk.LabelFrame(parent, text="CSV Settings", padding="10")
        csv_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(csv_frame, text="CSV File:").grid(row=0, column=0, sticky=tk.W)
        self.csv_label = ttk.Label(csv_frame, text="No file selected", foreground="red")
        self.csv_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Button(csv_frame, text="Select CSV File", 
                  command=self.select_csv).grid(row=0, column=2, padx=(10, 0))
        
        ttk.Label(csv_frame, text="Collection Name:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.collection_entry = ttk.Entry(csv_frame, width=30)
        self.collection_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        # Check when collection name changes
        self.collection_entry.bind('<KeyRelease>', lambda event: self.check_ready_to_upload())
        
        ttk.Label(csv_frame, text="Sub-Collection (Optional):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.subcollection_entry = ttk.Entry(csv_frame, width=30)
        self.subcollection_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        self.subcollection_entry.bind('<KeyRelease>', lambda event: self.check_ready_to_upload())
        
        # Sub-collection options
        subcol_options_frame = ttk.Frame(csv_frame)
        subcol_options_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(5, 10))
        
        self.subcol_mode = tk.StringVar(value="manual")
        ttk.Radiobutton(subcol_options_frame, text="Manual entry", variable=self.subcol_mode, 
                       value="manual", command=self.update_subcol_mode).grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(subcol_options_frame, text="From CSV filename", variable=self.subcol_mode, 
                       value="filename", command=self.update_subcol_mode).grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(subcol_options_frame, text="Add date", variable=self.subcol_mode, 
                       value="date", command=self.update_subcol_mode).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Label(csv_frame, text="Batch Size:").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        self.batch_size_var = tk.StringVar(value="500")
        batch_size_spinbox = ttk.Spinbox(csv_frame, from_=1, to=500, 
                                        textvariable=self.batch_size_var, width=10)
        batch_size_spinbox.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # Preview
        preview_frame = ttk.LabelFrame(parent, text="CSV Preview", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=8, width=70)
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Upload Control
        upload_control_frame = ttk.LabelFrame(parent, text="Upload", padding="10")
        upload_control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.upload_button = ttk.Button(upload_control_frame, text="Upload CSV to Firestore", 
                                       command=self.start_upload, state="disabled")
        self.upload_button.grid(row=0, column=0, padx=(0, 10))
        
        self.progress = ttk.Progressbar(upload_control_frame, mode='determinate')
        self.progress.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        self.status_label = ttk.Label(upload_control_frame, text="Ready")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Grid weights for upload tab
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)
        firebase_frame.columnconfigure(1, weight=1)
        csv_frame.columnconfigure(1, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        upload_control_frame.columnconfigure(1, weight=1)
    
    def setup_browse_tab(self, parent):
        # Refresh button
        refresh_frame = ttk.Frame(parent)
        refresh_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(refresh_frame, text="Refresh Collections", 
                  command=self.refresh_collections).grid(row=0, column=0, padx=(0, 10))
        
        self.collection_count_label = ttk.Label(refresh_frame, text="")
        self.collection_count_label.grid(row=0, column=1, padx=(10, 0))
        
        # Collections tree
        collections_frame = ttk.LabelFrame(parent, text="Collections & Documents", padding="10")
        collections_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Treeview with scrollbars
        tree_frame = ttk.Frame(collections_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.collections_tree = ttk.Treeview(tree_frame, columns=("Type", "Count", "Last Modified"), show="tree headings")
        self.collections_tree.heading("#0", text="Name")
        self.collections_tree.heading("Type", text="Type")
        self.collections_tree.heading("Count", text="Count")
        self.collections_tree.heading("Last Modified", text="Last Modified")
        
        self.collections_tree.column("#0", width=300)
        self.collections_tree.column("Type", width=100)
        self.collections_tree.column("Count", width=80)
        self.collections_tree.column("Last Modified", width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.collections_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.collections_tree.xview)
        self.collections_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.collections_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Action buttons
        action_frame = ttk.Frame(collections_frame)
        action_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(action_frame, text="View Details", 
                  command=self.view_collection_details).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(action_frame, text="Export to CSV", 
                  command=self.export_collection).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(action_frame, text="Delete Collection", 
                  command=self.delete_collection).grid(row=0, column=2, padx=(0, 10))
        
        # Status label for browse tab
        self.status_label_browse = ttk.Label(collections_frame, text="Ready - Click 'Refresh Collections' to load data")
        self.status_label_browse.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        # Grid weights for browse tab
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        collections_frame.columnconfigure(0, weight=1)
        collections_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def select_credentials(self):
        """Select Firebase service account JSON file"""
        file_path = filedialog.askopenfilename(
            title="Select Service Account Key JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.cred_path = file_path
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
            self.update_subcol_mode()  # Update sub-collection mode
            self.check_ready_to_upload()
    
    def update_subcol_mode(self):
        """Update sub-collection field based on mode"""
        if not hasattr(self, 'subcol_mode'):
            return
            
        mode = self.subcol_mode.get()
        
        if mode == "filename" and self.csv_path:
            # Get CSV filename (without extension)
            filename = os.path.splitext(os.path.basename(self.csv_path))[0]
            self.subcollection_entry.delete(0, tk.END)
            self.subcollection_entry.insert(0, filename)
            self.subcollection_entry.config(state="readonly")
            
        elif mode == "date":
            # Add today's date
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
    
    def get_final_collection_path(self):
        """Return final collection path"""
        main_collection = self.collection_entry.get().strip()
        sub_collection = self.subcollection_entry.get().strip()
        
        if sub_collection:
            return f"{main_collection}/{sub_collection}"
        return main_collection
    
    def preview_csv(self):
        """Show CSV file preview"""
        try:
            with open(self.csv_path, 'r', encoding='utf-8-sig', newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)
                
                if not rows:
                    self.preview_text.delete(1.0, tk.END)
                    self.preview_text.insert(1.0, "CSV file is empty!")
                    return
                
                headers = rows[0]
                total_rows = len(rows) - 1  # Excluding header
                
                # Collection path info
                collection_path = self.get_final_collection_path()
                
                preview = f"Target Collection: {collection_path}\n"
                preview += f"Total rows: {total_rows}\n"
                preview += f"Columns: {headers}\n\n"
                preview += "First 5 rows:\n"
                
                # Header + first 5 data rows
                for i, row in enumerate(rows[:6]):
                    if i == 0:
                        preview += f"HEADER: {row}\n"
                    else:
                        preview += f"Row {i}: {row}\n"
                
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, preview)
                
        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"Error: {str(e)}")
    
    def connect_firebase(self):
        """Connect to Firebase"""
        if not self.cred_path:
            messagebox.showerror("Error", "Please select service account JSON file first!")
            return
        
        try:
            # Clear previous connection
            if firebase_admin._apps:
                firebase_admin.delete_app(firebase_admin.get_app())
            
            # New connection
            cred = credentials.Certificate(self.cred_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            
            self.connection_status.config(text="Successfully connected!", foreground="green")
            self.check_ready_to_upload()
            
        except Exception as e:
            self.connection_status.config(text=f"Connection error: {str(e)}", foreground="red")
            messagebox.showerror("Firebase Connection Error", str(e))
    
    def check_ready_to_upload(self):
        """Check if ready to upload"""
        if (self.db is not None and 
            self.csv_path and 
            self.collection_entry.get().strip()):
            self.upload_button.config(state="normal")
        else:
            self.upload_button.config(state="disabled")
    
    def refresh_collections(self):
        """Refresh collections list"""
        if not self.db:
            messagebox.showerror("Error", "Please connect to Firebase first!")
            return
        
        try:
            # Clear existing items
            for item in self.collections_tree.get_children():
                self.collections_tree.delete(item)
            
            # Get all collections
            collections = self.db.collections()
            collection_count = 0
            
            for collection in collections:
                collection_count += 1
                collection_name = collection.id
                
                # Get document count
                docs = list(collection.limit(1000).stream())  # Limit for performance
                doc_count = len(docs)
                
                # Get last modified date from first document
                last_modified = "N/A"
                if docs:
                    first_doc = docs[0]
                    if '_upload_info' in first_doc.to_dict():
                        upload_info = first_doc.to_dict()['_upload_info']
                        if 'uploaded_at' in upload_info:
                            last_modified = upload_info['uploaded_at'].strftime("%Y-%m-%d %H:%M")
                
                # Add collection to tree
                collection_item = self.collections_tree.insert("", "end", text=collection_name, 
                                                             values=("Collection", doc_count, last_modified))
                
                # Check for sub-collections (documents that might have sub-collections)
                for doc in collection.limit(10).stream():  # Check first 10 docs for sub-collections
                    doc_collections = doc.reference.collections()
                    for sub_collection in doc_collections:
                        sub_docs = list(sub_collection.limit(100).stream())
                        sub_count = len(sub_docs)
                        
                        sub_last_modified = "N/A"
                        if sub_docs:
                            first_sub_doc = sub_docs[0]
                            if '_upload_info' in first_sub_doc.to_dict():
                                sub_upload_info = first_sub_doc.to_dict()['_upload_info']
                                if 'uploaded_at' in sub_upload_info:
                                    sub_last_modified = sub_upload_info['uploaded_at'].strftime("%Y-%m-%d %H:%M")
                        
                        self.collections_tree.insert(collection_item, "end", 
                                                    text=f"{doc.id}/{sub_collection.id}", 
                                                    values=("Sub-Collection", sub_count, sub_last_modified))
            
            self.collection_count_label.config(text=f"Found {collection_count} collections")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh collections: {str(e)}")
    
    def view_collection_details(self):
        """View details of selected collection"""
        selection = self.collections_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a collection first!")
            return
        
        item = selection[0]
        collection_name = self.collections_tree.item(item)['text']
        collection_type = self.collections_tree.item(item)['values'][0]
        
        try:
            # Create details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Collection Details: {collection_name}")
            details_window.geometry("600x400")
            
            # Collection info
            info_frame = ttk.LabelFrame(details_window, text="Collection Information", padding="10")
            info_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(info_frame, text=f"Name: {collection_name}").pack(anchor="w")
            ttk.Label(info_frame, text=f"Type: {collection_type}").pack(anchor="w")
            
            # Sample documents
            docs_frame = ttk.LabelFrame(details_window, text="Sample Documents", padding="10")
            docs_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            docs_text = scrolledtext.ScrolledText(docs_frame, height=15, width=70)
            docs_text.pack(fill="both", expand=True)
            
            # Get collection reference
            if "/" in collection_name:
                # Sub-collection
                parts = collection_name.split("/")
                parent_collection = parts[0]
                parent_doc = parts[1]
                sub_collection = parts[2] if len(parts) > 2 else "data"
                
                collection_ref = self.db.collection(parent_collection).document(parent_doc).collection(sub_collection)
            else:
                collection_ref = self.db.collection(collection_name)
            
            # Get sample documents
            docs = list(collection_ref.limit(5).stream())
            
            if docs:
                docs_text.insert(tk.END, f"Showing first {len(docs)} documents:\n\n")
                for i, doc in enumerate(docs, 1):
                    docs_text.insert(tk.END, f"Document {i} (ID: {doc.id}):\n")
                    doc_data = doc.to_dict()
                    docs_text.insert(tk.END, json.dumps(doc_data, indent=2, default=str))
                    docs_text.insert(tk.END, "\n" + "="*50 + "\n\n")
            else:
                docs_text.insert(tk.END, "No documents found in this collection.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load collection details: {str(e)}")
    
    def export_collection(self):
        """Export collection to CSV"""
        selection = self.collections_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a collection first!")
            return
        
        item = selection[0]
        collection_name = self.collections_tree.item(item)['text']
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Save CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialvalue=f"{collection_name.replace('/', '_')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            # Get collection reference
            if "/" in collection_name:
                # Sub-collection
                parts = collection_name.split("/")
                parent_collection = parts[0]
                parent_doc = parts[1]
                sub_collection = parts[2] if len(parts) > 2 else "data"
                
                collection_ref = self.db.collection(parent_collection).document(parent_doc).collection(sub_collection)
            else:
                collection_ref = self.db.collection(collection_name)
            
            # Get all documents
            docs = list(collection_ref.stream())
            
            if not docs:
                messagebox.showinfo("Info", "No documents found in this collection.")
                return
            
            # Get all field names
            all_fields = set()
            doc_data_list = []
            
            for doc in docs:
                doc_data = doc.to_dict()
                all_fields.update(doc_data.keys())
                doc_data_list.append(doc_data)
            
            # Remove metadata field from export
            all_fields.discard('_upload_info')
            all_fields = sorted(list(all_fields))
            
            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=all_fields)
                writer.writeheader()
                
                for doc_data in doc_data_list:
                    # Remove metadata and write row
                    doc_data.pop('_upload_info', None)
                    writer.writerow(doc_data)
            
            messagebox.showinfo("Success", f"Collection exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export collection: {str(e)}")
    
    def delete_collection(self):
        """Delete selected collection"""
        selection = self.collections_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a collection first!")
            return
        
        item = selection[0]
        collection_name = self.collections_tree.item(item)['text']
        
        # Confirmation
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the collection '{collection_name}'?\n\nThis action cannot be undone!"
        )
        
        if not result:
            return
        
        try:
            # Get collection reference
            if "/" in collection_name:
                # Sub-collection
                parts = collection_name.split("/")
                parent_collection = parts[0]
                parent_doc = parts[1]
                sub_collection = parts[2] if len(parts) > 2 else "data"
                
                collection_ref = self.db.collection(parent_collection).document(parent_doc).collection(sub_collection)
            else:
                collection_ref = self.db.collection(collection_name)
            
            # Delete all documents in batches
            docs = list(collection_ref.limit(500).stream())
            while docs:
                batch = self.db.batch()
                for doc in docs:
                    batch.delete(doc.reference)
                batch.commit()
                
                # Get next batch
                docs = list(collection_ref.limit(500).stream())
            
            messagebox.showinfo("Success", f"Collection '{collection_name}' deleted successfully!")
            self.refresh_collections()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete collection: {str(e)}")
    
    def check_ready_to_upload(self):
        """Check if ready to upload"""
        if (self.db is not None and 
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
        
        # Get final collection path
        final_collection_path = self.get_final_collection_path()
        
        # Confirmation message
        result = messagebox.askyesno(
            "Confirmation", 
            f"CSV file will be uploaded to:\n'{final_collection_path}'\n\nDo you want to continue?"
        )
        
        if result:
            # Upload in thread
            self.upload_button.config(state="disabled")
            thread = threading.Thread(target=self.upload_csv, args=(final_collection_path,))
            thread.daemon = True
            thread.start()
    
    def upload_csv(self, collection_path):
        """Upload CSV file to Firestore"""
        try:
            # Read CSV
            self.root.after(0, lambda: self.status_label.config(text="Reading CSV file..."))
            
            with open(self.csv_path, 'r', encoding='utf-8-sig', newline='') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
            
            total_rows = len(rows)
            batch_size = int(self.batch_size_var.get())
            
            self.root.after(0, lambda: self.progress.config(maximum=total_rows))
            
            # Sub-collection support
            if "/" in collection_path:
                # Main collection/Sub-collection structure
                parts = collection_path.split("/")
                main_collection = parts[0]
                sub_collection = parts[1]
                
                # Create a dummy document in main collection and add sub-collection
                main_doc_ref = self.db.collection(main_collection).document(sub_collection)
                collection_ref = main_doc_ref.collection("data")
            else:
                # Normal collection
                collection_ref = self.db.collection(collection_path)
            
            uploaded = 0
            
            # Upload in batches
            for i in range(0, total_rows, batch_size):
                batch = self.db.batch()
                batch_data = rows[i:i+batch_size]
                
                for row_data in batch_data:
                    # Clean data for Firestore
                    doc_data = self.clean_firestore_data(row_data)
                    
                    # Add metadata
                    doc_data['_upload_info'] = {
                        'uploaded_at': datetime.now(),
                        'source_file': os.path.basename(self.csv_path),
                        'collection_path': collection_path
                    }
                    
                    # Document ID (automatic)
                    doc_ref = collection_ref.document()
                    batch.set(doc_ref, doc_data)
                
                # Commit batch
                batch.commit()
                uploaded += len(batch_data)
                
                # Update progress
                self.root.after(0, lambda u=uploaded: self.progress.config(value=u))
                self.root.after(0, lambda u=uploaded, t=total_rows: 
                               self.status_label.config(text=f"Uploading... {u}/{t}"))
            
            # Success message
            self.root.after(0, lambda: self.status_label.config(
                text=f"Successfully completed! {total_rows} records uploaded."))
            self.root.after(0, lambda: messagebox.showinfo(
                "Success", f"{total_rows} records successfully uploaded to '{collection_path}'!"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.status_label.config(text=f"Error: {error_msg}"))
            self.root.after(0, lambda: messagebox.showerror("Upload Error", error_msg))
        
        finally:
            self.root.after(0, lambda: self.upload_button.config(state="normal"))
            self.root.after(0, lambda: self.progress.config(value=0))
    
    def clean_firestore_data(self, data):
        """Clean data types for Firestore"""
        cleaned = {}
        for key, value in data.items():
            if value is None or value == '':
                cleaned[key] = None
            elif value.lower() in ['true', 'false']:
                cleaned[key] = value.lower() == 'true'
            elif self.is_number(value):
                if '.' in value:
                    cleaned[key] = float(value)
                else:
                    cleaned[key] = int(value)
            else:
                cleaned[key] = str(value)
        return cleaned
    
    def is_number(self, s):
        """Check if string is a number"""
        try:
            float(s)
            return True
        except ValueError:
            return False

def main():
    root = tk.Tk()
    app = FireCSVUploader(root)
    
    # Close event
    def on_closing():
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
