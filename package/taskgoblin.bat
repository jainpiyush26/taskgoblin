@echo off
SET current_directory=%~dp0
SET ver=003
cd %current_directory%
cd ..
python bin/task_goblin.%ver%.py