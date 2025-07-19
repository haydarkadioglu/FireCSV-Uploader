"""
Firestore collection management utilities
"""
import csv
from typing import List, Dict, Any, Optional
from firebase_admin import firestore


class CollectionManager:
    """Manages Firestore collections operations"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
    
    def get_all_collections(self) -> List[Dict[str, Any]]:
        """
        Get all collections with their statistics
        
        Returns:
            List of collection information dictionaries
        """
        collections_info = []
        collections = self.db.collections()
        
        for collection in collections:
            collection_name = collection.id
            
            # Get document count and last modified
            docs = list(collection.limit(1000).stream())
            doc_count = len(docs)
            
            last_modified = "N/A"
            if docs:
                first_doc = docs[0]
                doc_data = first_doc.to_dict()
                if '_upload_info' in doc_data:
                    upload_info = doc_data['_upload_info']
                    if 'uploaded_at' in upload_info:
                        last_modified = upload_info['uploaded_at'].strftime("%Y-%m-%d %H:%M")
            
            collections_info.append({
                'name': collection_name,
                'type': 'Collection',
                'count': doc_count,
                'last_modified': last_modified,
                'path': collection_name
            })
            
            # Check for sub-collections
            for doc in collection.limit(10).stream():
                doc_collections = doc.reference.collections()
                for sub_collection in doc_collections:
                    sub_docs = list(sub_collection.limit(100).stream())
                    sub_count = len(sub_docs)
                    
                    sub_last_modified = "N/A"
                    if sub_docs:
                        first_sub_doc = sub_docs[0]
                        sub_doc_data = first_sub_doc.to_dict()
                        if '_upload_info' in sub_doc_data:
                            sub_upload_info = sub_doc_data['_upload_info']
                            if 'uploaded_at' in sub_upload_info:
                                sub_last_modified = sub_upload_info['uploaded_at'].strftime("%Y-%m-%d %H:%M")
                    
                    collections_info.append({
                        'name': f"{doc.id}/{sub_collection.id}",
                        'type': 'Sub-Collection',
                        'count': sub_count,
                        'last_modified': sub_last_modified,
                        'path': f"{collection_name}/{doc.id}/{sub_collection.id}",
                        'parent': collection_name
                    })
        
        return collections_info
    
    def get_collection_documents(self, collection_path: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get sample documents from a collection
        
        Args:
            collection_path: Path to collection
            limit: Maximum number of documents to retrieve
            
        Returns:
            List of document dictionaries
        """
        collection_ref = self._get_collection_ref(collection_path)
        docs = list(collection_ref.limit(limit).stream())
        
        documents = []
        for doc in docs:
            documents.append({
                'id': doc.id,
                'data': doc.to_dict()
            })
        
        return documents
    
    def export_collection_to_csv(self, collection_path: str, output_file: str) -> bool:
        """
        Export collection to CSV file
        
        Args:
            collection_path: Path to collection
            output_file: Output CSV file path
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            collection_ref = self._get_collection_ref(collection_path)
            docs = list(collection_ref.stream())
            
            if not docs:
                return False
            
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
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=all_fields)
                writer.writeheader()
                
                for doc_data in doc_data_list:
                    # Remove metadata and write row
                    doc_data.pop('_upload_info', None)
                    writer.writerow(doc_data)
            
            return True
            
        except Exception as e:
            print(f"Export error: {str(e)}")
            return False
    
    def delete_collection(self, collection_path: str) -> bool:
        """
        Delete all documents in a collection
        
        Args:
            collection_path: Path to collection
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            collection_ref = self._get_collection_ref(collection_path)
            
            # Delete all documents in batches
            deleted_count = 0
            while True:
                docs = list(collection_ref.limit(500).stream())
                if not docs:
                    break
                
                batch = self.db.batch()
                for doc in docs:
                    batch.delete(doc.reference)
                    deleted_count += 1
                batch.commit()
            
            return True
            
        except Exception as e:
            print(f"Delete error: {str(e)}")
            return False
    
    def _get_collection_ref(self, collection_path: str):
        """Get collection reference based on path"""
        if "/" in collection_path and collection_path.count("/") >= 2:
            # Sub-collection path: main_collection/doc_id/sub_collection
            parts = collection_path.split("/")
            main_collection = parts[0]
            doc_id = parts[1]
            sub_collection = parts[2]
            
            return self.db.collection(main_collection).document(doc_id).collection(sub_collection)
        else:
            # Main collection
            return self.db.collection(collection_path)
