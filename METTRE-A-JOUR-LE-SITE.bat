@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Mise a jour du site ghalibensouda.com
echo.
echo   ================================================================
echo      MISE A JOUR DU SITE  -  ghalibensouda.com
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

%PY% "outils\construire.py"
if errorlevel 1 (
  echo.
  echo   ---------------------------------------------------------------
  echo    LA MISE A JOUR A ECHOUE. Le site en ligne n'a pas ete touche.
  echo    Lis le message ci-dessus : il indique le fichier en cause.
  echo   ---------------------------------------------------------------
)
echo.
echo   Etape suivante : ouvre GitHub Desktop, colle le message de commit
echo   ^(Ctrl+V^), clique "Commit to main" puis "Push origin".
echo.
pause
