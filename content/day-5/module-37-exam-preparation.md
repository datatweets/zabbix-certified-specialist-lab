# Module 37: Exam Preparation

## Learning Objectives

By the end of this module participants can **prepare effectively for the Zabbix
Certified Specialist (ZCS) exam**: they know the exam's format and ground rules, can
rapidly review the key knowledge areas, recognise the question style, take a realistic
**mock exam**, and turn their results into a focused study plan.

## Topics

### The exam, in plain terms

The Zabbix Certified Specialist exam is:

- **50 multiple-choice questions, 60 minutes** — about **72 seconds per question**.
- **Pass mark: 80 %** (40 / 50). Aim higher; leave margin.
- Taken **online or in a classroom**.
- **Based on Zabbix 7.0 (LTS).** This course uses **7.4**. The concepts are the same;
  a handful of UI labels and defaults can differ. **Know that the exam tests 7.0** and
  don't be thrown by tiny wording differences.
- **No prerequisites** to sit it. Two routes to certification: attend an official
  certified course and pass, **or** purchase the exam separately.

It sits on a ladder: **Certified User (ZCU) → Certified Specialist (ZCS) → Certified
Professional (ZCP) → Certified Expert (ZCE)**. ZCS is your target; ZCP requires it
(Module 39).

> **TO-VERIFY / external:** exam pricing, scheduling, and the exact current question
> count can change — confirm on **zabbix.com/exam_zcs** before you book. The numbers
> above were accurate at the time of writing.

### What the exam actually asks

The questions are **conceptual and configuration-focused**, not trivia:

- *Definitions and behaviour:* "what does a dependent item do?", "what does a trigger
  dependency suppress?"
- *Correct syntax and keys:* the 7.x trigger expression form, item keys, API auth.
- *Cause and effect / scenarios:* "active checks aren't arriving — what's the most
  likely cause?", "no alert was sent — which link is broken?"
- *Architecture:* which component does what, which port, which gateway.

You will rarely be asked to recall an obscure number; you will often be asked to
reason about how the pieces fit. That is exactly what building the Online Shop across
40 modules taught you.

### Rapid review — the knowledge areas

Use this as a checklist. For each, you should be able to **explain it and give the
example you built**. The module to revisit is in brackets.

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

- **Do, don't re-read.** For every weak area, **redo that module's hands-on lab** in
  your Docker lab. The exam rewards people who have actually configured Zabbix.
- **Take the mock exam under real conditions** — 60 minutes, no notes — then study your
  misses by topic.
- **Memorise the small set of exact facts** that questions hinge on: ports (10050 /
  10051), 7.x trigger syntax, Bearer auth, Deny-wins, SLI formula, severities order.
- **Read every option.** MCQ distractors are often *almost* right; eliminate, don't
  pattern-match.

## Instructor-Led Review (Demonstration)

The instructor walks the 13 knowledge areas against the **live Online Shop lab** —
opening the actual host, trigger, action, service, and dashboard you built for each
area — then works through several sample questions out loud, modelling how to read the
options and eliminate distractors.

## Hands-On Lab — Take the mock exam

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

## Instructor Notes

- **The mock exam is the centrepiece.** Run it timed and silent like the real thing,
  then spend the bulk of the session on the **review of misses** — that's where
  learning happens. (Files: `content/exam/zcs-mock-exam.md` + `-answers.md`.)
- **Doing beats reading.** Push students back into the **live lab** for weak areas. The
  Online Shop they built is the best study aid — every exam topic has a concrete
  example in it.
- **Set expectations on version.** The exam is **7.0**; the course is **7.4**. Reassure
  students the concepts are identical and point out the few cosmetic differences (menu
  labels, a default or two). Don't let a wording difference rattle them mid-exam.
- **Drill the exact facts.** A small set of precise items recurs: ports, 7.x trigger
  syntax, Bearer auth, Deny-wins, the SLI formula, severity order, passive-vs-active.
  Make flashcards.
- **Time discipline.** ~72 seconds/question. Teach flag-and-return: answer the easy
  ones first, never burn five minutes on one question.
- **Common misreads.** MCQ distractors exploit half-knowledge ("auth field" vs "Bearer
  header"; "most critical of children" vs "if all children fail"). Practise
  eliminating.
- **Timing (~45 min):** ~10 min format + knowledge-area review, ~25 min the mock exam
  (or a timed subset), ~10 min score + build study plans. For a full 60-minute mock,
  run it as pre-work and use the session for review.

## Lab-State Delta

Module 37 (exam prep — knowledge module, no lab objects created):

- **Committed artifacts:** `content/exam/zcs-mock-exam.md` (45-question mock exam,
  matches the real 50 Q / 60 min / 80 % format, concepts stable across Zabbix 7.0/7.4)
  and `content/exam/zcs-mock-exam-answers.md` (answer key + per-question explanations +
  "revisit this module" map and topic-grouped study plan).
- No changes to the live lab. The mock exam draws on facts verified throughout Modules
  1–36; the real exam is based on **Zabbix 7.0** (this course on **7.4**) — concepts
  identical.
