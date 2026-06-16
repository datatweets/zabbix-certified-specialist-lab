#!/usr/bin/env python3
"""
Zabbix API automation demo (Module 36).

A minimal, dependency-free Python client for the Zabbix 7.4 JSON-RPC API.
It authenticates with an API token (Bearer header), then performs the common
read/write operations: list hosts, read current problems, and create a host.

Usage:
    export ZBX_URL="http://localhost:8080/api_jsonrpc.php"
    export ZBX_TOKEN="<your API token from Users -> API tokens>"
    python3 zbx_automation.py
"""
import json
import os
import urllib.request

ZBX_URL = os.environ.get("ZBX_URL", "http://localhost:8080/api_jsonrpc.php")
ZBX_TOKEN = os.environ["ZBX_TOKEN"]  # API token (Users -> API tokens)


def call(method, params=None):
    """One JSON-RPC call. Auth is the Bearer header (7.4); never the body 'auth'.

    apiinfo.version is special: it must be called WITHOUT an authorization header.
    """
    payload = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": 1}
    headers = {"Content-Type": "application/json-rpc"}
    if method != "apiinfo.version":
        headers["Authorization"] = f"Bearer {ZBX_TOKEN}"
    req = urllib.request.Request(ZBX_URL, data=json.dumps(payload).encode(), headers=headers)
    resp = json.load(urllib.request.urlopen(req))
    if "error" in resp:
        raise RuntimeError(resp["error"]["data"])
    return resp["result"]


def main():
    # 1) Who are we talking to?
    print("API version:", call("apiinfo.version"))

    # 2) Read: list the hosts
    hosts = call("host.get", {"output": ["hostid", "host"], "sortfield": "host"})
    print(f"\nHosts ({len(hosts)}):")
    for h in hosts:
        print(f"  {h['hostid']:>6}  {h['host']}")

    # 3) Read: current problems
    problems = call("problem.get", {"output": ["name", "severity"], "limit": 10})
    print(f"\nCurrent problems ({len(problems)}):")
    for p in problems:
        print(f"  [{p['severity']}] {p['name']}")

    # 4) Write: create a host (idempotent-ish — skip if it exists)
    name = "api-automation-demo"
    existing = call("host.get", {"filter": {"host": [name]}, "output": ["hostid"]})
    if existing:
        hostid = existing[0]["hostid"]
        print(f"\nHost {name} already exists ({hostid}).")
    else:
        res = call("host.create", {
            "host": name,
            "groups": [{"groupid": "23"}],          # Docker Lab
            "interfaces": [{
                "type": 1, "main": 1, "useip": 1,
                "ip": "127.0.0.1", "dns": "", "port": "10050",
            }],
        })
        hostid = res["hostids"][0]
        print(f"\nCreated host {name} -> hostid {hostid}")

    # 5) Read it back to confirm
    check = call("host.get", {"hostids": hostid, "output": ["host", "status"]})
    print("Read back:", check[0])


if __name__ == "__main__":
    main()
