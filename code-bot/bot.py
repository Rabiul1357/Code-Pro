import os
import sys
import time
from datetime import datetime

# Ensure Windows console supports UTF-8 characters and emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import GEMINI_API_KEYS
from firebase_client import (
    get_bot_status,
    set_bot_status,
    push_question,
    get_questions,
    clear_all_questions
)
from screen_capture import adaptive_multi_scroll_capture, capture_with_scroll
from gemini_solver import solve_from_images

POLL_INTERVAL_SECONDS = 2
HOTKEY = "f9"

def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def banner():
    print("=" * 64)
    print("       🚀 CODE-PRO SCANNER & SOLVER BOT (CLI)")
    print("=" * 64)
    print(" * Firebase RTDB: Connected (Admin SDK & REST)")
    print(f" * Gemini API Keys: {len(GEMINI_API_KEYS)} configured with auto-failover")
    print(f" * Remote Sync: Listening to web toggle (/bot_status)")
    print(" * Vision Engine: Adaptive Multi-Scroll & Stitching (LeetCode/HackerRank/All)")
    print("=" * 64)

def perform_capture_and_solve(max_scrolls: int = 5):
    """Executes the adaptive multi-scroll -> stitch -> solve -> upload pipeline."""
    log("📸 Starting adaptive screen capture sequence in 1 second...")
    time.sleep(1)

    try:
        capture_result = adaptive_multi_scroll_capture(
            max_scrolls=max_scrolls,
            scroll_amount=-650,
            delay=0.6,
            check_horizontal=True
        )
        total_frames = len(capture_result.get("frames", []))
        scrolls = capture_result.get("scrolls_performed", 0)
        has_h = capture_result.get("has_horizontal", False)
        log(f"✅ Captured {total_frames} frames ({scrolls} vertical scrolls, horizontal={has_h}). Analyzing with Gemini AI...")

        result = solve_from_images(capture_result)
        print("-" * 55, flush=True)
        print(f"📌 Problem:    {result.get('title')}", flush=True)
        print(f"💻 Language:   {result.get('language')}", flush=True)
        print(f"⚡ Complexity: {result.get('complexity')}", flush=True)
        print("-" * 55, flush=True)

        log("☁️ Uploading solution to Firebase Realtime Database...")
        key = push_question(result)
        if key:
            log(f"🎉 SUCCESS! Uploaded to Firebase (Key: {key})")
            log("👉 Solution is now live on your code-pro website!")
            return True
        else:
            log("⚠️ Failed to upload question to Firebase.")
            return False
    except Exception as e:
        log(f"❌ Error during solve pipeline: {e}")
        return False

def init_hotkey():
    """Optional background listener for F9 hotkey."""
    try:
        import keyboard
        def on_f9():
            log(f"⚡ Hotkey '{HOTKEY.upper()}' pressed! Triggering capture...")
            perform_capture_and_solve()
        keyboard.add_hotkey(HOTKEY, on_f9)
    except Exception:
        pass

