@echo off
echo Starting University Capital Analysis...
echo.

:: Set Python path (update this to your Python path)
set PYTHON_PATH=python

:: Create necessary directories
mkdir "D:\busineshuboffline CHATGTP\KEAN\University\Universitycapital"
mkdir "D:\busineshuboffline CHATGTP\KEAN\University\Universitycapital\analysis"
mkdir "D:\busineshuboffline CHATGTP\KEAN\University\Universitycapital\valuations"
mkdir "D:\busineshuboffline CHATGTP\KEAN\University\Universitycapital\market_analysis"
mkdir "D:\busineshuboffline CHATGTP\KEAN\University\Universitycapital\future_roadmap"

:: Run the analysis
echo Running project analysis...
%PYTHON_PATH% "D:\busineshuboffline CHATGTP\KEAN\University\analyze_project.py"

:: Run the valuation
echo.
echo Generating valuation report...
%PYTHON_PATH% "D:\busineshuboffline CHATGTP\KEAN\University\create_valuation.py"

echo.
echo Analysis complete! Reports have been generated in:
echo D:\busineshuboffline CHATGTP\KEAN\University\Universitycapital
pause
