# Module 36: Zabbix API and Automation

## Learning Objectives

By the end of this module participants can drive Zabbix from code: explain the
**JSON-RPC API** and **token authentication**, call it with **curl** and **Python**,
perform the common operations (**list hosts**, **read problems**, **create/update a
host**, **export configuration**), and write a small **automation script** —
understanding where the API fits in real operations and third-party integration.

## Topics

### What is the Zabbix API?

Everything you have done by clicking — hosts, items, triggers, services, users — is
also available through the **API**. It is a single HTTP endpoint,
**`/api_jsonrpc.php`**, speaking **JSON-RPC 2.0**: you POST a JSON request naming a
**method** and its **params**, and get a JSON **result** back. The frontend itself
uses this API, so anything the UI can do, your scripts can do — which is the
foundation of automating Zabbix.

### The JSON-RPC request

Every call has the same shape:

```json
{
  "jsonrpc": "2.0",
  "method": "host.get",
  "params": { "output": ["hostid", "host"] },
  "id": 1
}
```

- **`method`** — `<object>.<action>`, e.g. `host.get`, `trigger.create`,
  `problem.get`.
- **`params`** — the arguments (filters for reads, fields for writes).
- **`id`** — any number you choose; echoed back so you can match responses.

The reply is `{"jsonrpc":"2.0","result": …,"id":1}` on success or
`{… "error": {…}}` on failure.

### Authentication: API tokens

In Zabbix 7.4 you authenticate with an **API token** sent in the HTTP header
**`Authorization: Bearer <token>`** — *not* the deprecated `auth` field in the body.
Create one under **Users → API tokens → Create API token**: give it a name and a
user; it inherits **that user's permissions** (Module 25), so a token for a limited
user can only do what that user can.

![Creating an API token — name, user, optional expiry](assets/module-36/01-api-token-create.png)

The token's secret is shown **once** at creation — copy it then; you cannot see it
again (only revoke and regenerate). Tokens are listed, auditable, and revocable.

![The API tokens list — auditable and revocable](assets/module-36/02-api-token-list.png)

> **One special case:** `apiinfo.version` must be called **without** the
> authorization header — it's the only method that takes no auth.

### Calling the API with curl

The smallest possible call (no auth) — the version:

```bash
curl -s -X POST -H 'Content-Type: application/json-rpc' \
  -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}' \
  http://localhost:8080/api_jsonrpc.php
# {"jsonrpc":"2.0","result":"7.4.11","id":1}
```

With a token, read the hosts:

```bash
TOKEN=<your API token>
curl -s -X POST -H 'Content-Type: application/json-rpc' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid","host"]},"id":1}' \
  http://localhost:8080/api_jsonrpc.php
```

### Common operations

The method pattern is `<object>.<action>` with `get / create / update / delete`:

| Task | Method | Notes |
|---|---|---|
| List hosts | `host.get` | filter with `output`, `groupids`, `filter`, `search` |
| Read current problems | `problem.get` | live problems; `event.get` for history |
| Create a host | `host.create` | needs `groups` and (for agent) `interfaces` |
| Update a host | `host.update` | by `hostid`; e.g. add tags, change name |
| Export config | `configuration.export` | YAML/XML/JSON for a template or host (Module 29) |

### Automating with Python

`curl` is fine for one-offs; real automation uses a script. The committed example
`content/lab/api/zbx_automation.py` is a dependency-free Python client that
authenticates with a token, lists hosts, reads problems, and **creates a host** — its
output against the lab:

```text
API version: 7.4.11

Hosts (8):
   10084  Zabbix server
   10783  demo-api
   ...
Current problems (2):
  [3] Linux: Zabbix agent is not available (for 3m)
  [4] ERROR in Online Shop app log

Created host api-automation-demo -> hostid 10798
Read back: {'hostid': '10798', 'host': 'api-automation-demo', 'status': '0'}
```

The host it creates appears immediately in the UI — a host built entirely from code:

![The script-created host live in Data collection → Hosts](assets/module-36/03-script-host.png)

### Automation use cases and integration

The API is how Zabbix fits into a larger toolchain:

- **Bulk and self-service provisioning** — create hundreds of hosts from a CSV or a
  CMDB; let teams onboard services via a form instead of a ticket.
- **Configuration as code** — `configuration.export` templates into git (Module 29),
  import them via API in CI.
- **Integration with third-party tools** — push problems into **ticketing**
  (Jira/ServiceNow), **ChatOps** (Slack/Teams), or pull data into **Grafana** and
  data warehouses. Webhook media types (Module 27) are the *outbound* path; the API
  is the *inbound/management* path.

## Docker-Based Demonstration

