@echo off
REM Delete all __pycache__ folders
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo Cleaned up!