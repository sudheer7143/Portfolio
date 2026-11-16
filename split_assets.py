from pathlib import Path
import re

html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")

# Move the custom stylesheet into styles.css.
style_pattern = re.compile(r"<style>([\s\S]*?)</style>", re.IGNORECASE)
html, style_count = style_pattern.subn(
    '<link rel="stylesheet" href="styles.css" />',
    html,
    count=1,
)
if style_count != 1:
    raise SystemExit("Expected exactly one inline <style> block.")

style_match = style_pattern.search(html_path.read_text(encoding="utf-8"))
Path("styles.css").write_text(style_match.group(1).strip() + "\n", encoding="utf-8")

# Move the inline application script, leaving Tailwind configuration in the HTML.
script_pattern = re.compile(
    r"<script\b([^>]*)>([\s\S]*?)</script>",
    re.IGNORECASE,
)
scripts = list(script_pattern.finditer(html))
app_script = next(
    (
        match for match in reversed(scripts)
        if "src=" not in match.group(1).lower()
        and "tailwind.config" not in match.group(2)
        and match.group(2).strip()
    ),
    None,
)
if app_script is None:
    raise SystemExit("Could not find the inline application script.")

Path("script.js").write_text(app_script.group(2).strip() + "\n", encoding="utf-8")
html = html[:app_script.start()] + '<script src="script.js" defer></script>' + html[app_script.end():]

html_path.write_text(html, encoding="utf-8")
print("Created styles.css and script.js; updated index.html.")