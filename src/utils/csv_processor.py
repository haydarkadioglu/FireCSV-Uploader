"""
CSV processing and uploading utilities
"""
import csv
import os
import threading
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional
from firebase_admin import firestore


class CSVProcessor:
    """Handles CSV file processing and uploading to Firestore"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
    
    def read_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Read CSV file and return list of dictionaries
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of dictionaries representing CSV rows
        """
        with open(file_path, 'r', encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)
            return list(reader)
    
    def preview_csv(self, file_path: str, max_rows: int = 5) -> str:
        """
        Generate CSV preview text
        
        Args:
            file_path: Path to CSV file
            max_rows: Maximum number of rows to preview
            
        Returns:
            Preview text string
        """
        try:
            with open(file_path, 'r', encoding='utf-8-sig', newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)
                
                if not rows:
                    return "CSV file is empty!"
                
                headers = rows[0]
                total_rows = len(rows) - 1  # Excluding header
                
                preview = f"Total rows: {total_rows}\n"
                preview += f"Columns: {headers}\n\n"
                preview += f"First {min(max_rows, len(rows)-1)} rows:\n"
                
                # Header + first max_rows data rows
                for i, row in enumerate(rows[:max_rows+1]):
                    if i == 0:
                        preview += f"HEADER: {row}\n"
                    else:
                        preview += f"Row {i}: {row}\n"
                
                return preview
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clean_firestore_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean data types for Firestore compatibility
        
        Args:
            data: Raw data dictionary
            
        Returns:
            Cleaned data dictionary
        """
        cleaned = {}
        for key, value in data.items():
            if value is None or value == '':
                cleaned[key] = None
            elif str(value).lower() in ['true', 'false']:
                cleaned[key] = str(value).lower() == 'true'
            elif self._is_number(value):
                if '.' in str(value):
                    cleaned[key] = float(value)
                else:
                    cleaned[key] = int(value)
            else:
                cleaned[key] = str(value)
        return cleaned
    
    def _is_number(self, s: Any) -> bool:
        """Check if value is a number"""
        try:
            float(s)
            return True
        except (ValueError, TypeError):
            return False
    
    def upload_csv(self, 
                   file_path: str, 
                   collection_path: str, 
                   batch_size: int = 500,
                   progress_callback: Optional[Callable[[int, int], None]] = None,
                   status_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Upload CSV file to Firestore
        
        Args:
            file_path: Path to CSV file
            collection_path: Firestore collection path (can include sub-collections)
            batch_size: Number of documents to upload in each batch
            progress_callback: Callback for progress updates (current, total)
            status_callback: Callback for status updates
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            if status_callback:
                status_callback("Reading CSV file...")
            
            # Read CSV
            rows = self.read_csv(file_path)
            total_rows = len(rows)
            
            # Get collection reference
            collection_ref = self._get_collection_ref(collection_path)
            
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
                        'source_file': os.path.basename(file_path),
                        'collection_path': collection_path
                    }
                    
                    # Document ID (automatic)
                    doc_ref = collection_ref.document()
                    batch.set(doc_ref, doc_data)
                
                # Commit batch
                batch.commit()
                uploaded += len(batch_data)
                
                # Update progress
                if progress_callback:
                    progress_callback(uploaded, total_rows)
                if status_callback:
                    status_callback(f"Uploading... {uploaded}/{total_rows}")
            
            if status_callback:
                status_callback(f"Successfully completed! {total_rows} records uploaded.")
            
            return True
            
        except Exception as e:
            if status_callback:
                status_callback(f"Error: {str(e)}")
            return False
    
    def _get_collection_ref(self, collection_path: str):
        """Get collection reference based on path"""
        if "/" in collection_path:
            # Sub-collection
            parts = collection_path.split("/")
            main_collection = parts[0]
            sub_collection = parts[1]
            
            # Create a document in main collection and add sub-collection
            main_doc_ref = self.db.collection(main_collection).document(sub_collection)
            return main_doc_ref.collection("data")
        else:
            # Normal collection
            return self.db.collection(collection_path)
