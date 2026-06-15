# Module 17: Mass Operations

## Learning Objectives

By the end of this module participants can manage many hosts and items at once:
select multiple objects and **mass update** their groups, templates, inventory,
intervals, and status; **clone** hosts and templates to create new ones quickly;
and use **global search** to jump to any object — the skills that keep a growing
Zabbix configuration manageable.

## Topics

### Why mass operations

Day 2 added hosts one at a time. Real estates have *hundreds*. Editing them
individually does not scale and invites mistakes. Zabbix lets you act on **many
objects in one operation** — change a group, link a template, retune an interval,
or disable a noisy check across dozens of hosts at once. As the Online Shop grows
(a web tier of many nodes, a fleet of agents), these are the tools that keep it
sane.

### Select, then act in bulk

Every configuration list (Hosts, Items, Triggers, Templates) has **checkboxes**.
Tick several rows and a **bulk action bar** appears at the bottom — **Enable**,
**Disable**, **Export**, **Mass update**, **Delete** — acting on *all* selected
objects together.

![Three hosts selected; the bulk action bar appears](assets/module-17/01-hosts-selected.png)

### Mass update for hosts

**Mass update** opens a dialog where each field has an **enable checkbox** (it
shows *Original* until you turn it on) — only the fields you tick are changed; the
rest are left as-is. For hosts you can bulk-set:

- **Host groups** — with **Add / Replace / Remove** (move or add many hosts to a
  group at once).
- **Link templates** — **Link / Replace / Unlink** (bulk template linking).
- **Description, Monitored by (server/proxy), Status**, **Tags**, **Macros**, and
  **Inventory** fields (on their tabs).

![Host mass update — each field is opt-in; groups and templates support Add/Replace/Remove](assets/module-17/02-host-massupdate.png)

### Mass update for items (and triggers)

The same pattern works for **items**: select several and mass-change **Type**,
**Update interval**, **History**, **Trends**, **Status** (bulk **enable/disable**),
**Tags**, and preprocessing — ideal for retuning intervals or silencing a check
across many items. **Triggers** have an equivalent mass update (severity,
dependencies, tags, enable/disable).

![Item mass update — retune interval, history, trends, or status for many items at once](assets/module-17/03-item-massupdate.png)

### Cloning hosts and templates

To create a new object *like* an existing one, open it and use **Clone** (copies
the configuration) or **Full clone** (also copies discovered entities). Cloning a
well-built host or template is far faster than starting from scratch — build one
good example, clone it, adjust. The same button exists on templates.

![Clone an existing host to create a new one from it](assets/module-17/04-clone.png)

### Global search

The **search box** at the top-left finds any host, host group, template, or
template group by name and gives quick links straight to its Latest data,
Problems, Items, Triggers, and configuration — the fastest way to jump around a
large estate.

![Global search jumps straight to matching objects](assets/module-17/05-global-search.png)

## Docker-Based Demonstration

The instructor creates a small **web cluster** — `demo-web-01/02/03`, three hosts
representing a scaled-out web tier — then manages them *only* in bulk: select all
three and mass-update their group and templates, mass-disable items, clone one to
make a fourth, and use global search to jump between them. No per-host editing.

## Hands-On Lab

> This lab uses a throwaway `demo-web-01/02/03` cluster so you can practise bulk
> actions without touching the real Online Shop hosts.

1. **Add multiple hosts.** Create three hosts `demo-web-01`, `demo-web-02`,
   `demo-web-03` (a *Web Cluster (demo)* group, no interface, each with an HTTP
   item to `demo-nginx`). *(Tip: build one, then **Clone** it twice — step 5.)*
   **Expected:** three hosts in the new group.

2. **Select them and open the bulk bar.** In **Data collection → Hosts**, filter
   to the *Web Cluster (demo)* group, tick the header checkbox to select all.
   **Expected:** *3 selected* with **Enable / Disable / Export / Mass update /
   Delete** at the bottom.

3. **Move hosts into a group + link a template in bulk.** Click **Mass update**:
   - Enable **Host groups** → **Add** → choose a group.
   - Enable **Link templates** → **Link** → choose a template.

   **Update.**
   **Expected:** all three hosts gain the group and template in one action.

4. **Update host inventory in bulk.** Open **Mass update** again, go to the
   **Inventory** tab, set **Inventory mode = Manual**, and fill a field (e.g.
   *Location* = `Branch DC`). **Update.**
   **Expected:** all three hosts share the inventory value — no per-host typing.

5. **Clone a host.** Open `demo-web-01`, click **Clone**, change the name to
   `demo-web-04`, and **Add**.
   **Expected:** a new host identical to the original (items included), created in
   seconds.

6. **Disable and enable items in bulk.** Open **Items** for `demo-web-01`, select
   several, click **Mass update**, enable **Status → Disabled**, **Update** — then
   repeat with **Enabled** to turn them back on.
   **Expected:** the selected items flip status together.

7. **Use global search.** Type `demo-web` in the top search box.
   **Expected:** all the cluster hosts with quick links to their data and config.

8. **Clean up.** Delete the `demo-web-*` hosts and the demo group.
   **Expected:** the lab returns to the real Online Shop hosts.

## Expected Outcome

Participants can manage Zabbix at scale: bulk-update host groups, templates,
inventory, and status; bulk-retune and enable/disable items (and triggers); clone
hosts and templates to provision quickly; and use global search to navigate a
large configuration — doing in one action what would otherwise be dozens of edits.

## Instructor Notes

- **Lab vs production.** The mechanics are identical at any scale; in production
  you mass-update *hundreds* of hosts — which is exactly why "Replace" vs "Add" on
  groups/templates matters (Replace **removes** existing links). Stress reading the
  Add/Replace/Remove choice before clicking Update.
- **Opt-in fields prevent accidents.** In mass update, untouched fields stay
  *Original*. Make students enable **only** what they intend to change — a common
  mistake is enabling a field and leaving it blank, wiping it on every selected
  object.
- **Clone vs Full clone.** Clone copies the host's own config; **Full clone** also
  duplicates entities created by low-level discovery (Module 23). Use Full clone
  when the source has LLD-generated items you want to keep.
- **Templates are the *better* bulk tool.** Mass update is great for one-off
  changes, but the durable way to manage many hosts identically is a **template**
  (Module 18): change the template once, every linked host updates. Frame mass
  update as the quick fix and templates as the design.
- **Global search scope.** It matches hosts, host groups, templates, and template
  groups by name — not items or triggers. For those, filter within their list.
- **Timing (~45 min).** ~10 min why + select/bulk-bar, ~15 min host mass update
  (groups/templates/inventory), ~10 min item mass update + clone, ~5 min global
  search, ~5 min recap (Add vs Replace, templates as the real answer).

## Lab-State Delta

Module 17 is a **mechanism** module. It temporarily created a *Web Cluster (demo)*
group and hosts `demo-web-01/02/03` (with HTTP items) to practise bulk actions,
then **removed them all** — the reference lab is unchanged (5 hosts: Zabbix server,
zabbix-agent-basic, zabbix-agent2-docker, demo-api, demo-nginx). No permanent
configuration was added. Screenshots in `content/day-3/assets/module-17/`.
