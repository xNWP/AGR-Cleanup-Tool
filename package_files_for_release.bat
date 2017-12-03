ECHO OFF
CLS

DEL /P *.7z *.zip
CLS

SET "sevzip="C:\Program Files\7-Zip\7z.exe""
SET "version=v1"
SET "filelist=agr_cleanup_tool INSTALLATION.txt"

%sevzip% a -t7z AGR_Cleanup_Tool_%version%.7z %filelist%
%sevzip% a -tzip AGR_Cleanup_Tool_%version%.zip %filelist%

ECHO.
ECHO Packaged.
PAUSE > nul