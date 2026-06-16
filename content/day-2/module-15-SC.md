# Module 15: Network Discovery

## Learning Objectives

By the end of this module participants can onboard hosts **automatically** two
ways: server-initiated **network discovery** (scan an IP range, find services,
and act on what is found) and agent-initiated **auto-registration** (active agents
announce themselves with metadata). They can write a discovery rule with checks,
read the discovery status, and build discovery/auto-registration **actions** that
add hosts, place them in groups, and link templates with **zero clicks per host**.

## Topics

### Two ways to add hosts without clicking

Up to now, every host in the Online Shop lab arrived the same way: you opened the
frontend, filled in a form, picked a group, linked a template, and saved. That is
fine when there are five hosts. It stops being fine the moment a real environment
shows up — a data center with two hundred servers, a cloud account that spins
machines up and down by the hour, a branch office full of switches nobody has
inventoried. Adding hosts by hand does not scale. The labor grows linearly with
the fleet, and worse, it grows with the *churn* of the fleet, so the bigger and
more dynamic your environment, the more of your week disappears into a host
creation form.

Zabbix solves this by automating onboarding from both directions at once:

| | **Network discovery** | **Auto-registration** |
|---|---|---|
| Who starts it | the **server** (or a proxy) scans | the **active agent** connects in |
| How it finds hosts | probes an **IP range** for services | the agent **announces itself** |
| You configure | a **discovery rule** + discovery action | an agent with metadata + an autoreg action |
| Best for | sweeping a known network/subnet | hosts that come and go (cloud, autoscaling) |

The two approaches mirror each other. In network discovery the server is the
active party: it reaches out across a range of addresses and knocks on doors,
asking each one "is there a service here?" In auto-registration the host is the
active party: an agent boots up, dials home, and says "here I am, and here is what
I am." Read the table as a single idea seen from two ends of the same connection.
Either way, the hard work — naming the host, grouping it, attaching the right
template so it starts collecting data immediately — happens without a human
touching a form. Both end the same way: an **action** decides what to do with each
new host.

### Network discovery rules

Start with the server-initiated path, because it maps so cleanly onto the lab.
Our entire Online Shop lives inside one Docker network, and that network is, for
all practical purposes, a small subnet waiting to be scanned. A **discovery rule**
(Data collection → Discovery) is where you tell Zabbix **what to scan and how**:

- **IP range** — e.g. `172.24.0.1-30` (single IPs, ranges, or CIDR).
- **Checks** — one or more probes per IP: **Zabbix agent** (a key like
  `agent.hostname`), **SNMP**, **HTTP/HTTPS**, **TCP**, **ICMP ping**, SSH, etc.
  Each check is a "is this service here?" test.
- **Update interval** — how often to re-scan.
- **Device uniqueness** and **host naming** — whether a discovered device is keyed
  by IP or by an agent value, and what the created host is named (DNS, IP, or an
  agent value).

The checks are the heart of the rule, so it is worth understanding what they
actually do. Each check is a tiny, targeted probe sent to every address in the
range. A Zabbix agent check asks port `10050` to answer an item key; if it does,
there is a Zabbix agent there. An SNMP check queries an OID; an HTTP check tries to
open a web port; a ping check simply asks whether the address responds at all. You
can stack several checks on one rule, which is how a single sweep can discover
agents, web servers, and network devices in one pass and tell them apart.

