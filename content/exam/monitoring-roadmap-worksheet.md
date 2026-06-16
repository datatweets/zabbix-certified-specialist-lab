# Monitoring Roadmap Worksheet

Use this after the course to plan **what's next** — for your skills and for your
organization's monitoring. Fill in each section; revisit it every quarter.

---

## 1. Where I am now

- **Certification reached:** ☐ ZCU ☐ **ZCS (this course)** ☐ ZCP ☐ ZCE
- **What I can do today** (tick what you've actually done in the lab):
  ☐ deploy with Docker · ☐ agents (active/passive) · ☐ items & preprocessing ·
  ☐ triggers & dependencies · ☐ templates & mass ops · ☐ LLD ·
  ☐ web/log/DB/SNMP/JMX monitoring · ☐ proxy · ☐ alerting & escalation ·
  ☐ users/roles/permissions · ☐ security/maintenance · ☐ dashboards/maps/reports ·
  ☐ business services & SLA · ☐ API/automation · ☐ troubleshooting
- **My weakest areas (from the mock exam / scenarios):** _______________________

## 2. My next certification

| Next | Adds | Prereq | When |
|---|---|---|---|
| **ZCP (Professional)** | install from scratch, **HA** (server + proxy), PSK/cert encryption, advanced preprocessing & LLD, host prototypes, ODBC/SNMP discovery, autoregistration, VMware, **event correlation**, performance tuning | **ZCS** | __________ |
| **ZCE (Expert)** | DB tuning for **tens of thousands of hosts**, near-zero-downtime upgrades, vault credentials (HashiCorp/CyberArk), enterprise auth (**LDAP/SAML/MFA**), TimescaleDB, SELinux | ZCP | __________ |

- **My target:** ____________  **Target date:** ____________

## 3. Advanced topics to learn (check the ones relevant to you)

- ☐ **High availability** — native server HA cluster; proxy HA / load balancing
- ☐ **Large-scale architecture** — many proxies, DB partitioning / **TimescaleDB**,
  tuning `Start*` processes, sizing for NVPS
- ☐ **Cloud monitoring** — AWS/Azure/GCP via HTTP agent + cloud APIs, cloud-native
  metrics, autoscaling-aware discovery
- ☐ **Kubernetes / container monitoring** — the Kubernetes templates, cluster + node +
  pod metrics, service discovery
- ☐ **Network monitoring at scale** — SNMP LLD for switches/routers, network maps,
  traps, flow/latency
- ☐ **Enterprise alerting** — on-call rotation (PagerDuty/Opsgenie), ChatOps
  (Slack/Teams), escalation policies, alert deduplication & correlation
- ☐ **Integrations** — ticketing (Jira/ServiceNow), Grafana, data warehouses, webhooks
- ☐ **Automation & IaC** — templates in **git**, provisioning via the **API**,
  config in CI/CD, vault-managed secrets

## 4. My organization's monitoring needs

- **Systems to monitor** (servers, network, apps, cloud, DBs, k8s): _______________
- **What I monitor today vs. what's missing (gaps):** _______________
- **Who needs to see what** (ops dashboards, management SLA, on-call): _______________
- **SLAs / business services that matter:** _______________

## 5. Architecture plan

- **Single server or HA?** ____________
- **Proxies needed?** (remote sites, scale, security boundaries) ____________
- **Database:** MySQL / PostgreSQL / **+ TimescaleDB**? Retention (history/trends)? ___
- **Estimated scale:** ~______ hosts, ~______ NVPS → sizing implications: ___________
- **Security:** encryption (PSK/cert), LDAP/SAML, vault for secrets, HTTPS frontend ☐

## 6. Automation & IaC plan

- ☐ Templates exported to **git** (config-as-code, reviewed in PRs)
- ☐ Host/onboarding via **API** or **autoregistration**, not by hand
- ☐ Scheduled **configuration.export** backups; DB dump strategy
- ☐ Alerts integrated with ticketing/ChatOps via webhooks
- **My first automation to build:** _______________

## 7. 30 / 90 / 180-day action plan

| Horizon | Goal | Concrete step |
|---|---|---|
| **30 days** | close exam gaps / sit ZCS | _______________ |
| **90 days** | apply at work / start ZCP prep | _______________ |
| **180 days** | a production-grade improvement | _______________ |

## 8. Resources

- **Docs:** zabbix.com/documentation (pin your version) · **Training:**
  zabbix.com/training · **Exams:** zabbix.com/exams
- **Community:** Zabbix blog, forums, Telegram/Slack, local meetups & the annual summit
- **Your lab:** keep this Docker stack — extend it, break it, fix it. Doing keeps skills
  alive.

---

*Monitoring is never "done." Re-run this worksheet each quarter: new systems, new
scale, new gaps — and the next rung on the certification ladder.*
