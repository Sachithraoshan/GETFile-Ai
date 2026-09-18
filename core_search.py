import os
import sys
import subprocess

EXTENSIONS = {
    "pdf": ".pdf", "doc": ".docx", "word": ".docx",
    "python": ".py", "code": ".py", "image": ".png", 
    "photo": ".jpg", "excel": ".xlsx", "video": ".mp4"
}

# Added 'in', 'at', 'on', 'documents', 'desktop', 'downloads' to stopwords
STOPWORDS = {
    "find", "my", "the", "a", "an", "file", "files", "folder", 
    "open", "for", "of", "in", "on", "at", "to", "documents", "desktop", "downloads"
}

SKIP_DIRS = {
    "node_modules", ".git", "AppData", "$Recycle.Bin", 
    "System Volume Information", "Windows", "ProgramData"
}

def parse_user_input(text: str):
    words = text.lower().split()
    target_ext = ""
    keywords = []

    for word in words:
        word = word.strip(".,!?")
        if word in EXTENSIONS:
            target_ext = EXTENSIONS[word]
        elif word not in STOPWORDS:
            keywords.append(word)

    return " ".join(keywords), target_ext

def get_search_roots():
    if os.name == "nt":
        import string
        drives = [f"{letter}:\\" for letter in string.ascii_uppercase if os.path.exists(f"{letter}:\\")]
        return drives or [os.path.expanduser("~")]
    return [os.path.expanduser("~")]

def open_file(path: str):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception as e:
        print(f"Couldn't open path ({e}): {path}")

def search_files_and_folders(keyword: str, target_ext: str, roots, max_results: int = 15):
    matches = []

    for root_path in roots:
        for root, dirs, files in os.walk(root_path, topdown=True, onerror=lambda e: None):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

            # 1. Search Folders (If no specific extension requested)
            if not target_ext:
                for dir_name in dirs:
                    if keyword and keyword in dir_name.lower():
                        matches.append(os.path.join(root, dir_name))
                        if len(matches) >= max_results:
                            return matches

            # 2. Search Files
            for file_name in files:
                lower_name = file_name.lower()
                if target_ext and not lower_name.endswith(target_ext):
                    continue
                if keyword and keyword not in lower_name:
                    continue
                matches.append(os.path.join(root, file_name))
                if len(matches) >= max_results:
                    return matches

    return matches

def getfile_ai_search(user_prompt: str):
    keyword, ext = parse_user_input(user_prompt)
    print(f"AI Parsed -> Keyword: '{keyword}' | Extension: '{ext or 'any'}'\n")

    roots = get_search_roots()
    matches = search_files_and_folders(keyword, ext, roots)

    if not matches:
        print("No matching files or folders found.")
        return

    if len(matches) == 1:
        print(f"Found Match! Opening: {matches[0]}")
        open_file(matches[0])
        return

    print(f"Found {len(matches)} matches:\n")
    for i, m in enumerate(matches, 1):
        print(f"  [{i}] {m}")

    choice = input("\nWhich one do you want to open? (number, or Enter to skip): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(matches):
        open_file(matches[int(choice) - 1])

if __name__ == "__main__":
    getfile_ai_search("open my profile pic image")