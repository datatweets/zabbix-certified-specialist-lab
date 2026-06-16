# Module 29: Configuring Zabbix Import/Export

## Learning Objectives

By the end of this module you will be able to move and reuse Zabbix configuration
with confidence rather than rebuilding it by hand every time you need it
somewhere new. You will **export** a template to a file and **import** it back,
and you will understand the **import rules** (create / update / delete) and the
**diff preview** well enough to predict what each one will do before you click.
You will version a template in **git** the way you version application code, and
you will be able to explain how export and import together support **backup**,
**template libraries**, and **migration between environments**.

## Topics

### Why export and import

Think about everything you have built in this course so far by clicking through
the frontend: items, triggers, the discovery rules, the Online Shop API template.
All of that effort lives inside one Zabbix server's database. If that server
disappears, or if another team wants the same monitoring, the work is trapped —
there is no way to hand it over except to recreate every field by hand. Export
solves exactly that problem. It turns the configuration you built by clicking into
a **portable file** you can carry anywhere, and that single capability unlocks
four things teams need constantly:

- **Reuse** — apply the Online Shop's API monitoring to another team's API.
- **Version-control** — keep templates in **git**, review changes, roll back.
- **Migrate** — move config from a **dev** Zabbix to **production**.
- **Back up** — a config snapshot that survives a database loss.

None of this is a special trick reserved for this module. It is the same
discipline the whole course has been quietly following: every template we build
is exported to `content/lab/templates/` and committed. By the end of this module
you will understand *why* that habit matters, not just that we do it.

### What can be exported, and in what format

Export is not limited to templates, even though templates are the most common
thing you will move around. You can export **templates**, **hosts**, **host
groups**, **template groups**, **maps**, **media types**, and **images** — most of
the configuration objects you have met in this course. Zabbix 7.4 writes the
export in one of three formats: **YAML** (the default — readable, diff-friendly),
**XML**, or **JSON**. The format you pick is purely about how you want to read and
review the file later; the configuration it describes is identical either way.

The detail that surprises people is how *complete* an export is. When you export a
template, its triggers, items, discovery rules, value maps, and tags travel
**with** the template — it is the whole unit, not just a shell. You are not
exporting a name and then having to reconnect everything by hand on the other
side; you are exporting the monitoring, finished and intact.

![Selecting the template and exporting it (YAML)](assets/module-29/01-export.png)

### Importing and the import rules

Import is the other half of the round-trip: it reads a file back in. The
interesting question is what happens when the file describes objects that *already
exist* on the server, and that is exactly what the **rules** control. For each
object type, you decide how the imported file reconciles with reality:

- **Create new** — add objects in the file that don't exist yet.
- **Update existing** — overwrite matching objects with the file's version.
- **Delete missing** — remove objects that exist but are **not** in the file
  (use with care — it prunes).

The first two are the everyday combination: bring in anything new, refresh
anything that changed, and leave the rest alone. The third one is the sharp tool
in the drawer. "Delete missing" makes the server match the file *exactly*, which
is wonderful when you want a host to mirror a template precisely and dangerous if
you ever import a partial file by accident — anything the file omits gets removed.
Knowing which rules are ticked before you press Import is the whole skill here.

![The import dialog: choose a file and set create / update / delete rules](assets/module-29/02-import-dialog.png)

### UUIDs make import idempotent

Here is the question a careful student asks next: if I import a file twice, do I
end up with duplicate items? The answer is no, and the reason is worth
understanding because it underpins everything else in this module. Every exported
object carries a **UUID** — a unique identifier that stays the same across
exports. On import, Zabbix matches by UUID, not by name, so re-importing an
unchanged file changes nothing, and importing a **changed** file updates exactly
the changed objects and nothing more.

That property has a name worth knowing: an operation you can repeat safely with no
extra effect each time is called **idempotent**. Importing our unchanged template
reports **"No changes"** — which is the diff engine telling you, plainly, that it
compared the file against the server and found nothing to do. That message is not
a dead end; it is proof the matching works and that imports are safe to re-run as
often as you like.

![The import diff preview reports "No changes" for an unchanged file](assets/module-29/03-import-preview.png)

### Template libraries

