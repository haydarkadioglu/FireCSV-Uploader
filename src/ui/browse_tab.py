"""
Browse Collections tab UI components
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import threading
from typing import Optional


class BrowseTab:
    """Browse Collections tab UI and functionality"""
    
    def __init__(self, parent, firebase_manager, collection_manager):
        self.parent = parent
        self.firebase_manager = firebase_manager
        self.collection_manager = collection_manager
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the browse tab UI"""
        # Refresh button
        refresh_frame = ttk.Frame(self.parent)
        refresh_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(refresh_frame, text="Refresh Collections", 
                  command=self.refresh_collections).grid(row=0, column=0, padx=(0, 10))
        
        self.collection_count_label = ttk.Label(refresh_frame, text="")
        self.collection_count_label.grid(row=0, column=1, padx=(10, 0))
        
        # Collections tree
        collections_frame = ttk.LabelFrame(self.parent, text="Collections & Documents", padding="10")
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
        
        # Status label
        self.status_label_browse = ttk.Label(collections_frame, text="Ready - Click 'Refresh Collections' to load data")
        self.status_label_browse.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        # Grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=1)
        collections_frame.columnconfigure(0, weight=1)
        collections_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def refresh_collections(self):
        """Refresh collections list"""
        if not self.firebase_manager.is_connected():
            messagebox.showerror("Error", "Please connect to Firebase first!")
            return
        
        self.status_label_browse.config(text="Loading collections...")
        thread = threading.Thread(target=self._load_collections)
        thread.daemon = True
        thread.start()
    
    def _load_collections(self):
        """Load collections from Firestore"""
        try:
            self.collection_manager.db = self.firebase_manager.get_client()
            
            # Clear existing items
            for item in self.collections_tree.get_children():
                self.collections_tree.delete(item)
            
            # Get collections info
            collections_info = self.collection_manager.get_all_collections()
            
            # Group by main collections
            main_collections = {}
            sub_collections = {}
            
            for info in collections_info:
                if info['type'] == 'Collection':
                    main_collections[info['name']] = info
                else:
                    parent = info.get('parent', '')
                    if parent not in sub_collections:
                        sub_collections[parent] = []
                    sub_collections[parent].append(info)
            
            # Add to tree
            for collection_name, collection_info in main_collections.items():
                collection_item = self.collections_tree.insert(
                    "", "end", 
                    text=collection_name,
                    values=(collection_info['type'], collection_info['count'], collection_info['last_modified'])
                )
                
                # Add sub-collections
                if collection_name in sub_collections:
                    for sub_info in sub_collections[collection_name]:
                        self.collections_tree.insert(
                            collection_item, "end",
                            text=sub_info['name'],
                            values=(sub_info['type'], sub_info['count'], sub_info['last_modified'])
                        )
            
            self.collection_count_label.config(text=f"Found {len(main_collections)} collections")
            self.status_label_browse.config(text="Collections loaded successfully.")
            
        except Exception as e:
            error_msg = str(e)
            self.status_label_browse.config(text=f"Error: {error_msg}")
            messagebox.showerror("Loading Error", error_msg)
    
    def view_collection_details(self):
        """View details of selected collection"""
        selection = self.collections_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a collection first!")
            return
        
        item = selection[0]
        collection_name = self.collections_tree.item(item)['text']
        
        try:
            # Create details window
            details_window = tk.Toplevel(self.parent)
            details_window.title(f"Collection Details: {collection_name}")
            details_window.geometry("600x400")
            
            # Collection info
            info_frame = ttk.LabelFrame(details_window, text="Collection Information", padding="10")
            info_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(info_frame, text=f"Name: {collection_name}").pack(anchor="w")
            
            # Sample documents
            docs_frame = ttk.LabelFrame(details_window, text="Sample Documents", padding="10")
            docs_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            docs_text = scrolledtext.ScrolledText(docs_frame, height=15, width=70)
            docs_text.pack(fill="both", expand=True)
            
            # Load documents in thread
            def load_documents():
                try:
                    self.collection_manager.db = self.firebase_manager.get_client()
                    documents = self.collection_manager.get_collection_documents(collection_name, 5)
                    
                    if documents:
                        docs_text.insert(tk.END, f"Showing first {len(documents)} documents:\n\n")
                        for i, doc in enumerate(documents, 1):
                            docs_text.insert(tk.END, f"Document {i} (ID: {doc['id']}):\n")
                            docs_text.insert(tk.END, json.dumps(doc['data'], indent=2, default=str))
                            docs_text.insert(tk.END, "\n" + "="*50 + "\n\n")
                    else:
                        docs_text.insert(tk.END, "No documents found in this collection.")
                        
                except Exception as e:
                    docs_text.insert(tk.END, f"Error loading documents: {str(e)}")
                
                docs_text.config(state=tk.DISABLED)
            
            thread = threading.Thread(target=load_documents)
            thread.daemon = True
            thread.start()
                
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
        
        self.status_label_browse.config(text="Exporting...")
        thread = threading.Thread(target=self._export_collection, args=(collection_name, file_path))
        thread.daemon = True
        thread.start()
    
    def _export_collection(self, collection_name: str, file_path: str):
        """Export collection to CSV file"""
        try:
            self.collection_manager.db = self.firebase_manager.get_client()
            
            success = self.collection_manager.export_collection_to_csv(collection_name, file_path)
            
            if success:
                self.status_label_browse.config(text="Export completed successfully.")
                messagebox.showinfo("Success", f"Collection exported to {file_path}")
            else:
                self.status_label_browse.config(text="Export failed - no documents found.")
                messagebox.showinfo("Info", "No documents found in this collection.")
            
        except Exception as e:
            error_msg = str(e)
            self.status_label_browse.config(text=f"Export error: {error_msg}")
            messagebox.showerror("Export Error", error_msg)
    
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
        
        self.status_label_browse.config(text="Deleting...")
        thread = threading.Thread(target=self._delete_collection, args=(collection_name,))
        thread.daemon = True
        thread.start()
    
    def _delete_collection(self, collection_name: str):
        """Delete collection from Firestore"""
        try:
            self.collection_manager.db = self.firebase_manager.get_client()
            
            success = self.collection_manager.delete_collection(collection_name)
            
            if success:
                self.status_label_browse.config(text="Collection deleted successfully.")
                messagebox.showinfo("Success", f"Collection '{collection_name}' deleted successfully!")
                # Refresh the collection list
                self.refresh_collections()
            else:
                self.status_label_browse.config(text="Delete failed.")
                messagebox.showerror("Error", "Failed to delete collection")
            
        except Exception as e:
            error_msg = str(e)
            self.status_label_browse.config(text=f"Delete error: {error_msg}")
            messagebox.showerror("Delete Error", error_msg)
