; Speechmatics Batch – Inno Setup script
; Compile with Inno Setup 6+  (https://jrsoftware.org/isinfo.php)

[Setup]
AppName=Speechmatics Batch Transcriber
AppVersion=1.0.0
DefaultDirName={autopf}\SpeechmaticsBatch
DefaultGroupName=Speechmatics Batch
OutputDir=installer
OutputBaseFilename=SpeechmaticsBatchSetup
Compression=lzma2
SolidCompression=yes
DisableProgramGroupPage=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=icon.ico

[Files]
Source: "dist\SpeechmaticsBatch.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\Speechmatics Batch"; Filename: "{app}\SpeechmaticsBatch.exe"
Name: "{userdesktop}\Speechmatics Batch"; Filename: "{app}\SpeechmaticsBatch.exe"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Create a &Desktop shortcut"; Flags: unchecked

[Run]
Filename: "{app}\SpeechmaticsBatch.exe"; Description: "Launch now"; Flags: postinstall nowait skipifsilent