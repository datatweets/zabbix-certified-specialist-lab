#!/bin/sh
# Online Shop custom metric collector — helper for a Zabbix UserParameter.
# Demonstrates Module 11 (Custom Data Collection): the agent runs this script to
# return a business metric that no built-in template provides.
#
# Usage: online_shop.sh <field>
#   field = orders | failed_payments | queue_length | response_time_ms
#
# It reads the Online Shop API and extracts one numeric field from the JSON.
field="$1"
wget -qO- http://demo-api:5000/metrics 2>/dev/null \
  | grep -oE "\"${field}\":[0-9]+" \
  | grep -oE '[0-9]+'
