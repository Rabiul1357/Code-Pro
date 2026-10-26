import json
import requests
from config import GEMINI_API_KEYS, GEMINI_MODELS
from screen_capture import image_to_base64

PROMPT = """
You are an expert competitive programmer and technical interview assistant.
Analyze these screenshot(s) of a coding challenge (e.g., LeetCode, HackerRank, CodeChef, GeeksForGeeks, Mettl, or online assessment platform).
The images contain sequential scrolled views (vertical and/or horizontal) or a vertically stitched panorama of the full problem.

Please synthesize all parts into a unified problem understanding:
- Combine all text across all scrolled views (problem statement, notes, examples, inputs/outputs, and constraints at the bottom).
- Detect the target programming language and function/class signature from the visible editor.
- Write an optimal, fully passing solution matching the template.

Return your response ONLY as a valid JSON object with the following fields:
{
  "title": "A single-line concise title (e.g., '1. Two Sum - Find two indices that add up to target')",
  "description": "Full problem description, examples, and constraints synthesized in clean markdown",
  "language": "Detected language in editor (e.g. 'cpp', 'python', 'java', 'javascript', 'csharp')",
  "starter_code": "The starter function/class code template visible in the editor",
  "solution_code": "Complete working solution code matching the starter template exactly",
  "complexity": "Time and Space complexity (e.g., 'Time: O(n), Space: O(n)')",
  "explanation": "Short 2-3 bullet points explaining the logic"
}
"""

def solve_from_images(images_input) -> dict:
    """
    Takes a list of PIL Images (or file paths), or a dict from adaptive_multi_scroll_capture,
    encodes them, and calls Gemini Vision API with automatic key and model fallback.
    """
    # Normalize input
    raw_images = []
    if isinstance(images_input, dict):
        # Dict from adaptive_multi_scroll_capture
        stitched = images_input.get("stitched")
        frames = images_input.get("frames", [])
        if stitched:
            raw_images.append(stitched)
        for f in frames:
            if f not in raw_images:
                raw_images.append(f)
    elif isinstance(images_input, list):
        raw_images = images_input
    else:
        raw_images = [images_input]

    image_parts = []
    for item in raw_images:
        if isinstance(item, str):
            # File path
            from PIL import Image
            img = Image.open(item)
            b64 = image_to_base64(img)
        else:
            b64 = image_to_base64(item)
            
        image_parts.append({
            "inlineData": {
                "mimeType": "image/jpeg",
                "data": b64
            }
        })
        
    parts = image_parts + [{"text": PROMPT}]
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }
    
    last_error = None
    
    for key_idx, key in enumerate(GEMINI_API_KEYS):
        for model in GEMINI_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            try:
                print(f"[GeminiSolver] Trying Key #{key_idx + 1} with model '{model}'...")
                res = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=35
                )
                
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_content = candidates[0]["content"]["parts"][0]["text"]
                        parsed = json.loads(text_content)
                        print(f"[GeminiSolver] Successfully solved: {parsed.get('title')}")
                        return parsed
                elif res.status_code == 429:
                    print(f"[GeminiSolver] Rate limited on Key #{key_idx + 1}, switching to next key...")
                    break # Break out to next key
                else:
                    error_msg = res.json().get("error", {}).get("message", res.text[:100])
                    print(f"[GeminiSolver] HTTP {res.status_code}: {error_msg}")
                    last_error = error_msg
            except Exception as e:
                print(f"[GeminiSolver] Exception with model {model}: {e}")
                last_error = str(e)
                
    raise RuntimeError(f"All Gemini API keys and models failed. Last error: {last_error}")
