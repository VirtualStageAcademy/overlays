
# Tech Overview Core Document

## 1. Project Vision and Goals
- **Short-Term Outcomes**:
  - Set up a scalable and modular project structure.
  - Automate file discovery with `os.walk` and environment variables.
  - Launch the initial version of VSA with core features.

- **Long-Term Outcomes**:
  - Build a robust platform for live presentations.
  - Integrate dynamic overlays, WebSocket functionalities, and API support.
  - Scale the project for global users with high performance and security.

---

## 2. Coding Philosophy
- **Use of `os.walk`**:
  - Dynamically discover files and directories to reduce hardcoding.
  - Encapsulate logic in reusable, modular functions.

- **Environment Variables**:
  - Store critical paths, keys, and settings in `.env` files for flexibility.
  - Use libraries like `python-dotenv` to load variables dynamically.

- **Modular Organization**:
  - Follow the principle of **separation of concerns** (e.g., Backend, Config, Frontend).
  - Write reusable code for overlays, API integrations, and other shared components.

---

## 3. Directory and File Structure
The core directory structure for **TechHub**:
```
TechHub/
├── Backend/
├── Config/
│   ├── .env                # Shared environment variables
│   ├── .env.development    # Development-specific variables
│   ├── .env.production     # Production-specific variables
│   └── config.yaml         # Centralized configuration
├── Frontend/
├── GitHub/
├── Platforms/
├── Tech Overview/         # Added this folder for clarity
│   ├── Tech_Overview_Core.md
│   └── Supporting_Docs/
├── Tests/
├── Vercel/
└── Website/
```

**Best Practices**:
1. Keep environment-specific variables in `.env.*` files.
2. Use `README.md` in each folder to document its purpose.

---

## 4. Code Logic and Tools
- **Tools**:
  - Python for backend and file discovery.
  - GitHub for version control.
  - Vercel for hosting overlays and APIs.

- **Reusable Function for File Discovery**:
```python
import os

class FileFinder:
    def __init__(self, base_path):
        self.base_path = base_path

    def find_file(self, file_name):
        for root, dirs, files in os.walk(self.base_path):
            if file_name in files:
                return os.path.join(root, file_name)
        return None
```

---

## 5. Environment Variables
- **Common Variables**:
  - `TECHHUB_PATH`: Base path for the TechHub folder.
  - `ENV`: Current environment (development, production).

**Best Practices**:
- Use `.env` for shared settings and `.env.*` for environment-specific configurations.
- Never commit `.env` files to version control.

---

## 6. Current Task List
- [ ] Finalize Tech Overview core document.
- [ ] Set up `os.walk` and environment variable utilities.
- [ ] Create and populate **Config** folder with `.env` files.

---

## 7. Long-Term Roadmap
- Phase 1: Build dynamic overlays (Chat, Emoji, Wordcloud).
- Phase 2: Integrate API support for Zoom, YouTube, and Facebook.
- Phase 3: Launch production-ready platform with scalability.
