import sys
import os
import subprocess
import sqlite3
import json
from google import genai
from google.genai import types

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QLabel, QScrollArea, QListWidget
)
from PyQt6.QtCore import Qt, QMimeData, QUrl
from PyQt6.QtGui import QDrag

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

DB_FILE = "file_index.db"
SKIP_DIRS = {"node_modules", ".git", "AppData", "$Recycle.Bin", "System Volume Information", "Windows", "ProgramData"}

# --- Database & Search Engine ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            path TEXT UNIQUE,
            ext TEXT
        )
    """)
    conn.commit()
    conn.close()

def build_index():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    roots = [f"{letter}:\\" for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{letter}:\\")] if os.name == "nt" else [os.path.expanduser("~")]
    for root_path in roots:
        for root, dirs, files in os.walk(root_path, topdown=True, onerror=lambda e: None):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for d in dirs:
                cursor.execute("INSERT OR IGNORE INTO files (name, path, ext) VALUES (?, ?, ?)", (d.lower(), os.path.join(root, d), "folder"))
            for f in files:
                cursor.execute("INSERT OR IGNORE INTO files (name, path, ext) VALUES (?, ?, ?)", (f.lower(), os.path.join(root, f), os.path.splitext(f)[1].lower()))
    conn.commit()
    conn.close()

def search_sqlite(keyword: str, ext: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    query = "SELECT path FROM files WHERE name LIKE ?"
    params = [f"%{keyword}%"]
    if ext:
        query += " AND ext = ?"
        params.append(ext)
    query += " LIMIT 15"
    cursor.execute(query, params)
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

def open_file(path: str):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path], check=False)
    else:
        subprocess.run(["xdg-open", path], check=False)

# --- AI Chat Engine (with local fallback) ---
def process_chat_with_ai(user_text: str):
    def fallback_search():
        clean_word = user_text.lower()
        for word in ["find", "open", "my", "folder", "file", "project", "i want to", "search"]:
            clean_word = clean_word.replace(word, "")
        return {
            "reply": f"Searching your PC for '{clean_word.strip()}'...",
            "is_search": True,
            "keyword": clean_word.strip(),
            "ext": ""
        }

    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() in ("YOUR_API_KEY_HERE", "Your Api Key here"):
        return fallback_search()

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Friendly and talkative personality injected here!
        prompt = f"""
        You are GETFile Ai, a super friendly and talkative desktop assistant.
        Chat with the user naturally, just like a human or ChatGPT.
        Analyze user input: '{user_text}'
        
        Return ONLY valid raw JSON without markdown formatting:
        {{"reply": "Your very friendly, talkative response here", "is_search": true, "keyword": "search term", "ext": ""}}
        """
        
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt
        )
        
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[-1].rsplit("\n", 1)[0].replace("json", "").strip()
            
        return json.loads(raw_text)

    except Exception as e:
        print(f"API Error (using fallback): {e}")
        return fallback_search()

# --- Drag & Drop File List Widget ---
class DraggableFileList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(item.text())])
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.CopyAction)

# --- Main UI ---
class GetFileAIChatbot(QWidget):
    def __init__(self):
        super().__init__()
        init_db()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("GETFile Ai - Chatbot")
        self.setGeometry(300, 100, 750, 650)
        self.setStyleSheet("""
            QWidget { background-color: #181825; color: #cdd6f4; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
            QLineEdit { background-color: #313244; color: #ffffff; padding: 12px; border-radius: 20px; border: 1px solid #45475a; }
            QPushButton { background-color: #89b4fa; color: #11111b; font-weight: bold; border-radius: 18px; padding: 10px 20px; }
            QPushButton:hover { background-color: #b4befe; }
            QScrollArea { border: none; }
        """)

        main_layout = QVBoxLayout()

        # Header bar
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>GETFile Ai Chatbot</b>"))
        index_btn = QPushButton("Re-Index PC")
        index_btn.clicked.connect(self.reindex_system)
        header_layout.addWidget(index_btn, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(header_layout)

        # Chat Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.addStretch()
        self.chat_container.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area)

        # Input Bar
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Chat or ask to find files (e.g., 'find my sangmin pdf')...")
        self.input_field.returnPressed.connect(self.send_message)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)
        self.add_ai_message("Hello! I am **GETFile Ai**. I'm all set up and ready to chat! What can I help you find today?")

    def add_user_message(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("background-color: #89b4fa; color: #11111b; padding: 10px 15px; border-radius: 15px; margin: 5px;")
        lbl.setWordWrap(True)
        
        box = QHBoxLayout()
        box.addStretch()
        box.addWidget(lbl)
        self.chat_layout.addLayout(box)

    def add_ai_message(self, text, files=None):
        wrapper = QVBoxLayout()
        
        lbl = QLabel(text)
        lbl.setStyleSheet("background-color: #313244; color: #cdd6f4; padding: 10px 15px; border-radius: 15px; margin: 5px;")
        lbl.setWordWrap(True)
        
        box = QHBoxLayout()
        box.addWidget(lbl)
        box.addStretch()
        wrapper.addLayout(box)

        if files:
            file_list = DraggableFileList()
            file_list.setStyleSheet("background-color: #1e1e2e; border: 1px solid #45475a; border-radius: 10px; padding: 5px; margin-left: 10px;")
            file_list.setFixedHeight(120)
            for f in files:
                file_list.addItem(f)
            file_list.itemDoubleClicked.connect(lambda item: open_file(item.text()))
            wrapper.addWidget(file_list)

        self.chat_layout.addLayout(wrapper)

    def send_message(self):
        user_text = self.input_field.text().strip()
        if not user_text: return

        self.input_field.clear()
        self.add_user_message(user_text)
        QApplication.processEvents()

        ai_res = process_chat_with_ai(user_text)
        
        files = []
        if ai_res.get("is_search") and ai_res.get("keyword"):
            files = search_sqlite(ai_res.get("keyword"), ai_res.get("ext", ""))
            if not files:
                ai_res["reply"] += "\n\n(No matching files found. Click 'Re-Index PC' at the top right if you haven't indexed recently.)"

        self.add_ai_message(ai_res.get("reply", "All done!"), files if files else None)

    def reindex_system(self):
        self.add_ai_message("Indexing your computer files... Just a moment!")
        QApplication.processEvents()
        build_index()
        self.add_ai_message("Indexing complete! I am fully updated and ready to search instantly.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = GetFileAIChatbot()
    ex.show()
    sys.exit(app.exec())