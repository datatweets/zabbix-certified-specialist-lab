# Module 18: Advanced Templates

## Learning Objectives

By the end of this module you will be able to design a **reusable template** from
the ground up: bundle items, triggers, and macros into a single unit; **link** it
to hosts so they inherit everything it contains; parameterize it with **macros** so
that each host can differ where it needs to; and **export and import** it as a
versioned file you can keep under source control. The concrete payoff is that we
take the ad-hoc `demo-api` monitoring you wired up by hand back in Day 2 and turn
it into one clean, reusable *Online Shop API by HTTP* template — the kind of
artifact a real monitoring team builds once and reuses across an entire estate.

## Topics

### What is a template?

Up to now, every item and trigger you have built has lived directly on a single
host. That works fine when you have one of something. It falls apart the moment you
have ten. A **template** is the answer: a reusable bundle of monitoring
configuration — items, triggers, graphs, dashboards, macros, and low-level
discovery rules — that you **link** to hosts rather than rebuild on each one.

The mechanism is inheritance. Linked hosts **inherit** everything in the template,
and the relationship stays live: change the template once and every linked host
updates with it. This is precisely how Zabbix monitors hundreds of identical hosts
without anyone copying and pasting configuration — and it is the same machinery
behind the 360 built-in templates that ship with the product. When you eventually
manage a fleet, you will spend almost all of your time editing templates, not
hosts.

### Template inheritance and linked templates

It is worth being precise about what "inherits" means in practice, because it
governs how you will edit things for the rest of your Zabbix career. When a
template is linked to a host, the host receives the template's items and triggers
as **inherited** objects. You can spot them immediately because they are shown with
the **template name as a prefix** — and, critically, you cannot edit the inherited
parts on the host itself. The template owns them; you change them on the template,
and the host follows.

Templates do not only attach to hosts. They can also be **linked to other
templates** — a pattern called nesting. A high-level template links several
lower-level ones, composing a complete monitoring profile out of smaller, reusable
parts. Think of it the way you would think of composing software from libraries:
you assemble a big capability from focused building blocks rather than writing one
enormous module that does everything.

![Inherited items on a linked host — note the template-name prefix](assets/module-18/04-linked-host.png)

### Template items, triggers, graphs, dashboards

Everything you have ever built on a host can live on a template instead. That is
the whole point — a template is a host's monitoring configuration, lifted off the
host and made reusable. Our template carries:

- **Items** — the HTTP master item and its JSONPath dependent items (orders, queue
  length, response time).
- **Triggers** — the queue/response-time/unreachable triggers, referencing the
  template's own items as `/Online Shop API by HTTP/key`.
- It can also carry **graphs**, **dashboards**, and **LLD rules** (Module 23).

Notice the trigger references in the second bullet. On a host, a trigger points at
that host's key; on a template, it points at the *template's* own key. That
indirection is what lets the same trigger expression work on every host the
template touches — each linked host substitutes its own collected values.

![Template items: one HTTP master + JSONPath dependent items](assets/module-18/01-template-items.png)

