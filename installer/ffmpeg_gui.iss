; Skrypt instalatora Inno Setup dla FFmpeg GUI PL.
; Wymaga wcześniejszego uruchomienia: python build_exe.py
; Kompilacja: ISCC.exe installer\ffmpeg_gui.iss

#define MyAppName "FFmpeg GUI PL"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Iwo"
#define MyAppURL "https://github.com/M00r/ffmpeg-gui-pl"
#define MyAppExeName "FFmpegGUI.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=FFmpegGUI-Setup-{#MyAppVersion}
SetupIconFile=..\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
; Domyślnie zaznaczone: utwórz skrót na pulpicie.
Name: "desktopicon"; Description: "Utwórz skrót na pulpicie"; \
    GroupDescription: "Dodatkowe ikony:"; Flags: checkedonce

[Files]
; Główny plik .exe oraz katalog z wtyczkami.
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\plugins\*"; DestDir: "{app}\plugins"; \
    Flags: ignoreversion recursesubdirs

[Icons]
; Skrót w menu Start i opcjonalnie na pulpicie.
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; \
    Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; \
    Description: "Uruchom {#MyAppName}"; Flags: nowait postinstall skipifsilent