' Windows Task Scheduler Kurulum - VBScript
' Yönetici olarak çalışır

Set WshShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strPythonPath = "C:\Users\metin\Desktop\BRІÇ\.venv\Scripts\python.exe"
strScriptPath = "C:\Users\metin\Desktop\BRІÇ\scheduled_server.py"

' Kontrol et
If Not objFSO.FileExists(strPythonPath) Then
    MsgBox "Hata: Python bulunamadı (" & strPythonPath & ")", vbCritical
    WScript.Quit 1
End If

If Not objFSO.FileExists(strScriptPath) Then
    MsgBox "Hata: Scheduler script bulunamadı (" & strScriptPath & ")", vbCritical
    WScript.Quit 1
End If

' Task Scheduler'a ekle
strCommand = "schtasks /create /tn ""BridgeBot_AutoUpdate"" /tr """ & strPythonPath & " " & strScriptPath & """ /sc onstart /ru SYSTEM /f /rl highest"

On Error Resume Next
WshShell.Run "cmd /c " & strCommand, 0, True
intErr = Err.Number
On Error Goto 0

If intErr = 0 Then
    MsgBox "✓ Görev başarıyla oluşturuldu!" & vbCrLf & _
           "Adı: BridgeBot_AutoUpdate" & vbCrLf & _
           "Tetikleyici: Sistem başlangıcında", vbInformation
Else
    MsgBox "✗ Görev oluşturulamadı. Hata kodu: " & intErr, vbCritical
End If

' Görev listesini aç
WshShell.Run "taskmgr.exe", 1, False
