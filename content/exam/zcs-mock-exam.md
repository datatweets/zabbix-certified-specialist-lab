# Zabbix Certified Specialist — Mock Exam

**Format (matches the real exam):** 45 multiple-choice questions · target **60
minutes** · pass mark **≥ 80 %** (≥ 36 / 45). One correct answer per question.

> The official ZCS exam is based on **Zabbix 7.0 (LTS)**; this course uses **7.4**.
> These questions cover concepts that are **identical in both** versions. Answers and
> explanations are in `zcs-mock-exam-answers.md` — don't peek until you've finished.

Track your time. Flag anything you're unsure of and return to it. Read every option
before choosing.

---

## Section 1 — Architecture & deployment

**1.** Which Zabbix component **stores** all configuration and collected data?
- A) Zabbix server
- B) Zabbix frontend
- C) Zabbix database
- D) Zabbix proxy

**2.** Which TCP port does the Zabbix **server** listen on to receive data from active
agents, proxies, and trappers?
- A) 10050
- B) 10051
- C) 161
- D) 443

**3.** Which component renders dashboards to **PDF** for scheduled reports?
- A) Zabbix proxy
- B) Zabbix Java gateway
- C) Zabbix web service
- D) Zabbix agent 2

**4.** The Zabbix **Java gateway** is required to monitor:
- A) SNMP network devices
- B) JMX-enabled Java applications
- C) ODBC databases
- D) Windows event logs

**5.** In a **Docker Compose** deployment, the frontend, server, and database typically
run as:
- A) A single process
- B) Separate containers on a shared network
- C) One container with three ports
- D) Kernel modules

## Section 2 — Data collection: agents & items

**6.** In a **passive** Zabbix agent check, who initiates the connection?
- A) The agent connects to the server
- B) The server or proxy connects to the agent
- C) The frontend connects to the agent
- D) The database connects to the agent

**7.** For an **active** agent check to work, the agent's `Hostname` parameter must:
- A) Resolve in DNS
- B) Match the host name configured in Zabbix
- C) Be unique on the subnet
- D) Equal the server's hostname

**8.** Which item type **receives** values pushed to the server (e.g. by
`zabbix_sender`)?
- A) Zabbix agent
- B) Zabbix trapper
- C) Simple check
- D) Calculated

**9.** The item key `vfs.fs.size[/,pused]` returns:
- A) Total size of `/` in bytes
- B) Free space on `/` in bytes
- C) Percentage of space **used** on `/`
- D) Number of inodes on `/`

**10.** A **dependent** item obtains its value from:
- A) An SNMP OID
- B) A master item, via preprocessing
- C) The database directly
- D) A user macro

**11.** To collect a metric that **no built-in key provides** (e.g. from a local
script run by the agent), you configure:
- A) A UserParameter
- B) A trapper item
- C) An SNMP trap
- D) A web scenario

**12.** Preprocessing step "**Change per second**" is typically used for:
- A) Text logs
- B) Ever-increasing counters (e.g. network bytes) to get a rate
- C) Encrypting values
- D) Discovering hosts

## Section 3 — Triggers & problems

**13.** Which is the correct **Zabbix 7.x** trigger expression syntax?
- A) `{host:key.last()}>0`
- B) `last(/host/key)>0`
- C) `host.key.last()>0`
- D) `[host:key].last>0`

**14.** A trigger that **depends on** another trigger will:
- A) Fire only if the other also fires
- B) Be **suppressed** while the trigger it depends on is in PROBLEM
- C) Inherit the other trigger's severity
- D) Delete the other trigger's events

**15.** The **recovery expression** of a trigger defines:
- A) When the problem starts
- B) When the problem is considered **resolved**
- C) The notification message
- D) The escalation interval

**16.** `nodata(/host/key,5m)=1` is true when:
- A) The last value equals 5
- B) **No data** has arrived for the item in 5 minutes
- C) Five problems exist
- D) The item is disabled

**17.** Which trigger **severity** is the highest?
- A) High
- B) Average
- C) Warning
- D) Disaster

## Section 4 — Templates & low-level discovery

**18.** **Linking** a template to a host:
- A) Copies items once, then disconnects
- B) Makes the host **inherit** the template's items/triggers, kept in sync
- C) Applies only to hosts created afterward
- D) Requires the API

**19.** When exporting configuration in Zabbix 7.x, the **default** format is:
- A) CSV
- B) YAML
- C) INI
- D) SQL

**20.** On **import**, Zabbix matches existing objects primarily by their:
- A) Name
- B) Numeric ID
- C) **UUID**
- D) Creation date

**21.** A **low-level discovery (LLD)** rule returns:
- A) A single numeric value
- B) **JSON** describing discovered entities with `{#MACRO}` keys
- C) A trigger expression
- D) A PDF report

**22.** In an LLD rule, **item prototypes** use:
- A) Fixed item keys
- B) `{#MACRO}` low-level discovery macros
- C) Only `{$MACRO}` user macros
- D) Only global regular expressions

