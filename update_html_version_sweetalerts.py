file_path = "templates/cfdis.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'src="/static/js/cfdis.js?v=1.5"' in content:
    content = content.replace('src="/static/js/cfdis.js?v=1.5"', 'src="/static/js/cfdis.js?v=1.6"')
    print("✅ Version updated to 1.6")
elif 'src="/static/js/cfdis.js?v=1.4"' in content:
    content = content.replace('src="/static/js/cfdis.js?v=1.4"', 'src="/static/js/cfdis.js?v=1.6"')
    print("✅ Version updated from 1.4 to 1.6")
else:
    print("ℹ️ Version tag not found or already updated.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