![Template triggers reference the template's own items](assets/module-18/02-template-triggers.png)

### Template macros — the key to reuse

Here is the question that decides whether a template is genuinely reusable or just a
copy of one host: how do two linked hosts differ? If the template hard-codes a URL
or a threshold, it fits exactly one host and nothing else. The answer is
**template macros** (`{$NAME}`), which provide defaults that each linked host can
**override**. Our template uses three:

- `{$API.URL}` — the API base URL (item URL is `{$API.URL}/metrics`), so each host
  points at its own API.
- `{$API.QUEUE.MAX}`, `{$API.RESPONSE.MAX}` — trigger thresholds, tunable per host.

Picture the payoff in Online-Shop terms. You stand up ten API instances, link the
one template to all ten, and give each its own `{$API.URL}`. That single definition
now monitors all ten — one template, ten endpoints, each watched against the same
logic but pointed at its own address and tuned to its own limits.

![Template macros provide per-host-overridable defaults](assets/module-18/03-template-macros.png)

### Versioning, export, and import

A template is configuration, and configuration deserves the same discipline as
code. Zabbix supports that directly. Templates carry a **vendor** and **version**
and can be **exported** to a single **YAML** (or XML/JSON) file — exactly the right
unit for version control and for moving config between environments such as staging
and production. **Import** reads that file back, governed by rules for **Update
existing / Create new / Delete missing** that decide what happens when the file and
the live system disagree. The course ships this template's export at
`content/lab/templates/online-shop-api-by-http.yaml`, so you have a real 7.4 export
to import against.

![Import: choose a file and the Update/Create/Delete rules](assets/module-18/05-import.png)

### Template design best practices

A few habits separate templates that age well from templates that become a
maintenance burden:

- **Macros for anything that varies** (URLs, thresholds, credentials).
- **One responsibility per template**; compose with nesting rather than one giant
  template.
- **Name and group clearly** (`Templates/Online Shop`).
- **Version-control the export** so changes are reviewable.
- **Never edit inherited objects on the host** — change the template.

## Docker-Based Demonstration

The instructor builds *Online Shop API by HTTP* end to end — the macro `{$API.URL}`,
the HTTP master item, the JSONPath dependent items, and the macro-driven triggers —
and then links it to a brand-new host (`demo-api-2`). The key moment to watch for is
that `demo-api-2` inherits all of it and starts collecting immediately, with no
items built on the host by hand. The instructor then exports the template to YAML
and shows the import dialog, closing the loop from "build once" to "ship as a file."

## Hands-On Lab

1. **Create a template.** In **Data collection → Templates → Create template**:
   - **Template name:** `Online Shop API by HTTP`
   - **Template groups:** `Templates/Online Shop`

   **Add.**
   **Expected:** an empty template appears in the list.

2. **Add macros.** Open the template → **Macros** tab → add:
   - `{$API.URL}` = `http://demo-api:5000`
   - `{$API.QUEUE.MAX}` = `40`
   - `{$API.RESPONSE.MAX}` = `200`

   These are the defaults; any linked host may later override them.
   **Expected:** three template macros saved.

3. **Add items.** On the template's **Items**, create an **HTTP agent** master item
   `api.metrics.raw` with URL `{$API.URL}/metrics` (Text), then **dependent items**
   `api.queue.length` (JSONPath `$.queue_length`), `api.response.time`
   (`$.response_time_ms`, ms), `api.orders` (`$.orders`).
   The master fetches the whole JSON payload once; each dependent extracts one field from it.
   **Expected:** four template items, the dependents fed by the master.

4. **Add triggers.** On the template's **Triggers**, create:
   - `Online Shop API queue is backing up` —
     `last(/Online Shop API by HTTP/api.queue.length)>{$API.QUEUE.MAX}`
   - `Online Shop API response time is high` —
     `last(/Online Shop API by HTTP/api.response.time)>{$API.RESPONSE.MAX}`
   - `Online Shop API is unreachable` —
     `nodata(/Online Shop API by HTTP/api.metrics.raw,2m)=1`

   Each expression references the template's own items and reads its threshold from a macro, so the same logic travels to every linked host.
   **Expected:** three template triggers using the template's items and macros.

5. **Link the template to a host (inheritance).** Create a host `demo-api-2`
   (group *Web Services*, no interface), and on its **Templates** link
   *Online Shop API by HTTP*. Optionally override `{$API.URL}` on the host.
   This is the moment the template proves itself — one link, and a bare host becomes fully monitored.
   **Expected:** within a minute `demo-api-2` shows the template's items
   **inherited** (template-name prefix) and collecting, plus the three triggers —
   a fully monitored host from **one link**. Link it to more API hosts the same
   way, each with its own `{$API.URL}`.

6. **Export the template.** In **Data collection → Templates**, select the
   template → **Export → YAML**.
   This file is the reviewable, version-controllable definition of everything you just built.
   **Expected:** a `.yaml` file downloads — a versioned, reviewable definition of
   the whole template (see `content/lab/templates/online-shop-api-by-http.yaml`).

7. **Import it again.** Click **Import**, choose the YAML file, review the
   **Update existing / Create new / Delete missing** rules, and **Import**.
   Reading those rules before you click is the habit that keeps an import from quietly deleting objects you wanted to keep.
   **Expected:** the template is recreated/updated from the file — the basis for
   moving configuration between environments and for version control.

## Expected Outcome

You can now build a reusable template with items, triggers, and macros, link it to
hosts that inherit everything, parameterize per-host behavior with macros, and
export and import the template as a versioned file. That is the core skill for
managing monitoring at scale — defining a pattern once and reusing it — instead of
editing hosts one at a time and watching the configuration drift apart.
