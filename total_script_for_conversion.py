import os
import re

DOCS_DIR = "docs"

# Patterns
HINT_START_PATTERN = re.compile(r'\{%\s*hint\s+style="(.*?)"\s*%\}')
HINT_END_PATTERN = re.compile(r'\{%\s*endhint\s*%\}')
TABS_START_PATTERN = re.compile(r"\{%\s*tabs\s*%\}")
TAB_TITLE_PATTERN = re.compile(r'\{%\s*tab\s+title="(.*?)"\s*%\}')
TABS_END_PATTERN = re.compile(r"\{%\s*endtabs\s*%\}")
TAB_END_PATTERN = re.compile(r"\{%\s*endtab\s*%\}")
YOUTUBE_PATTERN = re.compile(r'\{\{<\s*youtube\s+(.*?)\s*>}}')

# Conversion
def convert_gitbook_to_docusaurus(content):
    lines = content.splitlines()
    new_lines = []
    inside_hint = False
    hint_type = ""

    inside_tabs = False
    inside_tab = False

    for line in lines:
        stripped = line.strip()

        # Handle {% hint %}
        if (m := HINT_START_PATTERN.match(stripped)):
            inside_hint = True
            hint_type = m.group(1).capitalize()
            new_lines.append(f"> 💡 **{hint_type}**")
            continue
        elif HINT_END_PATTERN.match(stripped):
            inside_hint = False
            continue
        elif inside_hint:
            new_lines.append(f"> {line}")
            continue

        # Handle {% tabs %}
        if TABS_START_PATTERN.match(stripped):
            inside_tabs = True
            new_lines.append("import Tabs from '@theme/Tabs';\nimport TabItem from '@theme/TabItem';\n\n<Tabs>")
            continue
        elif TABS_END_PATTERN.match(stripped):
            inside_tabs = False
            new_lines.append("</Tabs>")
            continue
        elif (m := TAB_TITLE_PATTERN.match(stripped)):
            inside_tab = True
            title = m.group(1)
            new_lines.append(f'<TabItem value="{title.lower()}" label="{title}">')
            continue
        elif TAB_END_PATTERN.match(stripped):
            inside_tab = False
            new_lines.append("</TabItem>")
            continue

        # Handle YouTube embed {{< youtube ID >}}
        if (m := YOUTUBE_PATTERN.match(stripped)):
            video_id = m.group(1).strip()
            iframe = f"""<iframe width="100%" height="400" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>"""
            new_lines.append(iframe)
            continue

        # Default behavior
        new_lines.append(line)

    return "\n".join(new_lines)

# Process each .md file
def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if any(keyword in content for keyword in ["{% hint", "{% tabs", "{{< youtube"]):
        print(f"🔧 Converting: {path}")
        converted = convert_gitbook_to_docusaurus(content)

        # Backup original
        backup_path = path + ".bak"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)

        with open(path, "w", encoding="utf-8") as f:
            f.write(converted)

# Walk through docs directory
def walk_docs():
    for dirpath, _, filenames in os.walk(DOCS_DIR):
        for filename in filenames:
            if filename.endswith(".md"):
                full_path = os.path.join(dirpath, filename)
                process_file(full_path)

if __name__ == "__main__":
    walk_docs()
    print("✅ All Markdown files processed and GitBook syntax converted.")
