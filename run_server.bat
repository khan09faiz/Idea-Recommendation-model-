@echo off
cd /d "C:\Users\hp\OneDrive\Desktop\recomendation\Idea-Recommendation-model-"
echo Starting Creative Idea Recommendation System...
echo Server will be available at: http://127.0.0.1:8001
echo API documentation at: http://127.0.0.1:8001/docs
echo Press Ctrl+C to stop the server
echo.
"C:\Users\hp\OneDrive\Desktop\recomendation\.venv\Scripts\python.exe" start_server.py
pause
