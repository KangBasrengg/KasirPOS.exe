@echo off
REM ============================================
REM Script untuk build aplikasi client menjadi .exe
REM Jalankan file ini di Command Prompt / double-click
REM di komputer Windows yang sudah install Python
REM ============================================

echo Menginstall dependency...
pip install -r requirements.txt

echo.
echo Membangun file EXE (mungkin perlu beberapa menit)...
pyinstaller --noconfirm --onefile --windowed --name "POS_Kasir" ^
    --hidden-import themes ^
    main.py

echo.
echo ============================================
echo Selesai! File EXE ada di folder: dist\POS_Kasir.exe
echo ============================================
pause
