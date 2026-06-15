# Module 27: Alerting and Notifications

## Learning Objectives

By the end of this module participants can build **end-to-end alerting**: configure
a **media type** (email via the local Mailpit server), attach **media to a user**,
write a **trigger action** with **conditions**, **operations**, **escalation steps**,
and **recovery operations**, then prove it by generating a real problem and receiving
both a **problem** and a **recovery** email.

## Topics

### A trigger firing is not a notification

So far, problems have appeared only in **Monitoring → Problems**. Nobody is told.
Alerting is the bridge from "Zabbix knows" to "a human is notified", and it has a
fixed pipeline you must wire end to end:

```text
trigger fires → event → action (conditions match?) → operation →
   media type (how to send) + user media (where to send) + message template → notification
```

If any link is missing — no media type, no user media, no matching action, no
message template — **nothing is sent**. Most "alerting doesn't work" tickets are one
broken link in this chain.

### Media types — how a message is sent

A **media type** defines the channel. Zabbix ships many: **Email**, and webhook
integrations for **Slack, Microsoft Teams, Discord, Telegram, PagerDuty**, etc. For
the Online Shop we configure **Email** pointing at the lab's local SMTP server,
**demo-mailhog** (Mailpit), so no real mail leaves the lab:

- **SMTP server** `demo-mailhog`, **port** `1025`, no encryption, no auth (lab).
- A **from** address and HELO name.

![The Email media type pointing at the local Mailpit SMTP server](assets/module-27/01-media-type.png)

- **Slack / webhook (concept):** the webhook media types post JSON to a chat
  service's incoming-webhook URL — same pipeline, different media type. No real Slack
  endpoint exists in this lab.
- **SMS (concept):** Zabbix can drive a GSM modem or an SMS-gateway webhook; both
  need external hardware/accounts, so we describe them only.

### Message templates

A media type carries **message templates** — the subject and body per event type
(**Problem**, **Problem recovery**, **Problem update**) — built from **macros** like
`{EVENT.NAME}`, `{HOST.NAME}`, `{EVENT.SEVERITY}`, `{EVENT.DURATION}`. Without a
template for the event type, Zabbix raises *"No message defined for media type"* and
sends nothing — a classic first-time mistake.

### Users and media

A media type is *how*; **user media** is *where*. On a user's **Media** tab you add
an address (`oncall@online-shop.lab`), choose **which severities** trigger it, and a
**time period** when it is active. A user only receives an alert if they have media
**and** permission to the problem's host (Module 25).

