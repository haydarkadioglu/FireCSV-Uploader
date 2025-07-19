# FireCSV Uploader

Python GUI application for uploading CSV files to Firebase Firestore with advanced collection management features.

## 🎯 Features

- 🔥 **Firebase Firestore integration**
- 📊 **CSV file preview**
- 🚀 **Batch uploading** (for performance)
- 📊 **Progress bar**
- 🎯 **User-friendly interface**
- ⚡ **Multi-threading support**
- 🔧 **Automatic data type conversion**
- 📁 **Sub-collection support** (organize your data hierarchically)
- 🌟 **Tabbed interface** (Upload & Browse)
- 🗂️ **Collection browser** (view, export, delete collections)
- 📈 **Collection statistics** (document count, last modified)
- 🔍 **Document viewer** (inspect collection contents)
- 💾 **Export to CSV** (download collections back to CSV)
- 🗑️ **Collection deletion** (with confirmation)

## 🛠️ Installation

1. Install required packages:
```bash
pip install firebase-admin
```

2. Prepare your Firebase Service Account Key file:
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Project Settings > Service Accounts
   - Click "Generate new private key" button
   - Download the JSON file

## 🚀 Usage

1. Start the application:
```bash
# New modular version (recommended)
python main_v2.py

# Legacy version (deprecated)
python main.py
```

### Upload CSV Tab

2. **Configure Firebase settings:**
   - Select your Service Account JSON file
   - Click "Connect to Firebase" button

3. **Select CSV file and configure settings:**
   - Select your CSV file
   - Enter collection name
   - Configure sub-collection (optional):
     - **Manual entry**: Type sub-collection name manually
     - **From CSV filename**: Use CSV filename as sub-collection name
     - **Add date**: Append current date to sub-collection name
   - Set batch size (default: 500)

4. **Click "Upload CSV to Firestore"** button

### Browse Collections Tab

5. **Manage your Firestore data:**
   - Click "Refresh Collections" to load all collections
   - View collection statistics (type, document count, last modified)
   - **View Details**: Inspect sample documents in a collection
   - **Export to CSV**: Download collection data as CSV file
   - **Delete Collection**: Remove entire collections (with confirmation)

## 📁 CSV Format Requirements

- **UTF-8 encoding** required
- **First row** must contain column headers
- Supported data types:
  - String (text)
  - Number (int/float)
  - Boolean (true/false)
  - Null (empty values)

## 📊 Data Type Conversion

The application automatically performs these conversions:
- `"true"`, `"false"` → Boolean
- Numbers → Integer or Float
- Empty values → `null`
- Everything else → String

## 🗂️ Sub-Collection Support

Organize your data hierarchically:
- **Main Collection**: `employees`
- **Sub-Collection**: `employees/2024_Q1/data`
- **Document Structure**: Each CSV row becomes a document in the sub-collection

Sub-collection modes:
- **Manual**: Type custom sub-collection name
- **From filename**: Use CSV filename as sub-collection name
- **Add date**: Append current date (YYYYMMDD) for time-based organization

## ⚙️ Settings

- **Batch Size:** Number of records to upload at once (1-500)
- **Collection Name:** Name of the Firestore collection to create
- **Sub-Collection:** Optional hierarchical organization

## 🎮 Testing

Create sample CSV files:
```bash
# English sample (recommended)
python create_sample_employees_en.py

# Turkish sample (legacy)
python create_sample_csv.py
```

The English sample (`sample_employees.csv`) includes comprehensive employee data with 19 columns and 50 records.

## 🔧 Important Notes

- **Batch uploading** is used for large files
- New documents are **added to existing collections** (doesn't overwrite)
- Each CSV row becomes a separate **Firestore document**
- Empty values are saved as **null**
- Application is **thread-safe**
- **Metadata tracking**: Each document includes upload information
- **Hierarchical structure**: Sub-collections provide better organization

## 🌟 Advanced Features

### Collection Management
- **Real-time statistics**: See document counts and modification dates
- **Hierarchical view**: Navigate main collections and sub-collections
- **Document inspection**: View sample documents with formatted JSON
- **Bulk operations**: Export or delete entire collections

### Performance Optimizations
- **Batch commits**: Efficient bulk uploads
- **Background processing**: Non-blocking UI during operations
- **Progress tracking**: Real-time upload progress
- **Memory efficient**: Streaming for large files

## 🐛 Troubleshooting

### Firebase Connection Error
- Ensure the Service Account JSON file is correct
- Check that your Firebase project is active
- Verify Firestore is enabled in your project

### CSV Reading Error
- Ensure the file is UTF-8 encoded
- Check CSV format is correct
- Verify column headers are present

### Upload Error
- Check your Firestore security rules
- Verify your internet connection
- Ensure you have write permissions

### Collection Browser Issues
- Click "Refresh Collections" to reload data
- Check Firebase connection status
- Verify you have read permissions

## 📝 Supported File Formats

- `.csv` (Comma Separated Values)
- UTF-8, UTF-8-BOM encoding

## 🛡️ Security

- Firebase credentials files are included in `.gitignore`
- Stored securely locally
- Network traffic encrypted with HTTPS
- No credentials stored in application code

## 📦 Project Structure

```
FireCSV-Uploader/
├── main.py                      # Legacy monolithic version (deprecated)
├── main_v2.py                   # New modular main application
├── src/                         # Source code modules
│   ├── __init__.py
│   ├── firebase/                # Firebase management
│   │   ├── __init__.py
│   │   ├── firebase_manager.py  # Firebase connection manager
│   │   └── collection_manager.py # Collection operations
│   ├── ui/                      # User interface components
│   │   ├── __init__.py
│   │   ├── upload_tab.py        # Upload CSV tab
│   │   └── browse_tab.py        # Browse collections tab
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       └── csv_processor.py     # CSV processing utilities
├── create_sample_employees_en.py # English sample generator
├── create_sample_csv.py         # Turkish sample generator (legacy)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .gitignore                   # Git exclusions
├── sample_employees.csv         # Generated English sample
└── ornek_calisanlar.csv        # Generated Turkish sample (legacy)
```

## 🔄 Updates & Features

### Version 2.0 Features:
- ✅ **Modular Architecture**: Clean separation of concerns
- ✅ **Tabbed interface** (Upload & Browse)
- ✅ **Collection management**
- ✅ **Sub-collection support**
- ✅ **English localization**
- ✅ **Enhanced data organization**
- ✅ **Export functionality**
- ✅ **Document viewer**
- ✅ **Better error handling**
- ✅ **Thread-safe operations**

### Architecture Improvements:
- **firebase/**: Firebase connection and collection management
- **ui/**: Separated UI components for better maintainability
- **utils/**: Reusable utility functions
- **Clean imports**: Better dependency management

## 📄 License

This project is licensed under the MIT License.
