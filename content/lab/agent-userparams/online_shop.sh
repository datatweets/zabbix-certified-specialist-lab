#!/bin/sh
# Online Shop custom metric collector — helper for a Zabbix UserParameter.
# Demonstrates Module 11 (Custom Data Collection): the agent runs this script to
# return a business metric that no built-in template provides.
#
# Usage: online_shop.sh <field>
#   field = orders | failed_payments | queue_length | response_time_ms
#   field = discovery  -> emits Low-Level Discovery JSON (Module 23)
#
# It reads the Online Shop API and extracts one numeric field from the JSON.
field="$1"

# Module 23 (Low-Level Discovery): a custom LLD rule. Returns the list of Online
# Shop metrics as discoverable objects, so item/trigger prototypes create one
# item per metric automatically (the same app.shop[*] metrics Module 11 added by
# hand). Used as discovery key: app.shop[discovery].
if [ "$field" = "discovery" ]; then
  cat <<'JSON'
[
  {"{#FIELD}":"orders","{#LABEL}":"Total orders"},
  {"{#FIELD}":"queue_length","{#LABEL}":"Queue length"},
  {"{#FIELD}":"failed_payments","{#LABEL}":"Failed payments"},
  {"{#FIELD}":"response_time_ms","{#LABEL}":"API response time"}
]
JSON
  exit 0
fi

wget -qO- http://demo-api:5000/metrics 2>/dev/null \
  | grep -oE "\"${field}\":[0-9]+" \
  | grep -oE '[0-9]+'
