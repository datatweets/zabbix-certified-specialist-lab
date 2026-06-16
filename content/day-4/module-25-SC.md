# Module 25: User Management

## Learning Objectives

By the end of this module participants can control **who sees and changes what** in
Zabbix: explain the **users / user groups / roles** model, create a **custom role**,
grant **host-group permissions** through a user group, create a user, and prove the
result by logging in as that user — applying **least privilege** to the Online Shop
team and understanding where **external authentication** fits.

## Topics

### Why access control matters

Up to this point you have done everything as **Admin**, the account that can reach
every menu, edit every host, and change every setting. That was the right choice
while you were learning, because nothing got in your way. But a real Online Shop is
not run by one person with the keys to everything. Think about the people who
gather around a live monitoring system: an on-call viewer whose job is simply to
glance at the web tier during their shift and escalate if something looks wrong; a
monitoring admin who actually configures hosts and triggers as the shop grows; and
a super admin who manages the platform itself, including the other users. Handing
each of those people the full Admin login would be convenient for about a day and a
liability forever after — one mistyped change, one shared password leaked, one
person who left the company months ago but whose access never got revoked. Zabbix
exists to prevent exactly that, by letting you grant each person precisely the
access their job requires and not one click more. That principle has a name —
**least privilege** — and in this module we build it for the Online Shop.

### The three-part model: users, user groups, roles

Zabbix access control rests on three pieces, and the reason there are three rather
than one is worth understanding before you start clicking, because it is the single
idea that makes everything else fall into place. You need all three:

- A **role** defines *what kind of capabilities* a person has — which UI sections,
  which actions, API access. Every role is based on one of three **user types**:
  **User**, **Admin**, or **Super admin**.
- A **user group** defines *what data* its members can see — **permissions on host
  groups** — plus frontend access and authentication settings.
- A **user** is a person; they are assigned **one role** and belong to **one or more
  user groups**.

The split between role and group is the part that trips people up, so hold onto
this distinction: one of them answers "what is this person allowed to *do*?" and the
other answers "which hosts is this person allowed to *look at*?" Those are genuinely
different questions, and Zabbix keeps them separate on purpose so you can mix and
match — a read-only viewer of the web tier and a read-only viewer of the database
tier share the same role but belong to different groups.

> Capability comes from the **role**; visibility comes from the **user group**. A
> user needs both to be useful.

### User types and roles

Every role inherits from a **user type**, and the user type acts as a ceiling that
no amount of role tweaking can raise. Picking the right type is therefore the first
and most consequential decision you make about an account:

- **User** — sees only **Monitoring**-style views; cannot reach Data collection or
  Administration. The typical *viewer/operator*.
- **Admin** — can configure hosts, items, triggers, templates, and actions for the
  host groups they are permitted, but not manage users or global settings.
- **Super admin** — full control, including users, roles, and authentication; always
  sees **every** host group regardless of permissions.

Within that ceiling, a **role** lets you carve away capabilities you do not want a
particular person to have. Starting from the *User* type — already the most
restricted — you can switch off whole UI sections (Inventory, Reports, Services) and
disable **actions**, leaving a person who can watch the dashboards and the problem
list but cannot so much as acknowledge an event. For the Online Shop's on-call
viewer that is exactly what we want, so we build precisely that role and call it
`Online Shop Viewer`.

![The custom role: User type, Monitoring only, no edit actions](assets/module-25/01-role.png)

### Permissions are granted on host groups, through user groups

Capability tells Zabbix what a person may do; it says nothing about *where*. That
"where" is the job of permissions, and the model has one humane default worth
appreciating: a user starts out **denied everything**. Visibility is something you
hand out deliberately, never something a new account stumbles into. Members gain
sight of hosts only where their user group grants it, and grants are expressed per
**host group** at one of three levels:

- **Read** — see the hosts and their data.
- **Read-write** — see and (with an Admin role) configure them.
- **Deny** — explicitly hide them.

Two rules govern how this plays out, and both matter in practice. First,
permissions attach to **host groups**, not individual hosts — so the way you slice
your environment into groups directly shapes what access you can express, which is
one more reason the host-group structure from earlier modules was worth getting
right. Second, when a user belongs to several groups whose permissions overlap,
**Deny always wins**: an explicit Deny anywhere beats a Read or Read-write
everywhere else, which lets you carve a sensitive host out of an otherwise broad
grant. For the Online Shop we keep it simple and give the `Online Shop Viewers`
group **Read** on **Web Services** only — so its members see the web tier and
nothing else.

