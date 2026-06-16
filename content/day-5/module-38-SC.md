# Module 38: Exam Discussion & Strategy

## Learning Objectives

By the end of this module you will be able to walk into the Zabbix Certified
Specialist exam **confidently and strategically**, rather than nervously. That
means several distinct things, and it is worth naming them: you will understand
how the certification and the exam actually work, so there are no surprises on
the day; you will know the **common mistakes** that trip people up — most of them
the exact traps you already met while building the Online Shop — and how to avoid
them; you will be able to reason through **scenario-based** questions out loud,
which is what the exam really tests; and you will leave with a concrete plan to
**keep practising** in a personal Zabbix lab after the course ends, because a
certificate is a milestone, not a finish line.

## Topics

### Certification overview

Before you book anything, it helps to see where the Specialist exam sits in the
larger picture. Zabbix's certifications form a four-level ladder, and each rung
assumes a different depth of knowledge:

| Level | Certification | Prereq | Focus |
|---|---|---|---|
| 1 | **Certified User (ZCU)** | none | navigating and using Zabbix |
| 2 | **Certified Specialist (ZCS)** | none | **design + implement monitoring** *(this course)* |
| 3 | **Certified Professional (ZCP)** | **ZCS** | install/scale/secure, HA, advanced features |
| 4 | **Certified Expert (ZCE)** | ZCP | expert-level architecture |

Read that ladder from the bottom up and the progression tells a story. The User
level is about *operating* a Zabbix someone else built. The Specialist level —
the one you are preparing for — is about *designing and implementing* monitoring
yourself, which is exactly the skill this whole course has been building, one
Online Shop component at a time. Professional and Expert then take you into
running Zabbix at scale, securing it, and architecting it, and they require ZCS
as a stepping stone. So passing this exam is not just a credential; it is the
gateway to everything above it.

Here are the concrete facts about the exam you are sitting. **The ZCS exam:** **50
multiple-choice questions, 60 minutes, pass ≥ 80 %**, taken **online or in a
classroom**, **based on Zabbix 7.0 (LTS)**. There are **no prerequisites** to sit
it, and two ways to become certified: **attend an official certified training
course** and pass, **or purchase the exam separately**. Passing earns a
**certificate, a digital badge, and a physical pin**, and unlocks the path to
**ZCP** (Module 39).

> **TO-VERIFY / external:** prices, scheduling, and exact question counts can change —
> confirm on **zabbix.com/exam_zcs** and **zabbix.com/exams** before booking.

### A note on versions — 7.0 vs 7.4

There is one detail that quietly worries almost every student, so let's address
it head-on. The exam is built on **Zabbix 7.0 LTS**; this course is on **7.4**.
**The concepts you were tested on in the mock exam are identical in both.** A few
UI labels or defaults may differ slightly; don't let a small wording difference
unsettle you mid-exam. If anything, knowing 7.4 means you've seen *more* than the
exam asks — you have practised on a slightly newer release, which is a position of
strength, not a handicap.

### Exam-day strategy

How you spend your sixty minutes matters almost as much as what you know. Most
people who fail the ZCS do not fail because the material was beyond them; they
fail because they mismanaged time or talked themselves out of a correct answer.
The following habits are designed to protect you from both:

- **Budget your time.** ~**72 seconds per question**. Answer the easy ones first;
  **flag and return** to hard ones. Never burn five minutes on one question.
- **Read every option.** MCQ distractors are designed to look *almost* right.
  **Eliminate** wrong answers rather than pattern-matching the first plausible one.
- **Watch the qualifiers.** "always", "never", "only", "most likely" change the answer.
- **Trust your hands-on memory.** When unsure, picture how you actually configured it
  in the Online Shop lab — the muscle memory is usually right.
- **Don't leave blanks.** No penalty for guessing on MCQ; answer everything.

### Common mistakes (learn from this course's hard-won lessons)

The single most useful thing you can review before the exam is the list of
mistakes you already learned to avoid. These are the exact traps that caught us
while building the Online Shop — and that is no coincidence, because the same
points that confuse practitioners in real life are prime exam-distractor material.
A well-written wrong answer is almost always built on a real misconception. Each
item below pairs the correct fact with the trap it dispels, and points back to
the module where you first met it:

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

