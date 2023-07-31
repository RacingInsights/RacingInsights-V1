# Problems

When distributing the .exe to other devices, multiple issues might arise.

- 32 bit cannot run 64
- windows defender blocking
- other antivirus blocking
- some dependencies not available, this is not true if statically linked
  -> Question: is mine statically linked???

This page will serve as a place to gather information on best practices to avoid such issues.

# 1: Make an installer

Guide:
https://learn.microsoft.com/en-us/windows/msix/app-installer/how-to-create-appinstaller-file

Advantages:
[installer advantages list](https://superuser.com/questions/685038/difference-between-a-stand-alone-executable-file-and-an-installed-executable)

TL:DR ->

- File size
- User convenience
- Compatibility (conflicts, dependencies)
- Elevated privileges
- License agreement
- Security (when using shared runtime)
- Registry objects have to be registered
  -> [COM object registration](https://learn.microsoft.com/en-us/windows/security/threat-protection/windows-defender-application-control/allow-com-object-registration-in-windows-defender-application-control-policy)

# 2: Making the application a "trusted application" in Windows
Guide:
https://support.kaspersky.com/KESWin/10SP2/en-US/123510.htm

Info:
https://support.microsoft.com/nl-nl/topic/wat-is-preventie-van-gegevensuitvoering-dep-60dabc2b-90db-45fc-9b18-512419135817

TL:DR ->

Windows DEP (Data Execution Prevention) prevents running applications from locations where they're not supposed to be. There is a list of programs who have received permission.

-> Question: How to get permission for my app (programmatically)? 
- One step seems to be by adding it in the program files folder (this addition requires admin rights)

<div align="center">
  <a href="">
    <img src=".\docs\guides\screenshots\Allow_apps.png" width="400" height="auto">
  </a>
</div>