The uniqueness and naming settings answer a subtler question that beginners often
trip on: when the scan finds the same machine twice, how does Zabbix know it is the
same machine, and what should the resulting host be called? Keying on IP is the
simple default; keying on an agent-reported value (like the agent's own hostname)
is smarter when addresses might change, and it gives you a host named after the
machine rather than after a number.

![A discovery rule: IP range + a Zabbix agent check](assets/module-15/01-discovery-rule.png)

### Discovery status

A rule is not much use if you cannot see what it is finding, and discovery is the
kind of thing you want to watch unfold rather than trust blindly. While the rule
runs, **Monitoring → Discovery** shows every device found, which **services** are
up/down on it, and for how long. It is the live picture of what the scan sees on
the network — the answer to "did my probes actually reach anything, and what is
alive out there right now?" If you expected ten devices and the screen shows two,
that gap is your first clue that a check is wrong, a port is closed, or the range
is off.

![Status of discovery — devices found by the rule](assets/module-15/02-monitoring-discovery.png)

### Discovery actions: conditions and operations

Here is the crucial separation of concerns: a discovery rule only *finds* things.
It populates that status screen and stops. Finding a device is not the same as
deciding to monitor it — you might discover a printer you have no interest in, or
re-discover a host you already watch. The decision to act lives in a separate
object, a **discovery action** (Alerts → Actions → Discovery actions). If this
feels familiar, it should: it is the same conditions-and-operations machinery you
met with trigger actions back in Module 10, applied to a different kind of event.

- **Conditions** — when to act, e.g. *Discovery status = Up* and/or *Service =
  Zabbix agent*, *Discovery rule = …*, *received value matches …*.
- **Operations** — what to do: **Add host**, **Add to host groups**, **Link
  templates**, enable/disable, set inventory, even run a script.

Think of conditions as the filter that decides *which* discovered devices you care
about, and operations as the recipe applied to the ones that pass. Our action adds
each discovered agent to *Discovered hosts* and links *Linux by Zabbix agent* — so
a freshly discovered machine arrives fully monitored, with CPU, memory, disk, and
the rest already collecting, having never appeared in a manual form.

![Discovery action operations: add host, group, link template](assets/module-15/03-discovery-action.png)

### Auto-registration and agent metadata

Now the other direction. Network discovery assumes you know the addresses to scan,
but plenty of hosts do not sit still long enough to be scanned — a cloud instance
that exists for an hour, a container that scales out under load, a machine whose IP
is assigned by DHCP the moment it boots. For those, you want the host to introduce
itself, and that is exactly what auto-registration does.

The agent-initiated path (introduced in Module 7): an **active** agent with
`ServerActive` set connects to the server and may carry **`HostMetadata`** (a label
describing what it is — e.g. `lab-autoreg`, `web`, `db`). An **autoregistration
action** (Alerts → Actions → Autoregistration actions) matches on that metadata
and runs the same kind of operations — add host, group, link template. The
metadata is the clever part: because the agent tells you what kind of thing it is,
one action can sort incoming hosts intelligently, sending a `web`-tagged agent to
the web template and a `db`-tagged agent to the database template, all without you
ever knowing in advance that those particular machines would exist. This is ideal
for hosts that appear dynamically: each one registers itself the moment its agent
starts.

![The autoregistration action (agent-initiated onboarding)](assets/module-15/05-autoreg-action.png)

## Docker-Based Demonstration

Our Docker network *is* the "small network" to discover, which makes this the rare
case where the lab subnet behaves exactly like a production one. The instructor
creates a discovery rule that scans `172.24.0.1-30` for a **Zabbix agent**, shows
the two agent containers appearing under **Monitoring → Discovery**, then builds a
discovery action that **adds and templates** them automatically — and contrasts it
with the Module 7 **auto-registration** action, where a new agent container
onboards itself.

## Hands-On Lab

1. **Create a discovery rule.** Go to **Data collection → Discovery → Create
   discovery rule**:
   - **Name:** `Docker network — Zabbix agents`
   - **IP range:** `172.24.0.1-30`
   - **Update interval:** `60s`
   - **Checks → Add:** *Zabbix agent*, Key `agent.hostname`, Port `10050`

   The check tells Zabbix to knock on port `10050` at every address in the range
   and ask for `agent.hostname`; any address that answers has a Zabbix agent on it.
   **Add.**
   **Expected:** the rule is saved and starts scanning the range.

2. **Discover the agents.** After a minute, open **Monitoring → Discovery**.
   This is the live picture of the scan — confirmation that your probes reached
   real services rather than empty addresses.
   **Expected:** the rule lists the discovered devices — `172.24.0.9` and
   `172.24.0.13` (the two agent containers) — with the **Zabbix agent** service
   **Up**.

3. **Create a discovery action.** Go to **Alerts → Actions → Discovery actions →
   Create action**:
   - **Name:** `Auto-onboard discovered Zabbix agents`
   - **Conditions:** *Discovery status = Up*
   - **Operations:** **Add host**; **Add to host groups** → *Discovered hosts*;
     **Link templates** → *Linux by Zabbix agent*

   The condition filters the scan down to devices that are actually up; the
   operations are the recipe applied to each one that passes.
   **Add** (and ensure it is **Enabled**).
   **Expected:** the action will fire for each discovered, up agent.

4. **Watch hosts appear — automatically added and templated.** After the next
   discovery cycle, open **Data collection → Hosts** (filter to *Discovered
   hosts*). This is the payoff: hosts created and monitored without anyone opening
   a creation form.
   **Expected:** new hosts (named by IP, `172.24.0.9` / `172.24.0.13`) appear with
   the **Linux by Zabbix agent** template linked and a green **ZBX** — onboarded
   with no manual configuration.

   ![Hosts added and templated automatically by discovery](assets/module-15/04-discovered-hosts.png)

5. **Test auto-registration with a new agent container.** This is the other path
   (Module 7), where the host introduces itself instead of being scanned. With the
   `Lab auto-registration` action in place (metadata contains
   `lab-autoreg`), start a fresh agent that announces itself:
   ```bash
   docker run -d --name demo-newhost --network zabbix-lab \
     -e ZBX_SERVER_HOST=zabbix-server \
     -e ZBX_HOSTNAME=demo-newhost \
     -e ZBX_METADATA=lab-autoreg \
     zabbix/zabbix-agent:alpine-7.4-latest
   ```
   Notice that you never told the server this container's IP; the agent dials home
   on its own and the metadata `lab-autoreg` is what the autoreg action matches on.
   **Expected:** within ~1–2 minutes `demo-newhost` appears in **Data collection →
   Hosts** — added by the *autoregistration* action, not by a scan. The agent
   onboarded **itself**.

6. **Clean up the demo.**
   ```bash
   docker rm -f demo-newhost
   ```
   Then delete the discovered/registered demo hosts you do not want to keep, so the
   lab does not carry forward duplicates of machines it already monitors by name.
   **Expected:** the lab returns to its real hosts.

## Expected Outcome

Participants can build a network discovery rule with checks, read discovery status,
write discovery actions (conditions + operations) that add and template hosts
automatically, and explain and demonstrate agent auto-registration — so onboarding
hundreds of hosts becomes a configuration task, not a clicking task.
