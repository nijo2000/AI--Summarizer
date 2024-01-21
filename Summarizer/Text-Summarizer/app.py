import streamlit as st
import sqlite3
import hashlib
from helper import get_summary, spacy_rander
import PyPDF2
import io


# Database setup and functions
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

def create_users_table():
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT UNIQUE, password TEXT)')

def add_userdata(username, password):
    c.execute('INSERT INTO users(username, password) VALUES (?, ?)', (username, password))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data

# Create a users table
create_users_table()

# Layout of Login and Registration
st.sidebar.title("Login/Registration")

menu = ["Home", "Login", "SignUp"]
choice = st.sidebar.selectbox("Menu", menu)

# User Authentication
current_user = None

if choice == "Login":
    st.subheader("Login Section")

    username = st.sidebar.text_input("User Name")
    password = st.sidebar.text_input("Password", type='password')
    if st.sidebar.checkbox("Login"):
        # Password Hashing
        hashed_pswd = hashlib.sha256(password.encode('utf-8')).hexdigest()
        result = login_user(username, hashed_pswd)
        if result:
            current_user = username
            st.success(f"Logged In as {username}")

elif choice == "SignUp":
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')

    if st.button("Signup"):
        # Password Hashing
        hashed_new_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
        try:
            add_userdata(new_user, hashed_new_password)
            st.success("You have successfully created an account")
            st.info("Go to the Login Menu to login")
        except:
            st.error("Username already exists")

# Text Summarizer Functionality
if current_user:
    st.title(f"Welcome to Document Summarizer, {current_user}")

    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("Upload a file", type=["txt", "pdf"])
        text = ""
        if uploaded_file is not None:
            if uploaded_file.type == "text/plain":
                text = str(uploaded_file.read(), "utf-8")
            elif uploaded_file.type == "application/pdf":
                try:
                    with io.BytesIO(uploaded_file.read()) as open_pdf_file:
                        read_pdf = PyPDF2.PdfReader(open_pdf_file)
                        text = ''
                        for page in range(len(read_pdf.pages)):
                            text += read_pdf.pages[page].extract_text()
                except Exception as e:
                    st.error(f"Error in reading PDF file: {e}")
                    text = ''

        text = st.text_area("Enter Your Text or story", text, height=350, placeholder="Enter Your Text or story or your article; it can be of any length")
        
    if st.button("Get Summary"):
        summary = get_summary(text)

        try:
            with col2:
                st.write(f"Text Summary (Summary length: {len(summary)})",height=500)
                st.code(summary)

            spacy_rander(summary)

            # Uncomment the following line if you want to render analysis of the original text
            # spacy_rander(text, text="Yes")
            
        except NameError as e:
            st.error(f"An error occurred: {e}")
