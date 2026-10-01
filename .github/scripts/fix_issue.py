import os
import sys
import json
from google import genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    issue_title = os.environ.get("ISSUE_TITLE", "")
    issue_body = os.environ.get("ISSUE_BODY", "")

    if not api_key:
        print("Error: GEMINI_API_KEY is not set.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Gather repository code files (skipping hidden folders, node_modules, binaries, etc.)
    code_context = []
    ignored_dirs = {".git", ".github", "node_modules", "dist", "build", "__pycache__", "venv"}
    allowed_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json", ".md", ".go", ".rs"}

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in allowed_extensions:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        code_context.append(f"--- START FILE: {filepath} ---\n{f.read()}\n--- END FILE: {filepath} ---")
                except Exception:
                    pass

    context_str = "\n\n".join(code_context)

    prompt = f"""You are an automated software engineer. You are given an issue and the codebase files.

ISSUE TITLE: {issue_title}
ISSUE DESCRIPTION:
{issue_body}

CODEBASE:
{context_str}

TASK:
Analyze the issue and codebase. Return a valid JSON array containing ONLY the files that need to be created or modified to fix the issue.

OUTPUT FORMAT REQUIREMENTS:
- Your response MUST be strictly valid JSON.
- Do NOT wrap in markdown formatting unless required. Return a raw JSON array like this:
[
  {{
    "path": "path/to/file.ext",
    "content": "full updated content of the file"
  }}
]
- Include the ENTIRE updated content for each modified file (do not truncate or use placeholders like "...rest of file...").
"""

    print("Sending single API call to Gemini...")
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    try:
        changes = json.loads(response.text)
        if not isinstance(changes, list) or len(changes) == 0:
            print("No file updates were returned by Gemini.")
            sys.exit(0)

        for item in changes:
            path = item.get("path")
            content = item.get("content")
            if path and content is not None:
                if os.path.dirname(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Updated file: {path}")

    except json.JSONDecodeError:
        print("Failed to parse JSON output from Gemini.")
        print("Raw response:", response.text)
        sys.exit(1)

if __name__ == "__main__":
    main()
