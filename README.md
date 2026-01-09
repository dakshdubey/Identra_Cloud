# Identra Cloud 

**Advanced Biometric Cloud Storage System**
*Next-Gen Security for the Modern Web*

![Identra Cloud Banner](https://via.placeholder.com/1200x400?text=Identra+Cloud+Security+2026) 
*(Note: Replace with actual screenshot)*

##  Overview

**Identra Cloud** is a production-grade, secure cloud storage platform integrated with **EvoBioMat** biometric authentication. Built for the privacy-conscious era of 2026, it combines "Aeroglass" neomorphic aesthetics with military-grade security.

Unlike traditional cloud storage, Identra Cloud requires **facial biometric verification** for access, ensuring that your data remains yours, even if your password is compromised.

##  Key Features

###  **Biometric Security Core**
- **Face ID Login**: Seamless, password-less entry using `evoBioMat` SDK.
- **Liveness Detection**: Prevents spoofing attacks using advanced neural analysis.
- **Secure Session Guard**: Automatic session termination and re-verification for sensitive actions.

###  **Advanced File Management**
- **Masonry Grid Layout**: A beautiful, fluid "Google Photos" style gallery for your files.
- **Smart Search**: Real-time filtering by name, type, or date.
- **Instant Preview**: View images, watch videos, and read PDFs directly in the browser without downloading.
- **Drag & Drop Zone**: Intuitive upload interface with immersive animations.

###  **Industry-Level Features**
- **Activity Audit Log**: Complete history of every login, upload, and deletion event.
- **Secure Sharing**: Generate expirable, tokenized links for external sharing (Simulation).
- **Real-Time Analytics**: Visual storage quota usage and file categorization.
- **Encrypted Storage**: Files are renamed and tracked via secure database mapping, not raw filenames.

##  Technology Stack

- **Backend**: Python 3.10+, Flask 2.0+
- **Database**: MySQL 8.0 (Structured relational data)
- **Biometrics**: [EvoBioMat](https://pypi.org/project/evoBioMat/) SDK
- **Frontend**: HTML5, Vanilla JavaScript (ES6+), AeroGlass CSS (Custom Design System)
- **Icons**: FontAwesome 6 Pro

##  Installation & Setup

### Prerequisites
- Python 3.10 or higher
- MySQL Server installed and running
- Webcam (for biometric auth)

### 1. Clone & Install
```bash
git clone https://github.com/dakshdubey/identra-cloud.git
cd Identra
pip install -r requirements.txt
```

### 2. Database Setup
Create the database and tables using the provided schema.
```sql
CREATE DATABASE evobiomat_test;
USE evobiomat_test;
-- Run contents of schema.sql
```
*Tip: You can use `mysql -u root -p < schema.sql`*

### 3. Configuration
Update `app.py` or use environment variables for your DB credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_PASSWORD',
    'database': 'evobiomat_test'
}
```

### 4. Run the Server
```bash
python app.py
```
Visit **http://localhost:5000** in your browser.

## 📖 Usage Guide

1.  **Registration**: Click "Get Started". The system will scan your face to create a unique biometric profile.
2.  **Login**: Use "Verify Identity". Look at the camera. Upon success, you are granted access.
3.  **Dashboard**:
    *   **Upload**: Drag files anywhere or click "Upload".
    *   **Preview**: Click any file card to view it.
    *   **Delete**: Click the trash icon to remove files (Deleting is permanent!).
    *   **Audit**: Click the clock icon in the search bar to view your security logs.

## 📄 License
© 2026 Identra Security Systems. All Rights Reserved.
Powered by **EvoBioMat**.

---
*Built with ❤️ by the Daksha Dubey.*
