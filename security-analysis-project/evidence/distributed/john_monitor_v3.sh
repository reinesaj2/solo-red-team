#!/bin/bash

# Enhanced John the Ripper 16-Prong Attack Monitor v3
# For CS 660 Project 3 - Directory-based Isolated Attack Monitoring
# Monitors both Linux and Windows attacks with comprehensive status tracking

JOHN_LOG="john_monitor_v3.log"
CRACKED_LOG="john_cracked_report_v3.txt"

echo "=== Enhanced John the Ripper 16-Prong Attack Monitor v3 Started ===" | tee -a $JOHN_LOG
echo "Start Time: $(date)" | tee -a $JOHN_LOG
echo "Monitoring Linux root (SHA-512) and Windows LM attacks across 16 partitions..." | tee -a $JOHN_LOG
echo "Directory-based isolation architecture implemented" | tee -a $JOHN_LOG
echo "" | tee -a $JOHN_LOG

while true; do
    echo "=== Status Check at $(date) ===" >> $JOHN_LOG

    # Count active John processes
    LINUX_COUNT=$(ps aux | grep "[j]ohn" | grep "sha512crypt" | wc -l)
    LM_COUNT=$(ps aux | grep "[j]ohn" | grep "LM" | wc -l)
    TOTAL_JOHN=$((LINUX_COUNT + LM_COUNT))
    echo "Active John processes: $TOTAL_JOHN (Linux: $LINUX_COUNT, LM: $LM_COUNT)" >> $JOHN_LOG

    # Check for cracked Linux root passwords (directory-based pot files)
    ROOT_CRACKED=""
    for part in aa ab ac ad ae af ag ah; do
        if [ -f "john_work_$part/john_$part.pot" ]; then
            ROOT_CHECK=$(cat john_work_$part/john_$part.pot 2>/dev/null | grep -v "^$")
            if [ ! -z "$ROOT_CHECK" ]; then
                ROOT_CRACKED="$ROOT_CRACKED $ROOT_CHECK (partition: $part)"
            fi
        fi
    done
    if [ ! -z "$ROOT_CRACKED" ]; then
        echo "🎉 BREAKTHROUGH: Linux root password cracked!" >> $JOHN_LOG
        echo "ROOT PASSWORD FOUND: $ROOT_CRACKED" >> $CRACKED_LOG
        echo "Discovery time: $(date)" >> $CRACKED_LOG
        echo "---" >> $CRACKED_LOG
    fi

    # Check for cracked Windows LM passwords (directory-based pot files)
    LM_CRACKED=""
    for part in ai aj ak al am an ao ap; do
        if [ -f "john_work_$part/john_$part.pot" ]; then
            LM_CHECK=$(cat john_work_$part/john_$part.pot 2>/dev/null | grep -v "^$")
            if [ ! -z "$LM_CHECK" ]; then
                LM_CRACKED="$LM_CRACKED $LM_CHECK (partition: $part)"
            fi
        fi
    done
    if [ ! -z "$LM_CRACKED" ]; then
        echo "🎉 BREAKTHROUGH: Windows LM password(s) cracked!" >> $JOHN_LOG
        echo "LM PASSWORDS FOUND: $LM_CRACKED" >> $CRACKED_LOG
        echo "Discovery time: $(date)" >> $CRACKED_LOG
        echo "---" >> $CRACKED_LOG
    fi

    # Monitor attack progress and status
    echo "Attack Status Summary:" >> $JOHN_LOG
    echo "- Linux SHA-512 attacks (aa-ah): $LINUX_COUNT processes active" >> $JOHN_LOG
    echo "- Windows LM attacks (ai-ap): $LM_COUNT processes active (may have completed)" >> $JOHN_LOG

    # Check pot file sizes for activity indication
    ACTIVE_LINUX=0
    for part in aa ab ac ad ae af ag ah; do
        if [ -f "john_work_$part/john_$part.pot" ]; then
            SIZE=$(stat -c%s john_work_$part/john_$part.pot 2>/dev/null || echo "0")
            if [ "$SIZE" -gt 0 ]; then
                ACTIVE_LINUX=$((ACTIVE_LINUX + 1))
            fi
        fi
    done

    ACTIVE_LM=0
    for part in ai aj ak al am an ao ap; do
        if [ -f "john_work_$part/john_$part.pot" ]; then
            SIZE=$(stat -c%s john_work_$part/john_$part.pot 2>/dev/null || echo "0")
            if [ "$SIZE" -gt 0 ]; then
                ACTIVE_LM=$((ACTIVE_LM + 1))
            fi
        fi
    done

    echo "- Passwords discovered: Linux ($ACTIVE_LINUX/8), LM ($ACTIVE_LM/8)" >> $JOHN_LOG

    # Count total attack processes (including Hydra)
    HYDRA_COUNT=$(ps aux | grep "[h]ydra" | wc -l)
    TOTAL_ATTACK_PROCESSES=$((TOTAL_JOHN + HYDRA_COUNT))
    echo "Process distribution: Hydra: $HYDRA_COUNT, John: $TOTAL_JOHN, Total: $TOTAL_ATTACK_PROCESSES" >> $JOHN_LOG

    # Check recent log activity
    echo "Recent activity check:" >> $JOHN_LOG
    RECENT_LOGS=$(find john_work_* -name "john_*.log" -newermt "1 minute ago" 2>/dev/null | wc -l)
    echo "- Log files updated in last minute: $RECENT_LOGS" >> $JOHN_LOG

    echo "" >> $JOHN_LOG

    # Sleep for 60 seconds between checks
    sleep 60
done