def auto_daemon_loop():
    """Continuous automated polling daemon loop - NO terminal inputs required."""
    print("\n" + "=" * 64)
    print(" 🟢 [OPTION 1] AUTOMATED WEB DAEMON MODE ACTIVE")
    print("=" * 64)
    print(f" * Checking Firebase every {POLL_INTERVAL_SECONDS}s for 'Start Bot' signal from website.")
    print(" * Zero terminal input required while running.")
    print(" * Press 'q' on your keyboard OR Ctrl+C to return to Main Menu.")
    print("=" * 64)

    # Initial safety state: start as OFF
    set_bot_status(False)
    log("🔴 Bot is IDLE / OFF. Waiting for 'Start Bot' click from website...")

    was_active = False

    while True:
        try:
            # Non-blocking key check on Windows
            if sys.platform == "win32":
                try:
                    import msvcrt
                    if msvcrt.kbhit():
                        ch = msvcrt.getch()
                        if ch.lower() in (b'q', b'\x1b'):
                            log("Key 'q' pressed. Returning to Main Menu...")
                            break
                except Exception:
                    pass

            is_active = get_bot_status()

            # State transition: OFF -> ON (User clicked 'Start Bot' on website)
            if is_active and not was_active:
                log("🟢 [WEB TRIGGER] 'Start Bot' activated from website!")
                log("⚡ Beginning automated scan & solve in 1 second...")
                
                perform_capture_and_solve()

                # Reset status to OFF so website button flips back to 'Start Bot'
                set_bot_status(False)
                was_active = False
                log("🔄 Solved! Status reset to OFF. Ready for your next problem.")
                log("Waiting for next 'Start Bot' from website... (Press 'q' to return to menu)\n")

            # State transition: ON -> OFF (User manually stopped or reset)
            elif not is_active and was_active:
                log("🔴 [WEB TRIGGER] Bot was paused/stopped from website.")
                was_active = False

            time.sleep(POLL_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("")
            log("Stopped daemon loop. Returning to Main Menu...")
            break
        except Exception as e:
            log(f"⚠️ Polling warning: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)

def instant_capture():
    sec = 3
    print(f"\n⏱️ Switch to your coding problem browser window! Capturing in {sec} seconds...")
    for s in range(sec, 0, -1):
        print(f"   {s}...", flush=True)
        time.sleep(1)
    set_bot_status(True)
    perform_capture_and_solve()
    set_bot_status(False)

def test_on_dump_screenshot():
    dump_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dump")
    shot1 = os.path.join(dump_dir, "Screenshot (945).png")
    shot2 = os.path.join(dump_dir, "Screenshot (946).png")

    imgs = []
    if os.path.exists(shot1):
        imgs.append(shot1)
    if os.path.exists(shot2):
        imgs.append(shot2)

    if not imgs:
        print("❌ Dump screenshots not found at:", dump_dir)
        return

    print(f"🔍 Testing solver on {len(imgs)} sample screenshot(s) from dump/...")
    result = solve_from_images(imgs)
    print("\n" + "=" * 50)
    print("TITLE:      ", result.get("title"))
    print("LANGUAGE:   ", result.get("language"))
    print("COMPLEXITY: ", result.get("complexity"))
    print("CODE PREVIEW:\n", result.get("solution_code")[:250])
    print("=" * 50)

    push = input("\nUpload this result to Firebase? (y/n) [default: y]: ")
    if push.strip().lower() in ("", "y", "yes"):
        key = push_question(result)
        print(f"✅ Successfully uploaded to Firebase! Key: {key}")

def show_firebase_questions():
    print("\nFetching questions from Firebase Realtime Database...")
    qs = get_questions()
    if not qs:
        print("ℹ️ No questions found in database.")
        return
    print(f"\nFound {len(qs)} question(s):")
    for qid, q in qs.items():
        title = q.get("title", "Untitled")
        lang = q.get("language", "unknown")
        print(f" * [{qid}] ({lang}) {title}")

def main_menu():
    banner()
    init_hotkey()

    while True:
        status = get_bot_status()
        status_str = "🟢 ACTIVE" if status else "🔴 OFF (Paused)"

        print("\n" + "=" * 50)
        print(f"MAIN MENU  [Firebase Status: {status_str}]")
        print("=" * 50)
        print(" [1] Start Automated Web Daemon Mode (Zero terminal input, 2s check)")
        print(" [2] Instant Capture & Solve (3s countdown)")
        print(" [3] Test Solve Sample Screenshots (dump/Two Sum)")
        print(" [4] View All Questions in Firebase")
        print(" [5] Clear All Questions from Firebase Database")
        print(" [6] Toggle Remote Bot Status (On / Off)")
        print(" [0] Exit")

        try:
            choice = input("\nEnter choice [0-6]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting bot. Goodbye!")
            sys.exit(0)

        if choice == "1":
            auto_daemon_loop()
        elif choice == "2":
            instant_capture()
        elif choice == "3":
            test_on_dump_screenshot()
        elif choice == "4":
            show_firebase_questions()
        elif choice == "5":
            confirm = input("⚠️ Are you sure you want to delete all questions from Firebase? (y/n): ")
            if confirm.strip().lower() in ("y", "yes"):
                clear_all_questions()
                print("✅ All questions cleared from Firebase database.")
        elif choice == "6":
            new_status = not status
            set_bot_status(new_status)
            print(f"Updated status to: {'ACTIVE' if new_status else 'OFF'}")
        elif choice == "0":
            print("Exiting bot. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please select 0-6.")

if __name__ == "__main__":
    main_menu()
