# Module 49: Backup, Restore, and Database Partitioning

> **Optional advanced module (extra).** Builds on Module 29 (import/export) and
> Module 30 (optimization). Pure database operations — no new containers.

## Learning Objectives

By the end of this module you can protect and scale the database that holds your
entire monitoring history. You will take a real **`mysqldump`** backup of the
Zabbix database and prove it is valid by **restoring it** into a scratch
database. You will then **partition** a history table by day and see why
partitioning is how large Zabbix installations keep their database fast —
replacing the slow, row-by-row housekeeper with an instant `DROP PARTITION`.

## Topics

### Two kinds of "backup"

Module 29 exported *configuration* as YAML — templates, hosts, triggers. That is
invaluable, but it is not a backup of your **data**: the months of history and
trends that make your graphs and SLAs meaningful live only in the database. A
real disaster-recovery plan needs a **database backup** as well.

For MySQL/MariaDB the standard tool is **`mysqldump`**, which writes the schema
and all rows as a SQL script you can replay to rebuild the database anywhere. The
flags matter: `--single-transaction` takes a consistent snapshot without locking
the busy history tables, and `--quick` streams rows rather than buffering them in
memory.

A backup you have never restored is a hope, not a backup. So the second half of
the drill is to **restore** the dump — here into a throwaway database — and
confirm it rebuilds cleanly. In production you would also automate the dump (cron
+ retention) and store it off the database host.

### Why partitioning exists

Zabbix keeps history and trends only for a configured window (in this lab, 31
days of history, a year of trends). Something has to delete the old rows, and by
default that something is the **housekeeper**, which issues `DELETE` statements.
On a small lab that is fine. On a busy server collecting thousands of values per
second, those deletes become the single most expensive thing the database does —
they fragment tables, generate huge amounts of I/O, and can fall behind faster
than they catch up (you saw the symptoms in Module 30: a growing database and a
struggling housekeeper).

**Partitioning** solves this. Instead of one giant `history` table, you split it
into one partition **per day** (and trends per month). Old data is then removed
by **dropping the whole partition** — a near-instant metadata operation — instead
of deleting millions of rows one at a time. The catch: when you partition, you
turn the Zabbix **History/Trends housekeeping off** and let a small scheduled
script manage partitions instead.

### How RANGE partitioning works

MySQL **RANGE** partitioning splits a table by a column's value. Zabbix history
tables are keyed on `(itemid, clock, ns)`, and because `clock` (the Unix
timestamp) is part of that key, you can partition on it. Each partition holds one
day's worth of rows — everything with a `clock` *less than* the next midnight:

```sql
PARTITION p2026_06_14 VALUES LESS THAN (UNIX_TIMESTAMP("2026-06-15 00:00:00"))
```

A final `MAXVALUE` partition catches anything newer, so writes never fail; a
management script then keeps adding tomorrow's partition and dropping the oldest.

## Docker-Based Demonstration

The instructor backs the database up, restores it to prove the dump, then
partitions a history table and drops a day with a single statement.

```bash
# Back up the Zabbix database (consistent snapshot, streamed)
docker exec zabbix-db sh -c 'mysqldump -uroot -proot_pwd --single-transaction \
  --quick --routines zabbix > /tmp/zabbix-backup.sql'
# -> ~58 MB, 207 CREATE TABLE statements

# Restore it into a scratch database and confirm it rebuilds
docker exec zabbix-db sh -c 'mysql -uroot -proot_pwd -e \
  "DROP DATABASE IF EXISTS zabbix_restore_test; CREATE DATABASE zabbix_restore_test;" \
  && mysql -uroot -proot_pwd zabbix_restore_test < /tmp/zabbix-backup.sql'
# live = 207 tables, restored = 207 tables  ->  the backup is valid
```