**23.** An **LLD filter** is used to:
- A) Encrypt discovered data
- B) **Include or exclude** discovered objects by matching a macro against a regex
- C) Set the host's IP
- D) Choose the dashboard layout

## Section 5 — Proxy & distributed monitoring

**24.** A Zabbix **proxy** is used to:
- A) Render PDF reports
- B) **Collect data on behalf of the server** (e.g. remote sites), then forward it
- C) Replace the Zabbix database
- D) Host the frontend

**25.** An **active** proxy:
- A) Waits for the server to connect to it
- B) **Connects to the server** to send collected data
- C) Cannot buffer data when the server is down
- D) Requires the Java gateway

## Section 6 — Actions, alerting & escalation

**26.** The **recommended** way to authenticate to the Zabbix 7.x API is:
- A) The body `auth` field
- B) HTTP header `Authorization: Bearer <token>`
- C) HTTP Basic authentication
- D) A frontend session cookie

**27.** An email **media type** with **no message template** will:
- A) Send a blank email
- B) Fail with "**No message defined for media type**"
- C) Use the operating system's mail
- D) Notify every user

**28.** **Escalation steps** in a trigger action let you:
- A) Change the trigger's severity
- B) **Notify additional people at increasing time intervals** if a problem persists
- C) Suppress recovery messages
- D) Export the configuration

**29.** A **recovery operation** in an action runs when:
- A) The problem first occurs
- B) The problem is **resolved**
- C) The action is saved
- D) A user acknowledges

**30.** A **user's media** entry defines:
- A) The global SMTP server
- B) **Where (address) and when (severity/time)** that user is notified
- C) The trigger expression
- D) The dashboard theme

**31.** To avoid an **alert storm**, a trigger action should be **scoped** by:
- A) Nothing — notify on every problem
- B) **Conditions** such as host group, severity, or tag
- C) The database size
- D) The agent version

## Section 7 — Users, permissions & security

**32.** In Zabbix, permission to **see hosts** is granted:
- A) Per individual user
- B) Through **user groups**, on **host groups**
- C) Only to Super admins
- D) Via templates

**33.** When a user belongs to **several user groups** with different permissions on the
same host group:
- A) The most permissive wins
- B) **Deny always wins**
- C) The newest wins
- D) Read-write always wins

**34.** A **Super admin** role:
- A) Sees only assigned host groups
- B) **Always sees all host groups**, regardless of permissions
- C) Cannot manage users
- D) Cannot call the API

**35.** The two options for **encrypting** agent↔server traffic are:
- A) PSK and certificate (TLS)
- B) SSH and VPN
- C) MD5 and SHA-256
- D) HTTP and HTTPS

**36.** The agent's **`Server`** parameter:
- A) Lists which servers/proxies may query the agent (passive checks)
- B) Sets the database host
- C) Defines the agent `Hostname`
- D) Turns on encryption

## Section 8 — Visualization & reports

**37.** A **map element** linked to a host:
- A) Always shows the same icon
- B) **Changes colour** based on the host's problem status
- C) Cannot be clicked
- D) Requires SNMP

**38.** Which report **ranks the most frequently firing** triggers?
- A) Availability report
- B) **Top 100 triggers**
- C) System information
- D) Audit log

**39.** **Scheduled PDF reports** require:
- A) Only the database
- B) The **Zabbix web service** and a configured **Frontend URL**
- C) An SNMP device
- D) The Java gateway

## Section 9 — Business services & SLA

**40.** In Zabbix 7.x, a **business service** is linked to problems via:
- A) Host IDs
- B) **Tags** (problem tags)
- C) Item keys
- D) IP addresses

**41.** The **SLI** (achieved service availability) is calculated as:
- A) downtime − uptime
- B) **uptime / (uptime + downtime)**
- C) the number of triggers
- D) NVPS × period

**42.** A service whose status calculation rule is "**most critical of child
services**" will:
- A) Always show OK
- B) **Reflect the status of its worst child**
- C) Fail only if all children fail
- D) Ignore its children

## Section 10 — Troubleshooting & operations

**43.** The fastest way to test whether an agent answers a **passive** check is:
- A) Restart the Zabbix server
- B) Run **`zabbix_get -s <host> -k <key>`**
- C) Rebuild the database
- D) Disable the trigger

**44.** **Maintenance** (with data collection) does what to a host's problems during the
window?
- A) Deletes them permanently
- B) **Suppresses** them (hidden unless "show suppressed problems")
- C) Escalates them faster
- D) Exports them to YAML

**45.** An item in the "**Not supported**" state usually means:
- A) The host is in maintenance
- B) **The server cannot collect it** (bad key, missing dependency, or permission)
- C) A trigger has fired
- D) The SLA is breached

---

*End of exam. Mark your answers, then check `zcs-mock-exam-answers.md`. Score ≥ 36 / 45
(80 %) to pass. For every miss, note the topic and revisit the matching module.*