![The user group grants Read on the Web Services host group](assets/module-25/02-usergroup-permissions.png)

### Frontend access and external authentication

A user group carries one more responsibility beyond host-group permissions: it sets
**Frontend access** (System default / Internal / LDAP / Disabled) and can switch off
login for its members entirely, which is a quick way to suspend a whole team without
deleting their accounts. The authentication method itself — the question of *how*
Zabbix proves a person is who they claim to be — lives one level up, under **Users →
Authentication**:

- **Internal** — Zabbix stores the password (what this lab uses).
- **LDAP / Active Directory** and **SAML (SSO)** — **external authentication**: the
  identity provider verifies the user, while Zabbix still decides *authorization*
  from the user's group and role. This is the production norm so people use their
  corporate accounts and offboarding is centralized.

The division of labor in that second bullet is the part to internalize. Even when a
corporate directory handles the login, Zabbix never gives up control of
*authorization* — it still consults the user's group and role to decide what they
can see and do. Authentication answers "is this really Jane?"; authorization answers
"what is Jane allowed to touch?" External providers take over only the first
question. The payoff in a real company is large: people sign in with the same
account they use for email, and when someone leaves, disabling that one central
account locks them out of Zabbix too, with no separate cleanup to forget.

> **TO-VERIFY / concept only:** real LDAP/SAML needs an external identity provider,
> which this Docker lab does not include. We teach the concept and where to configure
> it; the lab uses Internal authentication.

### A user, assembled

With the pieces defined, assembling an actual account is almost anticlimactic, which
is the whole point — the design did the hard thinking so the creation is mechanical.
The user `shop.viewer` ties it together: the `Online Shop Viewer` role (capability)
plus the `Online Shop Viewers` group (visibility).

![The user shop.viewer: assigned to the Online Shop Viewers group](assets/module-25/03-user.png)

## Docker-Based Demonstration

The instructor creates the read-only role, creates a user group with Read on Web
Services, creates the `shop.viewer` user, then **logs in as that user** in a private
window to show the effect: a trimmed menu and only the Online Shop's web hosts —
the proof that the permission model works.

## Hands-On Lab

1. **Create a read-only role.** **Users → User roles → Create user role**: Name
   `Online Shop Viewer`, **User type** `User`. Under *Access to UI elements* leave
   **Monitoring** and **Dashboards** checked but **uncheck** Inventory, Reports, and
   Services; set *Access to actions* off (read-only). **Add.**
   **Expected:** the role is saved with User type and a Monitoring-only UI.

2. **Create a user group with host-group permissions.** **Users → User groups →
   Create user group**: Name `Online Shop Viewers`. On the **Host permissions** tab,
   add host group **Web Services** with permission **Read**. **Add.**
   **Expected:** the group lists `Web Services: Read`.

3. **Create the user.** **Users → Users → Create user**: Username `shop.viewer`,
   Name/Last name as you like, **Groups** = `Online Shop Viewers`, set a strong
   password `<StrongPassw0rd!>` (it must not contain the name or username), and on
   the **Permissions** tab set **Role** = `Online Shop Viewer`. **Add.**
   **Expected:** the user exists with that role and group.

4. **Verify by logging in as the user.** Open a **private/incognito window**, sign in
   as `shop.viewer`.
   **Expected:** the left menu shows only **Dashboards** and **Monitoring** — no Data
   collection, Alerts, Users, Administration, Inventory, Reports, or Services.

5. **Confirm the data scope.** As `shop.viewer`, open **Monitoring → Hosts**.
   **Expected:** only **demo-api** and **demo-nginx** (the Web Services group) appear
   — every other host (database, SNMP, Java) is hidden. The viewer cannot
   acknowledge or edit anything (read-only).

   ![Logged in as shop.viewer: trimmed menu, only Web Services hosts](assets/module-25/04-viewer-scope.png)

6. **Look at where external auth lives (concept).** Back as Admin, open **Users →
   Authentication**.
   **Expected:** tabs for **LDAP** and **SAML** — the place you would point Zabbix at
   a corporate directory in production. Leave it on the default for the lab.

## Expected Outcome

Participants have a working least-privilege setup for the Online Shop: a read-only
role, a user group scoped to the web tier, and a user who — when logged in — sees
only what they should. They can explain user types, the role-vs-group split,
host-group permission levels, the Deny precedence rule, and the role of external
authentication.