![The on-call user's email media: all severities, always active](assets/module-27/03-user-media.png)

### Actions — conditions, operations, escalation, recovery

An **action** decides *when* to notify and *what to do*:

- **Conditions** scope it — we match the host group **Web Services**, so only Online
  Shop web-tier problems trigger this action (not every problem in Zabbix).
- **Operations** are the steps taken while the problem is active, arranged as an
  **escalation**: each step has a **start time** and the message recipients.
- **Recovery operations** run once the problem resolves.

Our action escalates: **step 1** emails the on-call **immediately**; **step 2**, after
**1 hour** unresolved, emails the whole **Zabbix administrators** group — so an
ignored problem climbs to more people. A **recovery operation** emails the on-call
when it clears.

![The action's operations: a 2-step escalation plus a recovery operation](assets/module-27/02-action-operations.png)

### Internal actions

Besides trigger problems, Zabbix has **internal actions** (a separate event source)
that notify on *monitoring health* events — an item becoming **not supported**, a
host **unreachable**, or an LLD rule erroring. Use them so a *broken check* pages you
instead of silently going dark. They are configured the same way, under **Alerts →
Actions → Internal actions**.

### Alert troubleshooting

When an expected email doesn't arrive, check the chain in order: is the **action**
enabled and do its **conditions** match the event? does the **user** have **media**
and **permission**? does the **media type** have a **message template**? Then read
**Reports → Audit log** / the action's status and the media type's **Test** button.
The send result (sent / failed + error) is recorded per alert.

## Docker-Based Demonstration

The instructor configures the Email media type against Mailpit, adds email media to
the Admin user, builds the `Online Shop problem notifications` action with a two-step
escalation and a recovery operation, then **stops `demo-nginx`** to raise a real
problem and shows the alert email arrive in the Mailpit web UI — then starts it and
shows the recovery email.

## Hands-On Lab

1. **Confirm the local mail server.** Mailpit (the lab's `demo-mailhog`) is already
   running; its web UI is at **http://localhost:8025**.
   **Expected:** an empty Mailpit inbox in the browser.

2. **Create the Email media type.** **Alerts → Media types → Create media type**:
   Name `Email (Mailpit lab)`, Type **Email**, **SMTP server** `demo-mailhog`,
   **port** `1025`, Connection security **None**, Authentication **None**, from email
   `zabbix@online-shop.lab`.
   **Expected:** the media type is saved and **Enabled**.

3. **Add message templates.** On the media type's **Message templates** tab, add a
   **Problem** template (subject `Problem: {EVENT.NAME}`) and a **Problem recovery**
   template (subject `Resolved in {EVENT.DURATION}: {EVENT.NAME}`), each with a body
   using macros.
   **Expected:** two templates listed — without them, sends fail.

4. **Give the user email media.** **Users → Users → Admin → Media → Add**: Type
   `Email (Mailpit lab)`, Send to `oncall@online-shop.lab`, all severities, active
   `1-7,00:00-24:00`.
   **Expected:** the Admin user shows one enabled email media.

5. **Create the trigger action.** **Alerts → Actions → Trigger actions → Create
   action**:
   - **Action** tab: Name `Online Shop problem notifications`; **New condition** →
     *Host group* = `Web Services`.
   - **Operations** tab: *Default operation step duration* `1h`. **Step 1** — *Send
     message* to **User Admin** via `Email (Mailpit lab)`. Add a **Step 2** (starts
     after 1h) — *Send message* to **User group Zabbix administrators** (escalation).
   - **Recovery operations** — *Send message* to **User Admin**.

   **Expected:** the action is saved and Enabled with two operation steps and a
   recovery operation.

6. **Generate a problem.** Stop the web frontend to fire the *Online Shop frontend is
   unavailable* trigger (Module 21):
   ```bash
   docker stop demo-nginx
   ```
   **Expected:** within ~1 min a problem appears in **Monitoring → Problems**, and an
   email **`Problem: Online Shop frontend is unavailable`** arrives in Mailpit.

7. **Recover the problem.** Bring it back:
   ```bash
   docker start demo-nginx
   ```
   **Expected:** the problem resolves and a **`Resolved in … : Online Shop frontend
   is unavailable`** email arrives — the recovery operation firing.

8. **Read the inbox.** Refresh **http://localhost:8025**.
   **Expected:** both the problem and the recovery email, from
   `zabbix@online-shop.lab` to `oncall@online-shop.lab`, with the macros resolved in
   the body.

   ![Problem and recovery emails delivered to the local inbox](assets/module-27/04-mailpit-inbox.png)

## Expected Outcome

Participants have working end-to-end alerting in the Docker lab: an email media type,
a user with media, an action that notifies and escalates on Online Shop web-tier
problems, and verified problem **and** recovery emails — the foundation for real
on-call workflows.

## Instructor Notes

- **Lab vs production.** We send to **Mailpit**, a local catch-all SMTP server, so no
  real email leaves the lab and students can see every message. In production you
  point the media type at a real relay (with TLS + auth), and add **Slack/Teams**
  webhooks and **PagerDuty/Opsgenie** for on-call rotation. The pipeline is identical.
- **The chain is the lesson.** When alerting "doesn't work", walk the chain: action
  enabled & conditions match → user has media → user has host permission → media type
  has a message template. We hit the **"No message defined"** error on purpose-worthy
  ground: a media type with no templates sends nothing.
- **Scope actions tightly.** An action with no conditions notifies on **every**
  problem in Zabbix — instant alert storm. We scoped to the **Web Services** host
  group; teach students to always scope by host group, severity, or tag.
- **Escalation is for the unacknowledged.** Steps with increasing delay move an
  ignored problem to more people. Pair with *Pause operations for suppressed problems*
  so maintenance windows (Module 26) don't page anyone.
- **Recovery and update operations.** Always configure a **recovery** message — an
  "all clear" is as important as the alarm. **Update** operations notify on
  acknowledgement/severity changes.
- **Internal actions catch blind spots.** A "not supported" item or an unreachable
  host means you've *stopped* monitoring something — an internal action turns that
  into an alert instead of silence.
- **Don't alert on noise.** Only severities that warrant waking someone should reach
  SMS/phone; route informational problems to email/chat. Tune in the user media
  severity filter and the action conditions.
- **Timing (~45 min).** ~10 min the pipeline + media types, ~8 min media type +
  templates, ~5 min user media, ~12 min action with escalation + recovery, ~8 min
  generate/recover and read the inbox, ~2 min internal actions + troubleshooting recap.

## Lab-State Delta

Added in Module 27 (kept — end-to-end alerting for the Online Shop):

- **Media type:** `Email (Mailpit lab)` (mediatypeid `104`, type Email) → SMTP
  `demo-mailhog:1025`, from `zabbix@online-shop.lab`, no auth/TLS. Two **message
  templates** (Problem, Problem recovery).
- **User media:** Admin (userid `1`) given email media → `oncall@online-shop.lab`,
  all severities, always active.
- **Trigger action:** `Online Shop problem notifications` (actionid `9`,
  eventsource trigger) — condition *Host group = Web Services*; **Operations** step 1
  → User Admin immediately, step 2 → user group *Zabbix administrators* after 1h
  (escalation); **Recovery operation** → User Admin. Step duration 1h.
- **Verified end to end:** stopped/started `demo-nginx` (and live demo-api triggers)
  → Mailpit received **Problem** and **Recovery** emails with macros resolved.
  demo-nginx left running/clean. Screenshots in `content/day-4/assets/module-27/`.
