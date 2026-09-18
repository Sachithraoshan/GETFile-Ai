# GETFile AI 🔍🤖

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![AI Model](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**GETFile AI** is an intelligent desktop search agent and conversational assistant designed to help you locate, open, and organize files on your computer using natural language queries.

Instead of remembering complex folder structures or exact filenames, simply ask in natural language—like *"Find my math assignment PDF from last week"* or *"Open my profile picture"*.

---

## 🌟 Key Features

- 💬 **Conversational Search:** Ask for files in plain English. The built-in AI extracts target file extensions and semantic keywords automatically.
- ⚡ **Lightning-Fast SQLite Indexing:** Indexes directories across drives into a local SQLite database for instant retrieval.
- 🔄 **Smart Offline Fallback:** Functions seamlessly offline using heuristic NLP parser even without an active internet connection or Gemini API key.
- 🖱️ **Drag-and-Drop File Sharing:** Drag search results directly from the chat window into your browser, email client, Slack, or desktop folders.
- 🎨 **Modern Dark UI:** Clean, responsive desktop interface crafted with PyQt6.
- 💻 **Cross-Platform Foundation:** Built with cross-platform core logic supporting Windows, macOS, and Linux.

---

## 🛠️ Tech Stack

- **GUI:** [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- **AI Engine:** [Google GenAI SDK](https://github.com/google-gemini/generative-ai-python) (`gemini-2.5-flash` / Gemini API)
- **Database:** SQLite3 (Local high-performance file indexing)
- **Packaging:** PyInstaller (Standalone desktop binary support)

---

## 📁 Repository Structure

```text
GETFile-Ai/
├── core_search.py       # Standalone CLI search engine & heuristics
├── gui_app.py           # PyQt6 Desktop chatbot interface & SQLite indexer
├── gui_app.spec         # PyInstaller build specification
├── requirements.txt     # Python project dependencies
├── .env.example         # Example environment configuration
├── .gitignore           # Git ignore rules for clean repository
└── README.md            # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Sachithraoshan/GETFile-Ai.git
cd GETFile-Ai
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API (Optional)

GETFile AI runs out-of-the-box using built-in keyword extraction. To enable conversational AI responses with Google Gemini:

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Set your API key inside `.env`:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

---

## 🖥️ Usage

### Run Desktop GUI Application

```bash
python gui_app.py
```

- **Re-Index PC:** Click the **Re-Index PC** button in the top right to scan and index your drives.
- **Search:** Type requests like `find my report docx` or `open python notes` in the chat input.
- **Open / Drag:** Double-click any result to open it immediately, or drag items into other applications.

### Run Standalone CLI Search

```bash
python core_search.py
```

---

## 📦 Packaging Executable

To compile a standalone `.exe` without console windows using PyInstaller:

```bash
pip install pyinstaller
pyinstaller gui_app.spec
```

The compiled binary will be placed in the `dist/` directory.

---

## 🗺️ Roadmap

- [ ] Semantic vector search using ChromaDB for document content inspection
- [ ] In-depth document parsing (PDF, DOCX, XLSX content indexing)
- [ ] Local LLM integration (Ollama / Llama.cpp) for 100% private, offline inference
- [ ] Tray minimization and background file watcher for real-time index updates

---

## 🤝 Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

*Developed with ❤️ by [Sachithra Oshan](https://github.com/Sachithraoshan)*
