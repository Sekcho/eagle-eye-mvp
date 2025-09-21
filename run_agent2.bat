@echo off
echo ========================================
echo Eagle Eye - Agent 2 Batch Processor
echo ========================================
echo.
echo This will find 7-Eleven POI for all villages in Google Sheets
echo.

:menu
echo Choose an option:
echo 1. Test mode (5 villages only)
echo 2. Process 50 villages
echo 3. Process all villages
echo 4. Custom number of villages
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running test mode - 5 villages only...
    python scripts\agent2_batch_processor.py --test
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Processing 50 villages...
    python scripts\agent2_batch_processor.py --max 50
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Processing ALL villages (this may take hours)...
    python scripts\agent2_batch_processor.py
    goto end
)

if "%choice%"=="4" (
    echo.
    set /p custom="Enter number of villages to process: "
    echo Processing %custom% villages...
    python scripts\agent2_batch_processor.py --max %custom%
    goto end
)

if "%choice%"=="5" (
    echo Goodbye!
    goto end
)

echo Invalid choice. Please try again.
echo.
goto menu

:end
echo.
echo Press any key to exit...
pause > nul