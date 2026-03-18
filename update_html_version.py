file_path = "templates/cfdis.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'src="/static/js/cfdis.js?v=1.1"' in content:
    content = content.replace('src="/static/js/cfdis.js?v=1.1"', 'src="/static/js/cfdis.js?v=1.2"')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Version updated to 1.2 in cfdis.html")
else:
    print("ℹ️ Version tag not found or already updated.")
