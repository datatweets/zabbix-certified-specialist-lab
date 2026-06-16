# Module 37: Exam Preparation

## Learning Objectives

By the end of this module participants can **prepare effectively for the Zabbix
Certified Specialist (ZCS) exam**: they know the exam's format and ground rules, can
rapidly review the key knowledge areas, recognise the question style, take a realistic
**mock exam**, and turn their results into a focused study plan.

## Topics

You have spent thirty-six modules building one monitoring platform for one imaginary
company. Now comes the moment that gives all that work a credential: the certification
exam. This module is not about adding another capability to the Online Shop. It is
about converting what you already know into a passing score under timed, closed-book
conditions — which is a different skill from configuring Zabbix, and one worth
practising on its own. The strategy here is simple: understand the rules of the game,
walk back through everything you built and name it precisely, sit a realistic mock
exam, and then study only the gaps that mock exam exposes.

### The exam, in plain terms

Before you can study efficiently, you need to know exactly what you are studying for —
the shape of the test, the clock, and the bar you must clear. The Zabbix Certified
Specialist exam is:

- **50 multiple-choice questions, 60 minutes** — about **72 seconds per question**.
- **Pass mark: 80 %** (40 / 50). Aim higher; leave margin.
- Taken **online or in a classroom**.
- **Based on Zabbix 7.0 (LTS).** This course uses **7.4**. The concepts are the same;
  a handful of UI labels and defaults can differ. **Know that the exam tests 7.0** and
  don't be thrown by tiny wording differences.
- **No prerequisites** to sit it. Two routes to certification: attend an official
  certified course and pass, **or** purchase the exam separately.

Notice what those numbers mean in practice. Seventy-two seconds per question is not
much; it rewards quick recognition over slow derivation, which is why the study
strategy later leans so hard on having actually done the work rather than merely read
about it. And the 80 % bar is high — you can miss only ten questions out of fifty — so
the goal is not "pass somehow" but "have margin to spare."

The certification itself sits on a ladder: **Certified User (ZCU) → Certified
Specialist (ZCS) → Certified Professional (ZCP) → Certified Expert (ZCE)**. ZCS is your
target; ZCP requires it (Module 39). Each rung assumes the one below, so passing ZCS is
not just a goal in itself — it is the gate to everything above it.

> **TO-VERIFY / external:** exam pricing, scheduling, and the exact current question
> count can change — confirm on **zabbix.com/exam_zcs** before you book. The numbers
> above were accurate at the time of writing.

### What the exam actually asks

A common worry before any certification is that it will be a memory test full of
obscure numbers. It is not. The questions are **conceptual and configuration-focused**,
not trivia, and they fall into a few recognisable families:

- *Definitions and behaviour:* "what does a dependent item do?", "what does a trigger
  dependency suppress?"
- *Correct syntax and keys:* the 7.x trigger expression form, item keys, API auth.
- *Cause and effect / scenarios:* "active checks aren't arriving — what's the most
  likely cause?", "no alert was sent — which link is broken?"
- *Architecture:* which component does what, which port, which gateway.

The pattern across all four is reasoning rather than recall. You will rarely be asked
to recall an obscure number; you will often be asked to reason about how the pieces fit.
That is exactly what building the Online Shop across 40 modules taught you. Every time
you traced why an active check failed, or which broken link in the alert chain swallowed
a notification, you were rehearsing the precise mental move the exam asks for.

### Rapid review — the knowledge areas

This is the heart of your revision. Use it as a checklist, working down the list one
area at a time. For each, you should be able to **explain it and give the example you
built** — the concrete host, trigger, or dashboard from your own lab — because a concept
you can attach to something you actually configured is a concept you will not forget
under time pressure. The module to revisit is in brackets.

**1. Architecture & deployment** *(M1–M5)* — server (processing) vs database (storage)
vs frontend (UI); proxy, agent, Java gateway, web service; ports **10050** (agent),
**10051** (server/trapper); Docker Compose as separate containers.

**2. Data collection & agents** *(M6–M9, M11)* — **passive** (server→agent) vs
**active** (agent→server, `Hostname` must match); item types (agent, trapper, SNMP,
HTTP, JMX, ODBC, calculated, dependent); real item keys; **UserParameter** for custom
metrics; preprocessing (change-per-second, JSONPath, regex).

**3. Triggers & problems** *(M10)* — **7.x syntax** `last(/host/key)>0`; severities
(Disaster highest); **recovery** expressions; **dependencies** (suppress the symptom,
alert the root cause); `nodata()`; problem events.

**4. Templates** *(M17, M18)* — linking **inherits** and keeps in sync; macros
`{$NAME}`; export/import as **YAML**, matched by **UUID**; mass operations.

