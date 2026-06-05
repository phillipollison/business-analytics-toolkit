#!/bin/bash

PROJECT_DIR="/Users/phillipollison/Desktop/business-analytics-toolkit"
PYTHON_BIN="$PROJECT_DIR/venv/bin/python3"
CONFIG_PATH="automation/configs/config.example.json"
LOG_PATH="logs/automation_cron.log"

if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="/usr/bin/python3"
fi

CRON_LINE="0 8 * * * cd $PROJECT_DIR && $PYTHON_BIN -m automation.run_daily --config $CONFIG_PATH >> $LOG_PATH 2>&1"

echo "Installing Clean0ps daily cron job:"
echo "$CRON_LINE"

( crontab -l 2>/dev/null | grep -v "automation.run_daily --config"; echo "$CRON_LINE" ) | crontab -

echo ""
echo "Cron installed."
echo ""
crontab -l