```sql
-- Partition history_uint by day, then drop the oldest day instantly
ALTER TABLE history_uint PARTITION BY RANGE (clock) (
  PARTITION p2026_06_14 VALUES LESS THAN (UNIX_TIMESTAMP("2026-06-15 00:00:00")),
  PARTITION p2026_06_15 VALUES LESS THAN (UNIX_TIMESTAMP("2026-06-16 00:00:00")),
  PARTITION p2026_06_16 VALUES LESS THAN (UNIX_TIMESTAMP("2026-06-17 00:00:00")),
  PARTITION p_future    VALUES LESS THAN MAXVALUE
);
ALTER TABLE history_uint DROP PARTITION p2026_06_14;   -- one day, gone instantly
```

The data lands neatly in per-day partitions, and dropping one removes a whole
day's history in milliseconds — no row-by-row delete.

## Hands-On Lab

1. **Back up the database.**
   ```bash
   docker exec zabbix-db sh -c 'mysqldump -uroot -proot_pwd --single-transaction \
     --quick --routines zabbix > /tmp/zabbix-backup.sql'
   docker exec zabbix-db sh -c 'ls -lh /tmp/zabbix-backup.sql; \
     grep -c "CREATE TABLE" /tmp/zabbix-backup.sql'
   ```
   Expected: a multi-megabyte `.sql` file containing ~**207** `CREATE TABLE`
   statements — the whole Zabbix schema and data.

2. **Restore into a scratch database.**
   ```bash
   docker exec zabbix-db sh -c 'mysql -uroot -proot_pwd -e \
     "DROP DATABASE IF EXISTS zabbix_restore_test; CREATE DATABASE zabbix_restore_test;" \
     && mysql -uroot -proot_pwd zabbix_restore_test < /tmp/zabbix-backup.sql'
   ```
   Expected: the import completes without error.

3. **Confirm the restore matches the original.**
   ```bash
   docker exec zabbix-db sh -c 'mysql -uroot -proot_pwd -N -e \
     "SELECT \"live\",     COUNT(*) FROM information_schema.tables WHERE table_schema=\"zabbix\" \
      UNION ALL \
      SELECT \"restored\", COUNT(*) FROM information_schema.tables WHERE table_schema=\"zabbix_restore_test\";"'
   ```
   Expected: both report the **same table count** (207 = 207). Your dump is a
   valid, restorable backup — not just a hope.

4. **Check whether a history table is partitioned.**
   ```bash
   docker exec zabbix-db sh -c 'mysql -uroot -proot_pwd -N -e \
     "SELECT MIN(clock), MAX(clock) FROM zabbix.history_uint;"'
   ```
   Expected: a span of a few days of data, in one un-partitioned table.

5. **Partition `history_uint` by day.** Use the day boundaries that cover your
   data (adjust the dates to match step 4):
   ```sql
   ALTER TABLE history_uint PARTITION BY RANGE (clock) (
     PARTITION p2026_06_14 VALUES LESS THAN (UNIX_TIMESTAMP("2026-06-15 00:00:00")),
     PARTITION p2026_06_15 VALUES LESS THAN (UNIX_TIMESTAMP("2026-06-16 00:00:00")),
     PARTITION p2026_06_16 VALUES LESS THAN (UNIX_TIMESTAMP("2026-06-17 00:00:00")),
     PARTITION p_future    VALUES LESS THAN MAXVALUE
   );
   ```
   Expected: the `ALTER` completes; the table now has one partition per day plus a
   `MAXVALUE` catch-all.

6. **See the data distribute across partitions.**
   ```bash
   docker exec zabbix-db sh -c 'mysql -uroot -proot_pwd -N -e \
     "SELECT PARTITION_NAME, TABLE_ROWS FROM information_schema.PARTITIONS \
      WHERE TABLE_SCHEMA=\"zabbix\" AND TABLE_NAME=\"history_uint\" \
      ORDER BY PARTITION_ORDINAL_POSITION;"'
   ```
   Expected: each day's rows sit in their own partition (e.g. tens of thousands
   per day), and new values keep landing in today's partition — Zabbix never
   noticed.

