@echo off
echo ==============================================
echo Running Reddit Scraper Automation...
echo ==============================================
python execution\scrape_reddit.py

echo.
echo ==============================================
echo Generating Dashboard and Logs...
echo ==============================================
python execution\generate_dashboard.py
python execution\generate_log_viewer.py

echo.
echo Opening Dashboard...
start reddit_dashboard.html

echo Done!
pause