**5. Discovery & LLD** *(M15, M23)* — network discovery vs **low-level discovery**; LLD
returns JSON with `{#MACRO}`; **item/trigger prototypes**; **filters** include/exclude.

**6. Proxy** *(M14)* — collects for remote sites; **active** (connects to server) vs
**passive**; buffers when the server is down.

**7. Actions & alerting** *(M27)* — the chain **trigger → action → operation → media
type + user media → message**; **escalation** steps; **recovery** operations; scope
actions with **conditions**; the "**No message defined**" gotcha.

**8. Users & permissions** *(M25)* — **user groups** grant permission on **host
groups**; roles (User/Admin/Super admin); **Deny wins**; Super admin sees all.

**9. Security** *(M26)* — change defaults; named least-privilege users; **PSK** and
**certificate** encryption; agent **`Server`** allow-list; audit log; maintenance.

**10. Dashboards, maps & reports** *(M12, M33, M34)* — widgets; **maps** colour by
status; **System information**, **Availability report**, **Top 100 triggers**;
**scheduled PDF** reports need the **web service** + **Frontend URL**.

**11. Business services & SLA** *(M28, M35)* — services map to problems by **tags**;
status calculation rules; **SLI = uptime/(uptime+downtime)** vs the SLO; root cause.

**12. API & automation** *(M36)* — JSON-RPC; **`Authorization: Bearer <token>`**;
`host.get/create/update`, `problem.get`, `configuration.export`.

**13. Troubleshooting** *(M30, M31)* — the method *symptom → layer → test → fix →
verify*; **`zabbix_get`**; container/Zabbix logs; **Not supported** items; housekeeping
and NVPS.

### Study strategy

Knowing the knowledge areas is one thing; preparing efficiently is another. The
difference between a candidate who passes comfortably and one who scrapes by — or
fails — is usually not how many hours they put in but how they spend them. A few
principles will get you the most return:

- **Do, don't re-read.** For every weak area, **redo that module's hands-on lab** in
  your Docker lab. The exam rewards people who have actually configured Zabbix.
- **Take the mock exam under real conditions** — 60 minutes, no notes — then study your
  misses by topic.
- **Memorise the small set of exact facts** that questions hinge on: ports (10050 /
  10051), 7.x trigger syntax, Bearer auth, Deny-wins, SLI formula, severities order.
- **Read every option.** MCQ distractors are often *almost* right; eliminate, don't
  pattern-match.

That last point deserves emphasis, because it is where careful candidates lose easy
marks. A well-written multiple-choice question often offers two answers that both look
plausible at a glance, with one subtly wrong word — the "auth field" where it should be
the "Bearer header," or "the most critical of children" where the rule is "if all
children fail." Reading every option and eliminating, rather than grabbing the first one
that feels right, is the habit that protects you from exactly those traps.

## Instructor-Led Review (Demonstration)

The instructor walks the 13 knowledge areas against the **live Online Shop lab** —
opening the actual host, trigger, action, service, and dashboard you built for each
area — then works through several sample questions out loud, modelling how to read the
options and eliminate distractors.

## Hands-On Lab — Take the mock exam

The mock exam is the centrepiece of this module, and the steps below mirror how you
should treat the real thing: sit it cold, score it honestly, and then let your mistakes
direct your revision. The point is not the score itself but the map of weaknesses it
hands you.

1. **Sit the mock exam.** Open `content/exam/zcs-mock-exam.md` and answer all **45
   questions in 60 minutes**, closed-book. Mark your answers; don't look at the key.
   **Expected:** a completed answer sheet and a sense of which topics felt shaky.

2. **Score it.** Check `content/exam/zcs-mock-exam-answers.md`.
   **Expected:** a score out of 45. **≥ 36 (80 %)** is a pass.

3. **Build a study plan from your misses.** For every wrong answer, note the **topic**
   and the **module** (the key lists both), grouped by area.
   **Expected:** a short list like *"Triggers (M10), Alerting (M27)"* — your revision
   targets.

4. **Redo the weak labs.** Go back into the live lab and **re-do the hands-on** for
   each weak module — actually configure it again.
   **Expected:** the concept is solid because you did it, not just read it.

5. **Re-test.** Re-take the questions you missed (or the whole exam) until you're
   comfortably over 80 %.
   **Expected:** consistent passing scores → you're ready to book.

## Expected Outcome

Participants know exactly what the ZCS exam expects, have measured themselves against a
realistic mock exam, have identified their weak areas, and have a concrete,
lab-based plan to close the gaps before sitting the real exam.