7. **Drop a day instantly.**
   ```sql
   ALTER TABLE history_uint DROP PARTITION p2026_06_14;
   ```
   Expected: a full day of history is removed in milliseconds — the operation that
   would take the housekeeper millions of individual `DELETE`s. This is the whole
   point of partitioning.

8. **Know the production rule.** When you partition, you must turn off Zabbix's
   own history/trends housekeeping (**Administration → Housekeeping**, uncheck
   *Enable internal housekeeping* for History and Trends) and let a scheduled
   script add tomorrow's partition and drop the oldest each night.
   Expected: you can explain why running both the housekeeper *and* partitioning
   is wasteful, and that partition management becomes a cron job.

## Expected Outcome

You have taken a real `mysqldump` backup of the Zabbix database and **proven it
restores** by rebuilding it into a scratch database with a matching table count.
You have partitioned a history table by day, watched the data distribute and new
values keep flowing, and dropped an entire day of history instantly with `DROP
PARTITION`. You understand why large Zabbix sites replace the housekeeper with
partitioning, and the operational rule that the two must not both run.

## Instructor Notes

- **Lab vs production — backups.** Here we dump and restore on the same container
  for the drill. In production you automate `mysqldump` (or **Percona XtraBackup**
  for large, hot databases; **pg_dump**/**pgBarman** for PostgreSQL) via cron with
  retention (`find -mtime +N -delete`), and you store the dumps **off** the
  database host. Stress: a backup is only real once you have restored it.
- **`--single-transaction` matters.** On InnoDB it gives a consistent snapshot
  without locking the history tables, so the dump does not stall live collection.
  Without it, a busy server can be blocked during the backup.
- **Partitioning is a one-way trade.** Once partitioned, you **must** disable
  Zabbix History/Trends housekeeping or the two fight. Make this explicit — a
  common production mistake is partitioning and leaving the housekeeper on.
- **Where the boundaries come from.** Real setups run a Perl/Python script
  (e.g. Opensource ICT Solutions' `mysql_zbx_part.pl`, referenced in the cookbook)
  on a nightly cron: it pre-creates the next N daily partitions and drops those
  older than the retention window. We did it by hand to show the mechanics.
- **PostgreSQL has a different answer.** On PostgreSQL the equivalent is the
  **TimescaleDB** extension (hypertables and automatic chunking), which Zabbix
  supports natively. We stay on MySQL here, so partitioning is the relevant tool;
  the cookbook's Chapter 12 covers TimescaleDB for the PostgreSQL path.
- **This persists.** The `history_uint` table remains partitioned after the lab. It
  is fully reversible with `ALTER TABLE history_uint REMOVE PARTITIONING`. New data
  flows into the `MAXVALUE` partition once the dated partitions are passed, so the
  lab keeps working even without a management script.
- **Timing (~40 min):** ~12 min backup/restore drill, ~8 min why-partitioning,
  ~15 min partition + distribute + drop, ~5 min housekeeping/cron production rule.

## Lab-State Delta

Added in Module 49 (kept):

- **Verified backup/restore:** `mysqldump` of `zabbix` (~58 MB, 207 tables) →
  restored into scratch DB `zabbix_restore_test` (207 = 207) → scratch DB and dump
  file removed afterward. No lasting change from this part.
- **Partitioning (persists):** `zabbix.history_uint` is now **RANGE-partitioned by
  `clock`** (daily partitions `p2026_06_14` … plus `p_future` MAXVALUE). The oldest
  partition was dropped to demonstrate instant purge. Zabbix continues writing
  normally; reversible with `ALTER TABLE history_uint REMOVE PARTITIONING`.
- **Housekeeping unchanged** in the lab (left enabled); production rule to disable
  History/Trends housekeeping when partitioning is documented, not applied.
- **No new containers.** Command-line module — verification is the SQL output
  shown above.
