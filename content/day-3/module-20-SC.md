# Module 20: SNMP Monitoring

## Learning Objectives

By the end of this module you will be able to monitor a device over **SNMP** from
start to finish. You will be able to explain what SNMP is and the small vocabulary
that comes with it — OIDs, MIBs, versions, and community strings — well enough to
talk about it without hand-waving. You will test an SNMP device straight from the
command line, add it to Zabbix as an **SNMP host** carrying an SNMP interface,
collect real metrics by **OID**, and **troubleshoot** the single most common SNMP
failure you will ever meet in the field: a wrong community string.

## Topics

### What is SNMP, and why it matters

So far in the Online Shop we have leaned heavily on the Zabbix agent — a piece of
software we install on a host and ask to report back. That works beautifully for
servers we control. But a great deal of the infrastructure that keeps an online
business running is hardware you *cannot* install software on: the router that
carries traffic to the shop, the switch the servers plug into, the firewall in
front of them, the printer in the back office, the UPS keeping the rack alive, the
storage array holding the database. None of these will run a Zabbix agent. They
need a different door.

**SNMP** (Simple Network Management Protocol) is that door. It is how you monitor
devices that **cannot run a Zabbix agent** — routers, switches, firewalls,
printers, UPSs, storage arrays. The device runs an **SNMP agent** that answers
queries on **UDP 161**; Zabbix (the *manager*) asks it for values. Think of it as a
polite question-and-answer protocol: the device sits there with a catalog of facts
about itself, and the manager walks up and asks, "What's your name? How long have
you been up? How many network interfaces do you have?" In our lab,
`demo-snmp-device` runs net-snmp and stands in for a network device — so you learn
SNMP without a physical router.

### OIDs and MIBs

If SNMP is a question-and-answer protocol, you need a precise way to name the thing
you are asking about — and "the device's name" is far too vague for a machine.
Every value an SNMP device exposes has an **OID** (Object Identifier) — a
dotted-number address in a global tree, e.g.:

