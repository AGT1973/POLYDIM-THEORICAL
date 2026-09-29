@echo off
REM ============================================================================
REM compilar_tesis.bat — Script de compilación triple para POLYDIM Tesis Doctoral
REM ============================================================================
REM Requisitos:
REM   - MiKTeX o TeX Live instalado (pdflatex, biber disponibles en PATH)
REM   - O instalar MiKTeX desde: https://miktex.org/download
REM
REM Uso: Doble clic sobre este archivo, o desde cmd:
REM   cd E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO\TESIS_DOCTORAL_LATEX
REM   compilar_tesis.bat
REM ============================================================================

SET TESIS_DIR=E:\POLYDIM-THEORICAL\CONSTITUCION_TESIS_MANIFESTO\TESIS_DOCTORAL_LATEX
SET MAIN=main

echo.
echo ===========================================================================
echo  POLYDIM TESIS DOCTORAL — COMPILACION LaTeX TRIPLE
echo  Directorio: %TESIS_DIR%
echo ===========================================================================
echo.

REM Verificar que pdflatex esté disponible
where pdflatex >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pdflatex no encontrado en PATH.
    echo Instalar MiKTeX desde https://miktex.org/download
    echo O agregar la carpeta bin de TeX Live al PATH.
    pause
    exit /b 1
)

REM Verificar que biber esté disponible (para biblatex)
where biber >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ADVERTENCIA] biber no encontrado. La bibliografia puede no compilarse.
    echo Instalar biber con: mpm --install biber
    SET SKIP_BIBER=1
) else (
    SET SKIP_BIBER=0
)

echo [1/4] Primera pasada de pdflatex (genera .aux, .toc, .lof, .lot)...
echo.
pdflatex -interaction=nonstopmode -halt-on-error %MAIN%.tex
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Primera pasada de pdflatex fallo. Verificar errores arriba.
    echo Los errores mas comunes son:
    echo   - Paquete no instalado: usar 'mpm --install nombre_paquete'
    echo   - Error de sintaxis LaTeX en alguno de los .tex
    pause
    exit /b 1
)
echo.
echo [OK] Primera pasada completada.

REM Compilar bibliografía con biber
if %SKIP_BIBER%==0 (
    echo.
    echo [2/4] Compilando bibliografia con biber...
    biber %MAIN%
    if %ERRORLEVEL% NEQ 0 (
        echo [ADVERTENCIA] biber reporto un error. La bibliografia puede estar incompleta.
    ) else (
        echo [OK] Biber completado.
    )
) else (
    echo [2/4] Saltando biber (no disponible)...
)

echo.
echo [3/4] Segunda pasada de pdflatex (resuelve referencias cruzadas)...
pdflatex -interaction=nonstopmode %MAIN%.tex
echo [OK] Segunda pasada completada.

echo.
echo [4/4] Tercera pasada de pdflatex (referencias finales y TOC)...
pdflatex -interaction=nonstopmode %MAIN%.tex
echo [OK] Tercera pasada completada.

echo.
echo ===========================================================================
echo  RESULTADO FINAL:
echo ===========================================================================

if exist %MAIN%.pdf (
    REM Calcular tamaño del PDF
    for %%A in (%MAIN%.pdf) do set SIZE=%%~zA
    echo.
    echo [SUCCESS] PDF generado exitosamente:
    echo   Archivo: %TESIS_DIR%\%MAIN%.pdf
    echo   Tamaño:  %SIZE% bytes
    echo.
    echo Abriendo PDF...
    start "" "%TESIS_DIR%\%MAIN%.pdf"
) else (
    echo.
    echo [FALLO] El PDF no fue generado. Revisar los logs de error arriba.
    echo El archivo de log esta en: %TESIS_DIR%\%MAIN%.log
)

echo.
echo Presione cualquier tecla para cerrar...
pause >nul
