@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Apercu du site pour une IA
echo.
echo   ================================================================
echo      APERCU DU SITE POUR UNE IA  -  ghalibensouda.com
echo   ================================================================

set PY=
where python >nul 2>&1 && set PY=python
if "%PY%"=="" (where py >nul 2>&1 && set PY=py)
if "%PY%"=="" (
  echo.
  echo   Python n'est pas installe sur cet ordinateur.
  echo   Telecharge-le sur https://www.python.org/downloads/
  echo   ^(coche "Add python.exe to PATH" pendant l'installation^)
  echo.
  pause
  exit /b 1
)

%PY% -c "import PIL" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   Installation de la librairie images ^(une seule fois^)...
  %PY% -m pip install --quiet --disable-pip-version-check Pillow
)

%PY% "outils\apercu-pour-ia.py"
if errorlevel 1 (
  echo.
  echo   ---------------------------------------------------------------
  echo    LA FABRICATION A ECHOUE. Lis le message ci-dessus.
  echo   ---------------------------------------------------------------
)
echo.
pause
