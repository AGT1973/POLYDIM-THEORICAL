@echo off
REM ============================================================================
REM INSTALAR_LATEX.bat — Descarga e instala MiKTeX para compilar la tesis
REM ============================================================================
REM MiKTeX es la distribución LaTeX más usada en Windows.
REM Descarga básica: ~260 MB. Paquetes faltantes se instalan al vuelo.
REM ============================================================================

echo.
echo ===========================================================================
echo  INSTALACION DE MiKTeX PARA POLYDIM TESIS DOCTORAL
echo ===========================================================================
echo.
echo Descargando instalador de MiKTeX...
echo Fuente oficial: https://miktex.org/download
echo.

REM Verificar si winget está disponible (Windows 10 1709+)
where winget >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [METODO 1] Instalando con winget (recomendado)...
    winget install MiKTeX.MiKTeX --accept-package-agreements --accept-source-agreements
    echo.
    echo Si el instalador pidio reiniciar, hazlo y luego ejecuta compilar_tesis.bat
    goto :DONE
)

REM Alternativa: descargar con PowerShell
echo [METODO 2] Descargando con PowerShell...
powershell -Command "Invoke-WebRequest -Uri 'https://miktex.org/download/win/miktexsetup-5.5.0+f427b8c2-x64.exe' -OutFile 'miktex_installer.exe'"
if exist miktex_installer.exe (
    echo Ejecutando instalador...
    start /wait miktex_installer.exe --unattended --shared=yes
    del miktex_installer.exe
    echo.
    echo MiKTeX instalado. Ejecuta compilar_tesis.bat para compilar la tesis.
) else (
    echo.
    echo No se pudo descargar automaticamente.
    echo Descargar manualmente desde: https://miktex.org/download
    echo Instalar y luego ejecutar compilar_tesis.bat
)

:DONE
echo.
echo Paquetes adicionales necesarios (se instalan automaticamente con MiKTeX):
echo   - booktabs, longtable, listings, mdframed, pgfplots, biblatex, biber
echo   - physics, epigraph, algorithm2e, cleveref
echo.
pause
