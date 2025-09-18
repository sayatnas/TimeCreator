' TimeCreator silent startup script (VBS version)
' Runs TimeCreator without any visible windows

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Change to the TimeCreator directory and run silently
objShell.Run "cmd /c cd /d """ & strScriptDir & """ && pythonw launch.py overlay", 0, False