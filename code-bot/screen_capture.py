import io
import time
import base64
from PIL import Image, ImageChops, ImageStat
import pyautogui

def capture_single_frame(box=None) -> Image.Image:
    """Takes a screenshot of the whole screen or specified bounding box."""
    if box:
        shot = pyautogui.screenshot(region=box)
    else:
        shot = pyautogui.screenshot()
    return shot

def compute_image_diff_percent(img1: Image.Image, img2: Image.Image, region=None) -> float:
    """Calculates the percentage pixel difference between two images (0.0 to 100.0)."""
    if img1 is None or img2 is None:
        return 100.0
    
    # Optional region cropping (e.g., question pane area)
    if region:
        i1 = img1.crop(region)
        i2 = img2.crop(region)
    else:
        i1 = img1
        i2 = img2

    # Fast grayscale thumbnail comparison
    thumb_size = (360, 240)
    t1 = i1.convert("L").resize(thumb_size)
    t2 = i2.convert("L").resize(thumb_size)
    
    diff = ImageChops.difference(t1, t2)
    stat = ImageStat.Stat(diff)
    return (stat.mean[0] / 255.0) * 100.0

def detect_scrollable_pane(width: int, height: int) -> tuple[int, int]:
    """
    Tests candidate positions across different competitive platforms (LeetCode, HackerRank, 
    CodeChef, Mettl, Canvas) to detect which pane actually scrolls when wheeled.
    """
    candidates = [
        (int(width * 0.28), int(height * 0.50)),  # Left pane (LeetCode, typical IDEs)
        (int(width * 0.40), int(height * 0.50)),  # Left-mid pane (HackerRank, Canvas)
        (int(width * 0.50), int(height * 0.50)),  # Centered problem statement
        (int(width * 0.20), int(height * 0.40)),  # Narrow left column
    ]

    base_frame = capture_single_frame()

    for x, y in candidates:
        pyautogui.moveTo(x, y)
        pyautogui.scroll(-250)
        time.sleep(0.35)
        test_frame = capture_single_frame()
        diff = compute_image_diff_percent(base_frame, test_frame)
        
        # If wheel caused visible scrolling, restore position and select this pane
        if diff >= 0.7:
            pyautogui.scroll(250)
            time.sleep(0.2)
            print(f"[ScreenCapture] Detected active scroll container at ({x}, {y}) [Diff: {diff:.2f}%]")
            return (x, y)
        else:
            # Revert any minor micro-movement
            pyautogui.scroll(250)
            time.sleep(0.1)

    # Fallback to standard 28% left pane
    default_pos = (int(width * 0.28), int(height * 0.50))
    print(f"[ScreenCapture] Using default question pane at {default_pos}")
    return default_pos

def trigger_horizontal_scroll(amount: int, x: int, y: int):
    """
    Attempts browser horizontal scrolling using both pyautogui.hscroll 
    and Shift + MouseWheel fallback for multi-platform compatibility.
    """
    pyautogui.moveTo(x, y)
    try:
        # Some browsers/OS accept hscroll directly
        pyautogui.hscroll(amount)
        time.sleep(0.1)
    except Exception:
        pass

    # Universal browser fallback: Shift + Wheel
    try:
        pyautogui.keyDown('shift')
        pyautogui.scroll(-amount if amount > 0 else abs(amount))
        time.sleep(0.15)
    finally:
        pyautogui.keyUp('shift')

def stitch_images_vertically(images: list[Image.Image]) -> Image.Image:
    """Stitches multiple consecutive screenshots vertically into a single panoramic image."""
    if not images:
        return None
    if len(images) == 1:
        return images[0]

    max_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)

    stitched = Image.new("RGB", (max_width, total_height), (255, 255, 255))
    y_offset = 0
    for img in images:
        if img.mode != "RGB":
            img = img.convert("RGB")
        stitched.paste(img, (0, y_offset))
        y_offset += img.height

    return stitched

