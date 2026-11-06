_Work in progress_

See https://docs.georchestra.org/analytics/technical_guides/installation/

## Database migrations

The chart runs an Alembic migration Job after every Helm install and upgrade.
The Job upgrades the schema to `head` and then synchronizes the configured
TimescaleDB policies. It is retried while the database becomes available.

New installations require no additional settings:

```yaml
cli:
  migrations:
    enabled: true
    targetRevision: head
```

When upgrading an existing, pre-Alembic installation, opt in to the baseline
step for the first deployment:

```yaml
cli:
  migrations:
    existingDatabase:
      enabled: true
      baselineRevision: "0001"
```

`bootstrap-existing` refuses to stamp the database if any expected `0001`
relation is missing. If the database already has an Alembic revision, the
baseline step is skipped, so leaving the option enabled cannot move the
recorded revision backwards. Disable the option again after adoption to keep
the deployment intent clear.

The Job is a `post-install,post-upgrade` Helm hook because the chart may also
deploy its own TimescaleDB instance. Helm waits for the hook to complete and
marks the release failed if migrations cannot be applied.

## Incremental OGC aggregation

The chart creates a separate recovery CronJob for the persistent OGC aggregation
queue. `buffer2db` already drains this queue after ingestion; the additional job
retries pending buckets and processes buckets queued by `file2db` or `fake2db`.

```yaml
cli:
  aggregation:
    enabled: true
    schedule: "15 * * * *"
    batchSize: 100
    backoffLimit: 2
    successfulJobsHistoryLimit: 1
    failedJobsHistoryLimit: 3
```

The CronJob runs `analytics-cli aggregate-ogc`. Successful transactions remove
their queue rows. Historical retention and removal of the legacy TimescaleDB
continuous aggregates are intentionally outside this job and belong to the final
cutover procedure.
