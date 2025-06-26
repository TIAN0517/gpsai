@echo off
start cmd /k "cd /d %~dp0 & python app.py"
cd gas-ai-frontend
start cmd /k "npm start"
cd .. 