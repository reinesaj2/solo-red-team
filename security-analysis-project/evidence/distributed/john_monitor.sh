#!/bin/bash

# 16-Prong John the Ripper Attack Monitor
# For CS 660 Project 3 - Distributed Offline Password Cracking
# Monitors background John processes without disturbing Hydra attacks

JOHN_LOG="john_monitor.log"
CRACKED_LOG="john_cracked_report.txt"

echo "=== John the Ripper 16-Prong Attack Monitor Started ===" | tee -a $JOHN_LOG
echo "Start Time: $(date)" | tee -a $JOHN_LOG
echo "Monitoring Linux root and Windows 2003 service account attacks..." | tee -a $JOHN_LOG
echo "" | tee -a $JOHN_LOG

while true; do
    echo "=== Status Check at $(date) ===" >> $JOHN_LOG

    # Count active John processes (excluding this monitor)
    JOHN_COUNT=$(ps aux | grep "[j]ohn" | grep -v grep | wc -l)
    echo "Active John processes: $JOHN_COUNT" >> $JOHN_LOG

    # Check for cracked Linux root password (multiple session files)
    ROOT_CRACKED=""
    for session in aa ab ac ad ae af ag ah; do
        ROOT_CHECK=$(john --show --session=john_$session 2>/dev/null | grep -v "0 password" | grep -v "password hash")
        if [ ! -z "$ROOT_CHECK" ]; then
            ROOT_CRACKED="$ROOT_CRACKED $ROOT_CHECK (session: $session)"
        fi
    done
    if [ ! -z "$ROOT_CRACKED" ]; then
        echo "🎉 BREAKTHROUGH: Linux root password cracked!" >> $JOHN_LOG
        echo "ROOT PASSWORD FOUND: $ROOT_CRACKED" >> $CRACKED_LOG
        echo "Discovery time: $(date)" >> $CRACKED_LOG
        echo "---" >> $CRACKED_LOG
    fi

    # Check for cracked Windows 2003 service passwords (multiple session files)
    SERVICE_LM_CRACKED=""
    for session in ai aj ak al am an ao ap; do
        SERVICE_CHECK=$(john --show --format=LM --session=john_$session 2>/dev/null | grep -v "0 password" | grep -v "password hash")
        if [ ! -z "$SERVICE_CHECK" ]; then
            SERVICE_LM_CRACKED="$SERVICE_LM_CRACKED $SERVICE_CHECK (session: $session)"
        fi
    done
    if [ ! -z "$SERVICE_LM_CRACKED" ]; then
        echo "🎉 BREAKTHROUGH: Windows 2003 service LM password(s) cracked!" >> $JOHN_LOG
        echo "SERVICE LM PASSWORDS FOUND: $SERVICE_LM_CRACKED" >> $CRACKED_LOG
        echo "Discovery time: $(date)" >> $CRACKED_LOG
        echo "---" >> $CRACKED_LOG
    fi

    # Count total processes to ensure we're not overloading
    HYDRA_COUNT=$(ps aux | grep "[h]ydra" | wc -l)
    TOTAL_ATTACK_PROCESSES=$((JOHN_COUNT + HYDRA_COUNT))
    echo "Hydra processes: $HYDRA_COUNT, John processes: $JOHN_COUNT, Total: $TOTAL_ATTACK_PROCESSES" >> $JOHN_LOG

    # Check log file sizes to monitor progress
    echo "Recent log activity:" >> $JOHN_LOG
    ls -la john*.16part.*.log 2>/dev/null | tail -3 >> $JOHN_LOG

    echo "" >> $JOHN_LOG

    # Sleep for 60 seconds between checks
    sleep 60
done