Once you see export and import as the mechanism for moving monitoring around, the
big built-in **template library** stops looking like magic and starts looking
familiar. Zabbix ships a large library (*Linux by Zabbix agent*, *PostgreSQL by
ODBC*, hundreds more) organized under template groups — and that is simply
import/export at scale, prepared by Zabbix and shipped with the product. Your own
templates form a **library** too: ours live in `Templates/Online Shop`. The thing
that turns a pile of templates into a *library* a team can actually use is
deliberate naming and grouping, so that someone six months from now can find the
Online Shop monitoring and reuse it without asking you where it lives.

### Backup and restore

This is the part where people most often confuse two different things, so let's
keep them firmly apart. There are two layers of backup, and they protect different
things:

- **Configuration backup** — export templates/hosts to files (and git). Restores
*what you monitor*.
- **Full backup** — a **database dump** of the Zabbix DB (`mysqldump`). Restores
*everything*, including history, events, and users.

The exports you make in this module capture *what you monitor* — the templates,
items, and triggers that define your monitoring. They do **not** capture the
collected history, the events, or the users. So export is not a substitute for a
database backup: if you need to recover everything after a disaster, you still
need a `mysqldump`. What versioned template files give you instead is speed — they
are the fastest way to rebuild monitoring config on a fresh server, with a clean
record of every change along the way.

### Migration between environments

Put all of this together and you get the workflow real teams use to promote
monitoring the way they promote code. You build and test a template on a **dev**
Zabbix, export it, then import it on **production** — the UUIDs keep the two in
sync so nothing duplicates, and git records every change so you can see exactly
what was promoted and roll it back if it misbehaves. That is how monitoring config
graduates from "something one engineer set up by hand" into something the whole
team can review, ship, and trust.

## Docker-Based Demonstration

The instructor exports the `Online Shop API by HTTP` template to YAML, **deletes**
it from the server, then **imports** it back from the file and shows it reappear with
all four items and three triggers intact — a full round-trip — and points out the
committed file under `content/lab/templates/`.

## Hands-On Lab

In this lab you will walk the complete round-trip yourself: export the Online Shop
API template, read what came out, delete it from the server, and bring it back from
the file. Doing the full loop is what makes export trustworthy — you will see with
your own eyes that nothing was lost.

1. **Export a template.** **Data collection → Templates**, filter to the
   `Templates/Online Shop` group, tick **Online Shop API by HTTP**, click
   **Export → YAML**.
   **Expected:** a `.yaml` file downloads containing the template, its 4 items, and
   3 triggers.

2. **Inspect the file.** Open it. Reading the file once is the best way to convince
   yourself that an export really is the complete monitoring, not a stub.
   **Expected:** human-readable YAML — `zabbix_export:` with `version: '7.4'`,
   `template_groups`, the template, its items (master HTTP agent + JSONPath
   dependents), triggers, and **uuid** fields.

3. **Delete the template.** Back in the list, tick it and **Delete** (it is unlinked,
   so nothing on a host breaks).
   **Expected:** the template is gone from `Templates/Online Shop`.

4. **Import it back.** Click **Import**, choose the exported file, leave **Create
   new** and **Update existing** checked, and **Import**. This is the moment the
   UUIDs earn their keep — Zabbix rebuilds the template from the file exactly as it
   was.
   **Expected:** Zabbix recreates the template with all 4 items and 3 triggers. (Re-
   importing the same file again reports **"No changes"** — imports are idempotent.)

   ![The reimported template's four items, fully restored](assets/module-29/04-imported-items.png)

5. **Re-link it (optional).** Link the reimported template to a host to confirm it
   works end to end (as in Module 18), then unlink to keep the lab tidy.
   **Expected:** the host inherits the template's items and triggers.

6. **Store it in git.** The file lives at
   `content/lab/templates/online-shop-api-by-http.yaml` and is committed with this
   module.
   ```bash
   git add content/lab/templates/online-shop-api-by-http.yaml
   git commit -m "template: Online Shop API by HTTP"
   ```
   **Expected:** the template is now versioned — diffs, history, and rollback like any
   code.

## Expected Outcome

You can now export any Zabbix configuration to a portable file and import it back
with the right create/update/delete rules, predicting what each rule will do
before you run it. You understand why UUID-based imports are idempotent and safe to
re-run, you can keep templates under version control in git, and you can explain
how export/import underpins the three things that depend on it: backup, reusable
template libraries, and dev-to-production migration.
