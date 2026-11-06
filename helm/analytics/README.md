_Work in progress_

See https://docs.georchestra.org/analytics/technical_guides/installation/

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