- `1.3.6.1.2.1.1.5.0` — **sysName** (the device's name)
- `1.3.6.1.2.1.1.1.0` — **sysDescr** (description)
- `1.3.6.1.2.1.1.3.0` — **sysUpTime**
- `1.3.6.1.2.1.2.1.0` — **ifNumber** (number of interfaces)

Read an OID the way you read a postal address from country down to house number:
each number narrows you down a branch of one enormous, globally agreed tree until
you arrive at exactly one value. That is what makes SNMP interoperable — a Cisco
switch and a Juniper router both publish their name at the same address, because
the address is standardized rather than invented per vendor.

Memorizing dotted numbers, of course, is no way to live. A **MIB** (Management
Information Base) is a dictionary that maps human names (`sysName`) to OIDs — so
you can write `SNMPv2-MIB::sysName.0` instead of the numbers. Zabbix ships common
MIBs; vendors provide device-specific ones. When you load the MIB for a particular
device family, the friendly names for its proprietary metrics become available
too, which is how monitoring tools can show you "Power Supply 1 Temperature"
instead of a wall of digits.

### SNMP versions and the community string

SNMP has evolved over the years, and the version you choose determines how the
device decides whether to trust the question it just received:

- **v1 / v2c** — simple; authentication is just a **community string** (a shared
  password, commonly `public` for read-only). v2c adds bulk requests for
  efficiency.
- **v3** — adds real authentication and encryption (user/password/privacy);
  preferred in production.

The community string deserves a moment of honesty: it is barely a password. It
travels in clear text and is often left at the factory default of `public`, which
is precisely why SNMPv3 exists. For a teaching lab on a private Docker network,
v2c is perfect — it strips the protocol down to its essentials so you can see the
mechanics clearly. Our device uses **v2c** with community **`public`**.

### SNMP interfaces in Zabbix

In Zabbix, a host talks to the outside world through *interfaces*, and the
interface type tells the server which protocol to speak. An agent host carries an
agent interface; an SNMP host carries something different. An SNMP host carries an
**SNMP interface** (not an agent interface): its address, **port 161**, the **SNMP
version**, and the **community** — which we store in a macro
**`{$SNMP_COMMUNITY}`** so it can differ per host and stay out of every item. That
last point is the one to internalize: by parking the community in a single macro
rather than copying it into each item, you give yourself one place to change when
the secret rotates, and you keep the password from being smeared across dozens of
item definitions.

![The SNMP interface: SNMPv2, community {$SNMP_COMMUNITY}, port 161](assets/module-20/01-snmp-host.png)

### SNMP items, templates

With the interface in place, each value you want becomes an item. An **SNMP item**
is type **SNMP agent**, attached to the SNMP interface, with the **SNMP OID** to
read. You can write items by OID directly (as we do), or — the usual production
path — **link a vendor SNMP template** (Zabbix ships *Generic by SNMP*, *Cisco IOS
by SNMP*, and hundreds more) that already contains the right OIDs and low-level
discovery for that device family. Hand-writing OIDs is the right way to *learn*
what the template is doing under the hood; once you understand that, the template
is the right way to *work*, because someone has already done the tedious job of
cataloging every OID a Cisco router exposes.

![An SNMP item reads a single OID](assets/module-20/02-snmp-item.png)

### Network device monitoring

Step back and notice what you are actually collecting. The values — interface
counters, CPU, memory, temperature, uptime — are exactly what you watch on real
switches and routers. There is nothing toy about them; the same OIDs you read off
`demo-snmp-device` are the ones a network engineer watches on production gear at
3 a.m. when traffic spikes. And the payoff scales: SNMP + low-level discovery
(Module 23) auto-creates an item per interface, so a 48-port switch monitors itself
once the template is linked. You do not define forty-eight items by hand; you link
one template and Zabbix discovers the ports.

## Docker-Based Demonstration

`demo-snmp-device` is already running net-snmp. The instructor tests it from the
command line, adds it as an SNMP host with a v2c interface, creates a few OID
items, shows them collecting in Latest data, then **breaks the community string**
and uses the item **Test** to diagnose the timeout. That last move is the heart of
the demonstration: you do not just configure SNMP, you watch it fail the way it
fails in real life and learn to read the symptom.

## Hands-On Lab

1. **Test SNMP from the command line.** Before involving Zabbix, prove the device
   answers (run from the device's own net-snmp tools):
   ```bash
   docker exec demo-snmp-device snmpget -v2c -c public localhost 1.3.6.1.2.1.1.5.0
   # -> SNMPv2-MIB::sysName.0 = STRING: demo-snmp-device
   docker exec demo-snmp-device snmpwalk -v2c -c public localhost 1.3.6.1.2.1.1
   ```
   This is the same discipline you used with `zabbix_get` for agents: prove the
   target works on its own terms before blaming the monitoring layer.
   **Expected:** the system subtree (sysName, sysDescr, sysUpTime, …). If this
   works, the device and community are correct.

2. **Add the SNMP host.** In **Data collection → Hosts → Create host**, set name
   `demo-snmp-device`, group `Network Devices`, add a macro
   `{$SNMP_COMMUNITY}` = `public`, and add an **SNMP interface**: DNS
   `demo-snmp-device`, port `161`, **SNMP version SNMPv2**, **SNMP community**
   `{$SNMP_COMMUNITY}`. Notice the community field points at the macro, not the
   literal string — that indirection is what we set up earlier.
   **Expected:** the host has one SNMP interface.

3. **Add SNMP items by OID.** Create items (Type **SNMP agent**, on the SNMP
   interface). An SNMP item still needs a **unique key** — any short name — plus
   the OID:

   | Name | Key | SNMP OID |
   | --- | --- | --- |
   | `System name (sysName)` | `snmp.sysname` | `1.3.6.1.2.1.1.5.0` |
   | `System description (sysDescr)` | `snmp.sysdescr` | `1.3.6.1.2.1.1.1.0` |
   | `Uptime (sysUpTime)` | `snmp.uptime` | `1.3.6.1.2.1.1.3.0` |
   | `Number of interfaces (ifNumber)` | `snmp.ifnumber` | `1.3.6.1.2.1.2.1.0` |

   **Expected:** four SNMP items. The **key is just a local identifier** in Zabbix
   — the **OID** is what's fetched from the device.

4. **Collect SNMP metrics.** Go to **Monitoring → Latest data**, filter to
   `demo-snmp-device`.
   **Expected:** the OID values arrive — `sysName` = `demo-snmp-device`,
   `ifNumber` = a number, `sysUpTime` climbing. You are monitoring a "network
   device" entirely over SNMP.

   ![SNMP metrics collected by OID](assets/module-20/03-latest-data.png)

5. **Break the community string.** Change the host macro `{$SNMP_COMMUNITY}` to
   `wrongcommunity` and save. We are deliberately staging the most common SNMP
   failure so you recognize it instantly the next time it happens for real.
   **Expected:** within a minute the SNMP items stop updating — the device ignores
   queries with the wrong community.

6. **Troubleshoot.** Open the `System name` item and click **Test → Get value and
   test**.
   **Expected:** a red **`Timeout while connecting to "demo-snmp-device:161"`** —
   and the dialog shows the **SNMP community** in use (`wrongcommunity`). The fix
   is plain: the community is wrong. Confirm from the CLI that `public` works but
   `wrongcommunity` times out, then set the macro back to `public`.

   ![Wrong community → timeout in the item Test](assets/module-20/04-broken.png)

7. **Confirm recovery.** With `{$SNMP_COMMUNITY}` back to `public`, the items
   collect again.
   **Expected:** Latest data resumes.

## Expected Outcome

You can now monitor a device over SNMP end to end: test it from the command line,
configure an SNMP host with the correct version and community, collect metrics by
OID (or via a template), and diagnose the classic wrong-community failure. That is
the foundation of network-device monitoring — and from here, templates and
low-level discovery are simply scale on top of mechanics you already understand.
