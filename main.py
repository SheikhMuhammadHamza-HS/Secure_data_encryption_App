import streamlit as st 
import hashlib
from cryptography.fernet import Fernet
import json
import os 
import time
from base64 import urlsafe_b64encode
from hashlib import pbkdf2_hmac

# Constants
DATA_FILE = "secured_data.txt"
SALT = b"secure_salt_value"
LOCKOUT_DURATION = 60

# Session state initialization
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0
if "lockout_time" not in st.session_state:
    st.session_state.lockout_time = 0

# Custom CSS for professional look
st.markdown("""
    <style>
        .main {
            max-width: 800px;
            padding: 2rem;
        }
        .title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1.5rem;
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            border: none;
            font-weight: 500;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .stTextInput>div>div>input {
            border-radius: 4px;
            padding: 0.5rem;
        }
        .stTextArea>div>div>textarea {
            border-radius: 4px;
            padding: 0.5rem;
        }
        .error {
            color: #e74c3c;
            font-weight: 500;
        }
        .success {
            color: #2ecc71;
            font-weight: 500;
        }
        .warning {
            color: #f39c12;
            font-weight: 500;
        }
        .info-box {
            background-color: #e8f4fc;
            border-left: 4px solid #3498db;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 4px 4px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Utility functions
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def generate_key(passkey):
    key = pbkdf2_hmac("sha256", passkey.encode(), SALT, 100000)
    return urlsafe_b64encode(key)

def hash_password(password):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), SALT, 100000).hex()

def encrypt_text(text, key):
    cipher = Fernet(generate_key(key))
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text, key):
    try:    
        cipher = Fernet(generate_key(key))
        return cipher.decrypt(encrypted_text.encode()).decode()
    except:
        return None

# Load data
stored_data = load_data()

# Sidebar Navigation
st.sidebar.title("🔒 SecureVault")
menu = ["Home", "Register", "Login", "Store Data", "Retrieve Data"]
choice = st.sidebar.radio("Navigation", menu)

if choice == "Home":
    st.markdown('<div class="title">Secure Data Encryption System</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>Welcome to SecureVault</h3>
        <p>A secure data storage and retrieval system that protects your sensitive information with military-grade encryption.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Key Features:
        - 🔐 AES-256 encryption
        - 👤 User authentication
        - ⏳ Brute-force protection
        - 📁 Local storage only
        """)
    
    with col2:
        st.markdown("""
        ### How It Works:
        1. Register an account
        2. Login securely
        3. Store encrypted data
        4. Retrieve with your passkey
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">
        <p>Developed with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

elif choice == "Register":
    st.markdown('<div class="title">Create New Account</div>', unsafe_allow_html=True)
    
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a unique username")
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
        
        submitted = st.form_submit_button("Register")
        if submitted:
            if not username or not password or not confirm_password:
                st.error("All fields are required")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif username in stored_data:
                st.error("Username already exists")
            else:
                stored_data[username] = {
                    "password": hash_password(password),
                    "data": []
                }
                save_data(stored_data)
                st.success("Account created successfully! Please login to continue.")
                st.balloons()

elif choice == "Login":
    st.markdown('<div class="title">Secure Login</div>', unsafe_allow_html=True)
    
    if time.time() < st.session_state.lockout_time:
        remaining_time = int(st.session_state.lockout_time - time.time())
        st.error(f"Account temporarily locked. Please try again in {remaining_time} seconds.")
        st.stop()
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        submitted = st.form_submit_button("Login")
        if submitted:
            if username in stored_data and stored_data[username]["password"] == hash_password(password):
                st.session_state.authenticated_user = username
                st.session_state.failed_attempts = 0
                st.success("Login successful!")
                time.sleep(1)
                st.rerun()  # This is the corrected line
            else:
                st.session_state.failed_attempts += 1
                remaining_attempts = 3 - st.session_state.failed_attempts
                
                if remaining_attempts > 0:
                    st.error(f"Invalid credentials. {remaining_attempts} attempts remaining.")
                else:
                    st.session_state.lockout_time = time.time() + LOCKOUT_DURATION
                    st.error("Too many failed attempts. Account locked for 60 seconds.")
                    st.stop()

elif choice == "Store Data":
    if not st.session_state.authenticated_user:
        st.warning("Please login first to access this page")
    else:
        st.markdown('<div class="title">Store Encrypted Data</div>', unsafe_allow_html=True)
        
        with st.form("store_form"):
            data_name = st.text_input("Data Name", placeholder="Give this data a name (optional)")
            data_content = st.text_area("Data Content", placeholder="Enter the sensitive data you want to encrypt", height=150)
            passkey = st.text_input("Encryption Passphrase", type="password", placeholder="Create a strong passphrase (remember this!)")
            
            submitted = st.form_submit_button("Encrypt & Store")
            if submitted:
                if not data_content or not passkey:
                    st.error("Data content and passphrase are required")
                else:
                    encrypted = encrypt_text(data_content, passkey)
                    if not stored_data[st.session_state.authenticated_user]["data"]:
                        stored_data[st.session_state.authenticated_user]["data"] = []
                    
                    entry = {
                        "name": data_name if data_name else f"Entry {len(stored_data[st.session_state.authenticated_user]['data']) + 1}",
                        "content": encrypted,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    stored_data[st.session_state.authenticated_user]["data"].append(entry)
                    save_data(stored_data)
                    st.success("Data encrypted and stored successfully!")
                    st.info("❗ Remember your passphrase - it cannot be recovered if lost")

elif choice == "Retrieve Data":
    if not st.session_state.authenticated_user:
        st.warning("Please login first to access this page")
    else:
        st.markdown('<div class="title">Retrieve Encrypted Data</div>', unsafe_allow_html=True)
        
        user_entries = stored_data.get(st.session_state.authenticated_user, {}).get("data", [])
        
        if not user_entries:
            st.info("No encrypted data found")
        else:
            entry_names = [f"{entry['name']} ({entry['timestamp']})" for entry in user_entries]
            selected_entry = st.selectbox("Select data to decrypt", entry_names)
            
            selected_index = entry_names.index(selected_entry)
            selected_data = user_entries[selected_index]["content"]
            
            with st.form("retrieve_form"):
                passkey = st.text_input("Decryption Passphrase", type="password", placeholder="Enter the passphrase used to encrypt this data")
                
                submitted = st.form_submit_button("Decrypt Data")
                if submitted:
                    decrypted = decrypt_text(selected_data, passkey)
                    if decrypted:
                        st.success("Decryption successful!")
                        st.text_area("Decrypted Content", value=decrypted, height=200)
                    else:
                        st.error("Incorrect passphrase or corrupted data")