The instructor creates an API token, calls the API with **curl** (`apiinfo.version`,
`host.get`, `problem.get`), then runs the **Python** script to list hosts, read
problems, and create a host — showing it appear in the UI — and finishes with a
`host.update` and a `configuration.export`.

## Hands-On Lab

1. **Create an API token.** **Users → API tokens → Create API token**: name it,
   assign your user, leave expiry off for the lab, **Add**, and **copy the token now**
   (it is shown once).
   **Expected:** the token is listed and Enabled.

2. **Authenticate and check the version.** From a terminal:
   ```bash
   curl -s -X POST -H 'Content-Type: application/json-rpc' \
     -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}' \
     http://localhost:8080/api_jsonrpc.php
   ```
   **Expected:** `"result":"7.4.11"` (no auth header needed for this method).

3. **Get the host list.** Call `host.get` with your token in the `Authorization:
   Bearer` header.
   **Expected:** the lab's 8 hosts with their ids.

4. **Get current problems.** Call `problem.get`.
   **Expected:** the live problems (e.g. the recurring log ERROR).

5. **Create / update a host.** Run the script
   `content/lab/api/zbx_automation.py` (set `ZBX_URL` and `ZBX_TOKEN` first), or call
   `host.create` directly. Then `host.update` to add a tag.
   **Expected:** `api-automation-demo` appears in **Data collection → Hosts**;
   the tag is set.

6. **Export a host's config.** Call `configuration.export` with
   `{"options":{"hosts":["<hostid>"]}}`.
   **Expected:** YAML for that host — config-as-code from the API.

7. **Write/extend a Python script.** Read
   `content/lab/api/zbx_automation.py`, then modify it (e.g. print only Web Services
   hosts, or create a host from variables).
   **Expected:** a working script you understand end to end.

## Expected Outcome

Participants can authenticate to the Zabbix API with a token, perform read and write
operations from curl and Python, automate host management and configuration export,
and explain how the API integrates Zabbix with the wider toolchain — the foundation
of operating Zabbix at scale.

## Instructor Notes

- **Lab vs production.** We hit a local endpoint over HTTP with an Admin-scoped token;
  in production use **HTTPS**, a **least-privilege** token (a dedicated automation
  user with only the needed permissions, Module 25), short **expiry**, and store the
  secret in a vault — never in the script or git.
- **Bearer header, not body `auth`.** This is the single most common 7.x mistake.
  `Authorization: Bearer <token>` is correct; the old body `auth` field is deprecated.
  Show both so students recognise old docs.
- **`apiinfo.version` is the odd one out** — no auth header. Every other method needs
  the token. A "must be called without authorization header" error means you sent the
  header where it isn't allowed.
- **Tokens inherit user permissions.** A token is only as powerful as its user. For
  automation, make a **role-scoped service user** and a token for it — don't automate
  as `Admin`. Tokens are listed and **revocable**, so rotate and audit them.
- **The API mirrors the UI exactly.** If you can do it in the frontend, there is a
  method for it — `host.*`, `item.*`, `trigger.*`, `service.*`, `configuration.*`.
  Teach students to read the 7.4 API reference and map UI fields to params (the same
  1:1 mapping this whole course relied on to verify objects).
- **Idempotency matters in automation.** Our script checks before it creates. Real
  automation must be safe to re-run — use `*.get` to check existence, or rely on
  **UUID-based import** (Module 29) for templates.
- **The API is the integration surface.** Pair *outbound* webhook alerts (Module 27)
  with *inbound* API automation to slot Zabbix into ticketing, ChatOps, and CI/CD.
- **Timing (~45 min).** ~8 min what/why + JSON-RPC, ~8 min tokens + auth, ~12 min curl
  operations (get/create/update/export), ~12 min the Python script + run it, ~5 min
  use cases + integration recap.

## Lab-State Delta

Added in Module 36 (API automation — kept artifact + demonstration):

- **API token:** `automation-demo` (tokenid `1`, user Admin, no expiry, enabled) —
  used to demonstrate **Bearer** authentication. (Secret shown once; not committed.)
- **Committed script:** `content/lab/api/zbx_automation.py` — dependency-free Python
  client (token auth, `host.get`, `problem.get`, `host.create`, read-back). Verified
  against the lab.
- **Verified operations:** `apiinfo.version` (7.4.11), `host.get` (8 hosts),
  `problem.get`, `host.create` (`api-automation-demo` → hostid 10798), `host.update`
  (added tag `managed-by:api`), `configuration.export` (host YAML). The demo host was
  **created then deleted** (demonstrate-then-revert) — lab back to **8 hosts**.
  Screenshots in `content/day-5/assets/module-36/`.