def stitch_images_horizontally(images: list[Image.Image]) -> Image.Image:
    """Stitches multiple screenshots horizontally into a single wide image."""
    if not images:
        return None
    if len(images) == 1:
        return images[0]

    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)

    stitched = Image.new("RGB", (total_width, max_height), (255, 255, 255))
    x_offset = 0
    for img in images:
        if img.mode != "RGB":
            img = img.convert("RGB")
        stitched.paste(img, (x_offset, 0))
        x_offset += img.width

    return stitched

def adaptive_multi_scroll_capture(
    max_scrolls: int = 6,
    scroll_amount: int = -650,
    delay: float = 0.6,
    check_horizontal: bool = True
) -> dict:
    """
    Dynamically scrolls as many times as necessary to capture the entire problem.
    - Automatically discovers the scrollable problem container across any platform.
    - Stops scrolling as soon as the bottom is reached (diff < 0.8%).
    - Tests for horizontal scroll (wide tables, long math formulas, diagrams).
    - Stitches frames vertically and provides individual frames.
    """
    frames = []
    width, height = pyautogui.size()

    print("[ScreenCapture] Capturing Frame 1 (top initial view)...")
    frame1 = capture_single_frame()
    frames.append(frame1)

    # Detect scroll container
    target_x, target_y = detect_scrollable_pane(width, height)
    pyautogui.moveTo(target_x, target_y)

    prev_frame = frame1
    scrolls_performed = 0

    for i in range(max_scrolls):
        print(f"[ScreenCapture] Scrolling down step {i + 1}/{max_scrolls}...")
        pyautogui.moveTo(target_x, target_y)
        pyautogui.scroll(scroll_amount)
        time.sleep(delay)

        new_frame = capture_single_frame()
        diff = compute_image_diff_percent(prev_frame, new_frame)
        print(f"[ScreenCapture] Frame {i + 2} difference: {diff:.2f}%")

        # If screen didn't change, we hit the bottom of the page/container
        if diff < 0.8:
            print(f"[ScreenCapture] Reached bottom of question pane at scroll {i + 1}. Halting vertical scroll.")
            break

        frames.append(new_frame)
        prev_frame = new_frame
        scrolls_performed += 1

    # Check for horizontal scroll if problem might be wide
    horizontal_frames = []
    if check_horizontal:
        print("[ScreenCapture] Checking for horizontal scrollable content...")
        trigger_horizontal_scroll(600, target_x, target_y)
        time.sleep(delay)
        h_frame = capture_single_frame()
        h_diff = compute_image_diff_percent(prev_frame, h_frame)

        if h_diff >= 1.0:
            print(f"[ScreenCapture] Horizontal content detected ({h_diff:.2f}% new). Adding horizontal frame.")
            horizontal_frames.append(h_frame)
            frames.append(h_frame)
            # Restore horizontal scroll to left
            trigger_horizontal_scroll(-600, target_x, target_y)
            time.sleep(0.3)
        else:
            print("[ScreenCapture] No horizontal scroll needed.")
            trigger_horizontal_scroll(-600, target_x, target_y)

    # Vertical stitch of frames
    print(f"[ScreenCapture] Stitching {len(frames)} total frames...")
    stitched_img = stitch_images_vertically(frames)

    return {
        "frames": frames,
        "stitched": stitched_img,
        "scrolls_performed": scrolls_performed,
        "has_horizontal": len(horizontal_frames) > 0
    }

# Backward compatibility alias
def capture_with_scroll(scroll_count: int = 1, scroll_amount: int = -500, delay: float = 0.6) -> list[Image.Image]:
    """Legacy wrapper that uses adaptive multi-scroll capture."""
    res = adaptive_multi_scroll_capture(max_scrolls=max(scroll_count, 5), scroll_amount=scroll_amount, delay=delay)
    return res["frames"]

def image_to_base64(img: Image.Image, max_dim: int = 1800) -> str:
    """Resizes if necessary to preserve aspect ratio and converts to base64 JPEG."""
    if img.mode != "RGB":
        img = img.convert("RGB")
        
    w, h = img.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
