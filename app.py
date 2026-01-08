import os
import sys
import datetime
import cryptography.fernet
import mysql.connector
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename

try:
    from evobiomat import EvoBioMat
    from evobiomat.errors.exceptions import EvoBioMatError
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import 'evobiomat'. {e}")
    print("Please ensure the SDK is installed: pip install evoBioMat")
    sys.exit(1)

# Configuration
UPLOAD_FOLDER = 'user_storage'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'docx', 'zip'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB limit

# Hardcoded Credentials for Demo
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "evobiomat_test"
}
ENCRYPTION_KEY = b"12345678901234567890123456789012" 

app = Flask(__name__, static_folder='static') # Default
# We will serve user files via a special route for security checks later, 
# but for now let's serve them using send_from_directory logic.
from flask import send_from_directory

app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
CORS(app)

# Ensure storage root exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Global SDK instance
try:
    print(">> [BOOT] Initializing EvoBioMat SDK...")
    sdk = EvoBioMat(DB_CONFIG, ENCRYPTION_KEY)
    print(">> [BOOT] System Ready.")
except Exception as e:
    print(f">> [BOOT ERROR] SDK Initialization failed: {e}")
    sdk = None

# --- HELPERS ---

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def log_activity(user_id, action, details=""):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (%s, %s, %s)", 
                       (user_id, action, details))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Log Error: {e}")

def get_user_storage_path(user_id):
    path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(user_id))
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_file_icon(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext in ['jpg', 'jpeg', 'png', 'gif']:
        return "fa-solid fa-image", "#3b82f6" # Blue
    elif ext in ['pdf']:
        return "fa-solid fa-file-pdf", "#ef4444" # Red
    elif ext in ['doc', 'docx', 'txt']:
        return "fa-solid fa-file-word", "#2563eb" # Dark Blue
    elif ext in ['mp4', 'mov', 'avi']:
        return "fa-solid fa-clapperboard", "#8b5cf6" # Purple
    elif ext in ['zip', 'rar', '7z']:
        return "fa-solid fa-file-zipper", "#f59e0b" # Orange
    else:
        return "fa-solid fa-file", "#94a3b8" # Gray

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

# --- ROUTES ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/files/<user_id>/<filename>')
def serve_file(user_id, filename):
    # Security: Ensure user can only access their own files?
    # For now, if you have the session key or just the link.
    # In a real app we'd check session['user_id'] == user_id.
    if session.get('user_id') != user_id:
         return "Unauthorized", 403
         
    return send_from_directory(get_user_storage_path(user_id), filename)

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index'))
    
    files = []
    stats = {
        "total_size": 0,
        "total_size_str": "0 B",
        "total_size_percentage": 0,
        "images": 0,
        "videos": 0,
        "documents": 0,
        "secrets": 0
    }
    
    # DB File Listing & Stats Calculation
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_files WHERE user_id = %s ORDER BY upload_date DESC", (user_id,))
        records = cursor.fetchall()
        
        for r in records:
            # Metadata
            filename = r['filename']
            file_path = r['local_path']
            
            # Real Size Calculation
            size_bytes = 0
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
            
            stats['total_size'] += size_bytes
            
            # Category Counting
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            if ext in ['jpg', 'jpeg', 'png', 'gif']:
                stats['images'] += 1
            elif ext in ['mp4', 'mov', 'avi']:
                stats['videos'] += 1
            elif ext in ['doc', 'docx', 'pdf', 'txt']:
                stats['documents'] += 1
            elif ext in ['enc', 'zip', 'rar']: # Treat encrypted/archives as secrets for now
                stats['secrets'] += 1
            
            # Dashboard List Item
            icon, color = get_file_icon(filename)
            files.append({
                "name": filename,
                "size": r['size'], # Keep the formatted string from DB for list
                "date": r['upload_date'].strftime('%Y-%m-%d %H:%M'),
                "icon": icon,
                "color": color,
                "url": url_for('serve_file', user_id=user_id, filename=filename) 
            })
        
        cursor.close()
        conn.close()
        
        # Format Total Size
        stats['total_size_str'] = format_size(stats['total_size'])
        # 100GB limit
        percentage = (stats['total_size'] / (100 * 1024 * 1024 * 1024)) * 100
        stats['total_size_percentage'] = min(percentage, 100)
        if stats['total_size'] > 0 and stats['total_size_percentage'] < 1:
             stats['total_size_percentage'] = 1 # Show at least a sliver
        
    except Exception as e:
        print(f"Error reading DB: {e}")

    return render_template('dashboard.html', files=files, stats=stats)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
        
    if file:
        try:
            filename = secure_filename(file.filename)
            save_path = os.path.join(get_user_storage_path(user_id), filename)
            file.save(save_path)
            
            # Get Size
            file_size = format_size(os.path.getsize(save_path))

            # Store in DB
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user_files (user_id, filename, size, local_path) VALUES (%s, %s, %s, %s)", 
                           (user_id, filename, file_size, save_path))
            conn.commit()
            cursor.close()
            conn.close()

            # Log Activity
            log_activity(user_id, "UPLOAD", f"Uploaded {filename}")

            return jsonify({"status": "success", "message": "File uploaded successfully"})
        except Exception as e:
            print(f"Upload Error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "error", "message": "Upload failed"}), 500

@app.route('/api/activity', methods=['GET'])
def get_activity_log():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    logs = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Limit to last 50 events
        cursor.execute("SELECT * FROM activity_logs WHERE user_id = %s ORDER BY timestamp DESC LIMIT 50", (user_id,))
        records = cursor.fetchall()
        
        for r in records:
            logs.append({
                "action": r['action'],
                "details": r['details'],
                "date": r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            })
            
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "logs": logs})
    except Exception as e:
        print(f"Activity Log Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Get all paths for this filename (handle potential duplicates)
        cursor.execute("SELECT local_path FROM user_files WHERE user_id = %s AND filename = %s", (user_id, filename))
        results = cursor.fetchall() # buffered read of all rows
        
        if not results:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "File not found"}), 404
            
        # 2. Remove from Filesystem
        for row in results:
            local_path = row[0]
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except Exception as del_err:
                    print(f"FS Delete Error: {del_err}")
        
        # 3. Remove from DB (All entries with this name for this user)
        cursor.execute("DELETE FROM user_files WHERE user_id = %s AND filename = %s", (user_id, filename))
        conn.commit()
        
        cursor.close()
        conn.close()

        # Log
        log_activity(user_id, "DELETE", f"Deleted {filename}")
        
        return jsonify({"status": "success", "message": "File deleted"})
            
    except Exception as e:
        print(f"Delete Error: {e}")
        return jsonify({"status": "error", "message": f"Deletion failed: {str(e)}"}), 500

