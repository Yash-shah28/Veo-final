@echo off
echo Installing Python dependencies...
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
pip install langchain
pip install langchain-google-genai
pip install google-generativeai

echo.
echo Installation complete!
echo.
echo Don't forget to add GEMINI_API_KEY to your .env file!
echo.
pause