If there is one mental shift that separates passing candidates from failing ones,
it is this: the exam (and real life) rewards reasoning, not recall. You will rarely
be asked to regurgitate a definition; you will be asked what is *most likely*
causing a described symptom, or which design fits a stated requirement. The way to
train for that is to make a reasoning pattern automatic. Practise the pattern
**symptom → layer → likely cause → fix → verify** out loud, so that under exam
pressure your mind reaches for a structured diagnosis instead of a panicked guess.
The committed `content/exam/zcs-scenarios.md` has ten real-world scenarios — agent
silent, no email, DB-down alert storm, SNMP timeout, invisible hosts, growing
queue, designing for JSON metrics / 200 branch offices, the "60 % SLA but green
now" puzzle, and a Not-supported item — each with **model reasoning**.

### Keep practising — and build a personal lab

Skills decay when they are not used, and a certificate earned today is worth little
if you cannot still configure a trigger six months from now. The single best way to
stay sharp is to **keep a personal Zabbix lab**, and here is the good news: you
already have one. **This Docker stack** is yours to keep, and it is built for exactly
this kind of fearless experimentation.

- **It's reproducible and resettable.** `docker compose -f compose_lab.yaml down -v`
  then `up -d` gives everyone a clean, identical environment — break things freely.
- **Extend it.** Add a host, write a template, build a discovery rule, wire an alert —
  every exam topic has a place to practise.
- **Break and fix it.** Re-run the troubleshooting drills (Modules 31, 32, 40): stop a
  container, change a macro, disable an action — then diagnose.
- **Resources:** the **7.x documentation** (`zabbix.com/documentation`), the **Zabbix
  blog** and **community forums/Telegram**, and re-doing this course's labs.

Notice how little it actually takes to keep this going. A lab needs little: Docker
Desktop, ~8 GB RAM, a browser, and a terminal — exactly the student setup this
course assumed. Nothing about studying after the course requires special hardware
or a budget; it requires only that you keep the stack and keep poking at it.

## Instructor-Led Scenario Discussion (Demonstration)

The instructor works several cards from `zcs-scenarios.md` with the room: present the
situation, let participants reason aloud (*symptom → layer → cause → fix*), then reveal
the model reasoning and tie it to the live Online Shop lab. The goal is to make the
**reasoning pattern** automatic.

## Hands-On Lab — Discuss, then set up your practice lab

The lab for this module is unusual: instead of building a new monitoring object,
you are rehearsing the way of thinking the exam demands and making sure your study
environment is ready for the weeks ahead. Work through the steps in order — the
first two sharpen your diagnostic reasoning, and the last two get your personal lab
and a study plan in place.

1. **Work the scenarios.** In pairs or as a group, take each card in
   `content/exam/zcs-scenarios.md`: state the symptom, the layer, the most likely
   cause, and the fix **before** reading the model reasoning. Forcing yourself to
   commit to an answer first is what builds the reflex; reading the model reasoning
   only after you have tried is where the learning actually happens.
   **Expected:** you can reason through each without guessing — and you spot which
   modules to revisit.

2. **Reproduce one in the lab.** Pick a scenario (e.g. the alert chain, or active
   checks) and **recreate the fault** in your Docker lab, then diagnose and fix it.
   Reproducing a fault by hand cements the cause-and-effect far more deeply than
   reading about it ever could.
   **Expected:** the symptom appears, you find the cause with the right tool, you fix
   and verify it.

3. **Confirm you can reset your lab.** Practise a clean reset so you can study without
   fear of breaking anything — knowing you can always get back to a known-good state
   is what makes the lab safe to experiment in:
   ```bash
   docker compose -f compose_lab.yaml down       # keep data
   docker compose -f compose_lab.yaml up -d       # back up
   # full wipe (fresh start): add -v to 'down' to remove volumes
   ```
   **Expected:** the stack stops and starts cleanly; you know how to get a fresh
   environment.

4. **Write your prep plan.** From the mock exam (Module 37) and these scenarios, list
   your weak topics and schedule lab time for each before booking the exam. A vague
   intention to "study more" rarely survives a busy week; a dated, specific plan does.
   **Expected:** a dated, concrete study plan.

## Expected Outcome

By the end of this module you understand the certification and exam process, you
can avoid the common mistakes that account for most failures, you can reason
through scenario-based questions the way the exam expects, and you have a
resettable personal lab plus a concrete plan to keep practising. Put together,
that is what lets you sit the exam **confidently** — not hoping you remember
enough, but knowing you have rehearsed the exact thinking it asks of you.
