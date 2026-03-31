@echo off
echo ============================================================
echo  CRICKET STRATEGY AI - COMPLETE SETUP AND TRAINING
echo ============================================================
echo.

echo STEP 1 - Creating Python 3.11 virtual environment...
py -3.11 -m venv C:\Users\vishal\Desktop\cricket_statergy_ai\venv311
echo Done.
echo.

echo STEP 2 - Installing required packages...
C:\Users\vishal\Desktop\cricket_statergy_ai\venv311\Scripts\pip.exe install pandas numpy scikit-learn joblib --quiet
echo Done.
echo.

echo STEP 3 - Running ML training...
echo Please wait 3-5 minutes. DO NOT press any keys.
echo.
C:\Users\vishal\Desktop\cricket_statergy_ai\venv311\Scripts\python.exe C:\Users\vishal\Desktop\cricket_statergy_ai\train_model.py
echo.
echo ============================================================
echo  ALL DONE! Press any key to close.
echo ============================================================
pause
