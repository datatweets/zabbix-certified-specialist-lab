# Module 38: Exam Discussion & Strategy

## Learning Objectives

By the end of this module participants can approach the Zabbix Certified Specialist
exam **confidently and strategically**: they understand the certification and exam
process, know the **common mistakes** to avoid, can reason through **scenario-based**
questions out loud, and have a concrete plan to **keep practising** in a personal
Zabbix lab after the course.

## Topics

### Certification overview

The Zabbix Certified Specialist (**ZCS**) sits on a four-level ladder:

| Level | Certification | Prereq | Focus |
|---|---|---|---|
| 1 | **Certified User (ZCU)** | none | navigating and using Zabbix |
| 2 | **Certified Specialist (ZCS)** | none | **design + implement monitoring** *(this course)* |
| 3 | **Certified Professional (ZCP)** | **ZCS** | install/scale/secure, HA, advanced features |
| 4 | **Certified Expert (ZCE)** | ZCP | expert-level architecture |

**The ZCS exam:** **50 multiple-choice questions, 60 minutes, pass ≥ 80 %**, taken
**online or in a classroom**, **based on Zabbix 7.0 (LTS)**. There are **no
prerequisites** to sit it, and two ways to become certified: **attend an official
certified training course** and pass, **or purchase the exam separately**. Passing
earns a **certificate, a digital badge, and a physical pin**, and unlocks the path to
**ZCP** (Module 39).

> **TO-VERIFY / external:** prices, scheduling, and exact question counts can change —
> confirm on **zabbix.com/exam_zcs** and **zabbix.com/exams** before booking.

### A note on versions — 7.0 vs 7.4

The exam is built on **Zabbix 7.0 LTS**; this course is on **7.4**. **The concepts you
were tested on in the mock exam are identical in both.** A few UI labels or defaults
may differ slightly; don't let a small wording difference unsettle you mid-exam. If
anything, knowing 7.4 means you've seen *more* than the exam asks.

### Exam-day strategy

- **Budget your time.** ~**72 seconds per question**. Answer the easy ones first;
  **flag and return** to hard ones. Never burn five minutes on one question.
- **Read every option.** MCQ distractors are designed to look *almost* right.
  **Eliminate** wrong answers rather than pattern-matching the first plausible one.
- **Watch the qualifiers.** "always", "never", "only", "most likely" change the answer.
- **Trust your hands-on memory.** When unsure, picture how you actually configured it
  in the Online Shop lab — the muscle memory is usually right.
- **Don't leave blanks.** No penalty for guessing on MCQ; answer everything.

### Common mistakes (learn from this course's hard-won lessons)

These are the exact traps that caught us while building the Online Shop — and they are
prime exam-distractor material:

- **API auth.** It's the **`Authorization: Bearer <token>`** header, *not* the
  deprecated body `auth` field. (And `apiinfo.version` is called **without** any auth
  header.) *(M36)*
- **Trigger syntax.** 7.x is **function-first** `last(/host/key)>0`. The
  `{host:key.last()}` form is **pre-7.0** and wrong. *(M10)*
- **Menu names.** Host/template/item config is under **Data collection** in 7.x, *not*
  "Configuration". *(throughout)*
- **Active checks.** They need the agent **`Hostname`** to **match the Zabbix host
  name** and `ServerActive` set. A passive-works-but-active-doesn't symptom is almost
  always this. *(M7, M19)*
