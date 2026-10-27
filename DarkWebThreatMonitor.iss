#define MyAppName "DarkWeb Threat Monitoring System"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Anubhav Sharma and Anish Kumar"
#define MyAppExeName "DarkWebThreatMonitor.exe"

[Setup]
AppId={{A7D5B1F0-3C62-4C17-9E11-1A6EBD12F590}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\DarkWebThreatMonitor
DefaultGroupName={#MyAppName}
OutputDir=.
OutputBaseFilename=DarkWebThreatMonitor_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\DarkWebThreatMonitor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: postinstall nowait skipifsilent
