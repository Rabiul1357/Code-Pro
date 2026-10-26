# 🚀 Code-Pro: Automated Coding Scanner, Solver & Interactive Assistant

An end-to-end automated system designed for coding platforms and online assessments (LeetCode, HackerRank, CodeChef, Mettl, etc.).

The system consists of:
1. **`code-bot/` (Python CLI Bot)**: Captures your screen, automatically scrolls down to capture long problem statements & test cases, uses Google Gemini Multimodal Vision to solve the problem, and uploads the solution to Firebase Realtime Database.
2. **`code-pro/` (Vite + React Web App)**: Real-time web dashboard that displays questions as clean single-line summaries, provides a full Monaco Code Editor with one-click copy, includes remote Start/Stop bot controls, and features an interactive AI chatbot to debug or optimize code.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A[Browser / Coding Assessment Screen] -->|F9 Hotkey / Auto-scroll Capture| B[Python code-bot]
    B -->|Gemini Multimodal Vision API| C[Extracts Question & Solves Code]
    C -->|Uploads via Admin SDK / REST| D[(Firebase Realtime Database)]
    D <-->|Realtime Listener & Sync| E[Vite Web App: code-pro]
    E -->|Remote Start / Stop Toggle| D
    E -->|Chatbot Refinement| F[Gemini AI: Fix / Optimize / Convert]
    F -->|Apply to Editor| E
```

---

## 🌟 Key Features

* **⚡ Auto-Scroll Multi-Frame Capture**: Automatically scrolls the question panel to capture the complete problem statement, constraints, example test cases, and starter code.
* **🧠 Gemini Multimodal Vision AI**: Solves problems directly from screenshots without fragile OCR. Matches the platform's starter code template (e.g., C++, Python, Java).
* **🔑 Multi-Key Failover Rotation**: Pre-configured with automatic rotation across 5 Gemini API keys so you never hit rate limits.
* **🔥 Firebase Realtime Database Integration**: Supports both native `firebase-admin` (Service Account) and REST API fallback. Instant syncing without page reloads.
* **🛑 Remote Bot Control**: Navbar toggle button on the website lets you **Start** or **Pause** the Python bot remotely at any time.
* **💻 Monaco Code Editor**: Embedded VS Code editor (`vs-dark` theme) with language selection, instant one-click **Copy Code** button, and reset capabilities.
* **🤖 Integrated AI Assistant Chatbot**: Ask Gemini to optimize time complexity, fix potential edge cases, or convert code between languages with a 1-click **"Apply to Editor"** button.

---

## 📁 Directory Structure

```
Code-Pro/
├── README.md                                      # Comprehensive documentation
├── IMPLEMENTATION_PLAN.md                         # Architecture and implementation plan
├── .gitignore                                     # Protects credentials, node_modules, dumps
├── quipu-c6fdb-firebase-adminsdk-*.json           # Firebase Admin Service Account credentials
├── code-bot/                                      # Python CLI Bot
│   ├── bot.py                                     # Interactive CLI entrypoint
│   ├── gemini_solver.py                           # Gemini Vision solver with key failover
│   ├── screen_capture.py                          # Multi-frame auto-scrolling capture
│   ├── firebase_client.py                         # Firebase Admin SDK & REST client
│   ├── config.py                                  # API keys & model configurations
│   └── requirements.txt                           # Python dependencies
└── code-pro/                                      # Vite + React Web App
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx                                # Main layout and state coordinator
        ├── firebase.js                            # Firebase Realtime Database client
        ├── gemini.js                              # Client-side chatbot AI integration
        ├── index.css                              # Modern styling and design system
        └── components/
            ├── Navbar.jsx                         # Header with remote bot toggle
            ├── QuestionList.jsx                   # Chronological sidebar problem list
            ├── QuestionView.jsx                   # Single-line title & expandable details
            ├── CodeEditor.jsx                     # Monaco editor with copy button
            └── Chatbot.jsx                        # AI assistant with prompt chips
```

---

## 🚀 How to Run and Use

### Step 1: Start the Web App (`code-pro`)

Open a terminal in the project directory:

```powershell
cd c:\Users\skahi\Downloads\Code-Pro\code-pro
npm run dev
```

The web dashboard will be available at:
👉 **`http://localhost:5173/`**

---

### Step 2: Run the Python Bot (`code-bot`)

Simply double-click **`run.bat`** inside `code-bot/`, or run:

```powershell
cd code-bot
.\run.bat
```
*(On the first run, `run.bat` automatically creates a virtual environment `.venv` and installs all dependencies. On subsequent runs, it starts instantly via `.venv`!)*


You will see the continuous daemon output:
```
================================================================
       🚀 CODE-PRO FULLY AUTOMATED SCANNER BOT
================================================================
 * Control Mode:   100% REMOTE (Controlled via Website Navbar)
 * Terminal Input: NONE REQUIRED (Runs continuously in background)
 * Remote Polling: Every 2 seconds from Firebase RTDB
 * Hotkey Fallback: Press 'F9' to trigger manually anytime
 * Stop Bot:       Press Ctrl+C in this terminal to exit
================================================================
[22:25:00] 🔴 Bot initialized in OFF state.
[22:25:00] 👉 Open your website (http://localhost:5173) and click 'Start Bot' whenever you have a problem on screen.
```

---

### Step 3: Solve Coding Problems (Zero Terminal Touch)

1. Keep the Python bot running in the terminal. **You never have to type anything in the terminal.**
2. Open your coding problem in your browser (LeetCode, HackerRank, etc.).
3. Open your `code-pro` website (or on your phone/another tab).
4. Whenever you want to scan and solve a problem, click **"Start Bot"** in the website navbar:
   - The Python bot automatically detects the trigger within 2 seconds.
   - It captures the screen, automatically scrolls down to read the full description and constraints, and captures the second frame.
   - Gemini Vision AI extracts the question, writes an optimal passing solution, and uploads to Firebase.
   - The solution appears **instantly in real time** on your website inside Monaco Editor!
   - The bot automatically resets its status back to ready for the next problem.
5. For the next question, simply click **"Start Bot"** on the website again!

---

### Step 4: Using the Website Features

* **Single-Line Title**: The complex question text is converted into an easy-to-read single-line summary title.
* **Copy Code**: Click the **Copy Code** button above the editor to instantly copy the full code to your clipboard.
* **Remote Bot Toggle**: Use the **Start Bot / Stop Bot** button in the navbar to pause or resume the bot remotely.
* **AI Chatbot**:
  * If a platform fails a testcase or you need an alternative language, click quick chips like:
    * `⚡ Optimize Time/Space`
    * `🐞 Fix Edge Cases`
    * `🐍 Convert to Python`
    * `☕ Convert to Java`
  * Or type a custom prompt.
  * When the AI provides a new solution, click **"Apply to Editor"** to update the code in Monaco editor directly!

---

## 🔒 Security Note
* The `.gitignore` file is pre-configured to ensure service account JSON files (`*firebase-adminsdk*.json`) and private keys are never committed to version control.