- **Alerting chain.** A media type with **no message template** sends nothing ("No
  message defined"); an **unscoped action** causes an alert storm. *(M27)*
- **Permissions.** **Capability (role) ≠ visibility (host-group permission via user
  group)**; and **Deny wins**. *(M25)*
- **Services map by tags**, not by host or item; the SLI is computed over the **whole
  period**, not the moment. *(M28, M35)*
- **Maintenance suppresses, it doesn't delete** — and a forgotten window hides real
  outages. *(M26)*
- **Passive vs active.** Passive = server→agent (10050); active = agent→server (10051).
  Mixing these up is a frequent error. *(M6, M7)*

### Scenario-based reasoning

The exam (and real life) rewards reasoning, not recall. Practise the pattern **symptom
→ layer → likely cause → fix → verify** out loud. The committed
`content/exam/zcs-scenarios.md` has ten real-world scenarios — agent silent, no email,
DB-down alert storm, SNMP timeout, invisible hosts, growing queue, designing for JSON
metrics / 200 branch offices, the "60 % SLA but green now" puzzle, and a Not-supported
item — each with **model reasoning**.

### Keep practising — and build a personal lab

The single best way to stay sharp is to **keep a personal Zabbix lab**, and you already
have one: **this Docker stack**.

- **It's reproducible and resettable.** `docker compose -f compose_lab.yaml down -v`
  then `up -d` gives everyone a clean, identical environment — break things freely.
- **Extend it.** Add a host, write a template, build a discovery rule, wire an alert —
  every exam topic has a place to practise.
- **Break and fix it.** Re-run the troubleshooting drills (Modules 31, 32, 40): stop a
  container, change a macro, disable an action — then diagnose.
- **Resources:** the **7.x documentation** (`zabbix.com/documentation`), the **Zabbix
  blog** and **community forums/Telegram**, and re-doing this course's labs.

A lab needs little: Docker Desktop, ~8 GB RAM, a browser, and a terminal — exactly the
student setup this course assumed.

## Instructor-Led Scenario Discussion (Demonstration)

The instructor works several cards from `zcs-scenarios.md` with the room: present the
situation, let participants reason aloud (*symptom → layer → cause → fix*), then reveal
the model reasoning and tie it to the live Online Shop lab. The goal is to make the
**reasoning pattern** automatic.

## Hands-On Lab — Discuss, then set up your practice lab

1. **Work the scenarios.** In pairs or as a group, take each card in
   `content/exam/zcs-scenarios.md`: state the symptom, the layer, the most likely
   cause, and the fix **before** reading the model reasoning.
   **Expected:** you can reason through each without guessing — and you spot which
   modules to revisit.

2. **Reproduce one in the lab.** Pick a scenario (e.g. the alert chain, or active
   checks) and **recreate the fault** in your Docker lab, then diagnose and fix it.
   **Expected:** the symptom appears, you find the cause with the right tool, you fix
   and verify it.

3. **Confirm you can reset your lab.** Practise a clean reset so you can study without
   fear of breaking anything:
   ```bash
   docker compose -f compose_lab.yaml down       # keep data
   docker compose -f compose_lab.yaml up -d       # back up
   # full wipe (fresh start): add -v to 'down' to remove volumes
   ```
   **Expected:** the stack stops and starts cleanly; you know how to get a fresh
   environment.

4. **Write your prep plan.** From the mock exam (Module 37) and these scenarios, list
   your weak topics and schedule lab time for each before booking the exam.
   **Expected:** a dated, concrete study plan.

## Expected Outcome

Participants understand the certification and exam process, can avoid the common
mistakes, can reason through scenario-based questions the way the exam expects, and
have a resettable personal lab and a plan to keep practising — so they can sit the exam
**confidently**.

## Instructor Notes

- **Make them reason out loud.** The exam tests applied understanding; the scenario
  cards build it. Don't reveal the model reasoning until the room has tried — the
  struggle is the learning.
- **Common mistakes are distractor gold.** Every gotcha in the list is a likely wrong
  option on the exam. Drill the *correct* fact and *why the trap is wrong*.
- **Sell the personal lab.** Certification is a milestone, not the goal — operating
  Zabbix is. The Docker lab they keep is how skills stay fresh; make sure everyone can
  reset and extend it before they leave.
- **Manage exam nerves.** Most failures are time-management and over-thinking, not
  knowledge. Rehearse flag-and-return and elimination; remind them 80 % passes, not
  100 %.
- **Version reassurance.** Pre-empt the "but the course was 7.4!" worry — the mock exam
  already used version-stable concepts; the differences are cosmetic.
- **Lab vs production.** The same discipline that passes the exam runs real monitoring:
  reason about the chain, verify with the right tool, document the fix. The exam is a
  proxy for the job.
- **Timing (~45 min):** ~10 min certification overview + exam strategy, ~8 min common
  mistakes, ~17 min scenario discussion (5–6 cards), ~10 min personal-lab setup + prep
  plan.

## Lab-State Delta

Module 38 (exam discussion — knowledge module, no lab objects created):

- **Committed artifact:** `content/exam/zcs-scenarios.md` — 10 real-world,
  scenario-based discussion cards (agent silent, no email, DB-down alert storm, SNMP
  timeout, invisible hosts, growing queue, JSON-metrics design, 200-branch design,
  SLA-vs-current puzzle, Not-supported item), each with **model reasoning** and the
  module to revisit.
- Certification facts grounded in official zabbix.com (ladder ZCU→ZCS→ZCP→ZCE; ZCS = 50
  MCQ / 60 min / 80 % / Zabbix 7.0; two paths to certify). Common-mistakes list drawn
  from this course's verified gotchas. No live-lab changes. Lab at 8 hosts.
