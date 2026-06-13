#!/bin/sh
# Continuously append realistic Online Shop log lines. Mostly INFO, an occasional
# WARNING, and a rare ERROR so log triggers (Module 19) have something to catch.
LOG_DIR=/var/log/demo
LOG_FILE="$LOG_DIR/app.log"
mkdir -p "$LOG_DIR"

i=0
while true; do
  i=$((i + 1))
  ts=$(date '+%Y-%m-%d %H:%M:%S')
  case $((i % 15)) in
    7)  echo "$ts WARNING Slow request detected (latency=820ms) endpoint=/checkout" >> "$LOG_FILE" ;;
    13) echo "$ts ERROR Database connection failed: timeout after 5000ms" >> "$LOG_FILE" ;;
    *)  echo "$ts INFO Request handled endpoint=/products status=200" >> "$LOG_FILE" ;;
  esac
  sleep 5
done
