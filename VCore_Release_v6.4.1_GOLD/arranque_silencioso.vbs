Set WshShell = CreateObject("WScript.Shell")
' Detectamos la ruta de la carpeta automáticamente
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strPath

' Lanzamos los motores usando python.exe (que ESET si permite)
' El "0" al final los hace totalmente invisibles aunque no sean "w"
WshShell.Run "venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000", 0, False
WshShell.Run "venv\Scripts\python.exe watcher.py", 0, False