# --- API ENDPOINTS (EXISTING) ---

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "ready" if sdk else "error",
        "message": "System is initialized." if sdk else "Initialization failed. Check server logs."
    })

@app.route('/api/register-auto', methods=['POST'])
def register_auto():
    """Register user using evoBioMat SDK's native capture"""
    if not sdk:
        return jsonify({"status": "error", "message": "SDK not initialized."}), 400
    
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"status": "error", "message": "User ID is required."}), 400
    
    try:
        print(f">> [REGISTER] Starting enrollment for user: {user_id}")
        success = sdk.register(user_id)
        
        if success:
            print(f">> [REGISTER] Success for user: {user_id}")
            # Ensure folder exists
            get_user_storage_path(user_id)
            return jsonify({
                "status": "success", 
                "message": f"User '{user_id}' registered successfully. Please login."
            })
        else:
            print(f">> [REGISTER] Failed for user: {user_id}")
            return jsonify({"status": "error", "message": "Registration failed. Face not detected or cancelled."}), 500
            
    except Exception as e:
        print(f">> [REGISTER] Error: {str(e)}")
        return jsonify({"status": "error", "message": f"Registration error: {str(e)}"}), 500

@app.route('/api/verify-auto', methods=['POST'])
def verify_auto():
    """Verify user using evoBioMat SDK's native capture"""
    if not sdk:
        return jsonify({"status": "error", "message": "SDK not initialized."}), 400
    
    try:
        print(f">> [VERIFY] Starting verification...")
        result = sdk.verify()
        
        print(f">> [VERIFY] Result: {result.is_verified}, User: {result.user_id}")
        
        if result.is_verified:
            # Set Session
            session['user_id'] = result.user_id
            
            # Log Activity
            log_activity(result.user_id, "LOGIN", "Biometric verification success")
            
            return jsonify({
                "status": "success",
                "is_verified": True,
                "user_id": result.user_id,
                "message": "Access Granted"
            })
        else:
            return jsonify({
                "status": "failed",
                "is_verified": False,
                "message": "Biometric mismatch or user not found."
            })
        
    except Exception as e:
        print(f">> [VERIFY] Error: {str(e)}")
        return jsonify({"status": "error", "message": f"Verification error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
