ECHO OFF
cls

SET "ProjDir="C:\xCode\AGR Cleanup Tool""
SET "PluginFolder=agr_cleanup_tool"
SET "Cinema4DPluginDir="X:\C4D\plugins\%PluginFolder%""

CD %ProjDir%

RMDIR /S /Q %Cinema4DPluginDir%

MKDIR %Cinema4DPluginDir%
cls

XCOPY /S %PluginFolder% %Cinema4DPluginDir%

ECHO.
ECHO Plugin Pushed.
pause > nul