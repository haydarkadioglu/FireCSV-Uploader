"""
Firebase connection and management utilities
"""
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional


class FirebaseManager:
    """Manages Firebase connection and operations"""
    
    def __init__(self):
        self.db: Optional[firestore.Client] = None
        self.cred_path: Optional[str] = None
    
    def connect(self, credential_path: str) -> bool:
        """
        Connect to Firebase using service account credentials
        
        Args:
            credential_path: Path to service account JSON file
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Clear previous connection
            if firebase_admin._apps:
                firebase_admin.delete_app(firebase_admin.get_app())
            
            # New connection
            cred = credentials.Certificate(credential_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.cred_path = credential_path
            
            return True
            
        except Exception as e:
            print(f"Firebase connection error: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """Check if Firebase is connected"""
        return self.db is not None
    
    def get_client(self) -> Optional[firestore.Client]:
        """Get Firestore client"""
        return self.db
    
    def disconnect(self):
        """Disconnect from Firebase"""
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
        self.db = None
        self.cred_path = None
