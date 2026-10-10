@echo off
rem Crea dist\MarkItDown.exe (haz doble clic una sola vez; necesita Python instalado)
cd /d "%~dp0"

where py >nul 2>nul && (set PY=py -3) || (set PY=python)

echo [1/3] Preparando entorno...
%PY% -m venv .venv-build || goto :error
call .venv-build\Scripts\activate.bat || goto :error
python -m pip install --upgrade pip >nul

echo [2/3] Instalando dependencias (puede tardar unos minutos)...
pip install -e "packages\markitdown[pdf,docx,pptx,xlsx,xls,outlook,gui]" pyinstaller || goto :error

echo [3/3] Creando el ejecutable...
pyinstaller --noconfirm --onefile --windowed --name MarkItDown ^
  --collect-all magika --collect-all tkinterdnd2 ^
  --collect-all pptx --collect-all mammoth --collect-all pdfminer ^
  --copy-metadata markitdown ^
  packages\markitdown\src\markitdown\_gui_launcher.py || goto :error

echo.
echo Listo: dist\MarkItDown.exe
pause
exit /b 0

:error
echo.
echo Algo fallo. Revisa el mensaje de arriba.
pause
exit /b 1
