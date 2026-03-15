$sLinkFile = "$env:USERPROFILE\Desktop\RS-EDL.lnk" 
$sTargetFile = "$PSScriptRoot\run_app.bat" 
$sIconFile = "$PSScriptRoot\assets\icon.ico" # Asegúrate de tener un icono ahí 
$WshShell = New-Object -ComObject WScript.Shell 
$Shortcut = $WshShell.CreateShortcut($sLinkFile) 
$Shortcut.Description = "RS Engineering Decision Logger"
$Shortcut.TargetPath = $sTargetFile 
$Shortcut.IconLocation = $sIconFile 
$Shortcut.WorkingDirectory = $PSScriptRoot 
$Shortcut.Save()
