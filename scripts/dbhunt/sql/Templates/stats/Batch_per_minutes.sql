with preferences as (
    select time_span    = 60,   --span in minutes (60 is good for monitoring)
           utc_offset   = -5.0  --UTC+X in hours
), t2 as (
    select n = row_number() over (order by [object_id])-1 from sys.all_objects
)
select top 100
    'T+'+convert(varchar, n)+' x'+convert(varchar,max(p2.time_span))+' min' as elapsed_time,
    dateadd(HOUR, max(p2.utc_offset), max(LastMergeAttemptUTCTime)) as the_time,
    dateadd(HOUR, max(p2.utc_offset), max(BatchTimestamp)) as youngest_batch,
    dateadd(HOUR, max(p2.utc_offset), min(BatchTimestamp)) as oldest_batch,
    case when max(BatchTimeStamp) is null then null else count(*) end as batches_processed,
    case when max(BatchTimeStamp) is null then null else
        sum(case when (ErrorMessage is null or ErrorMessage = '') then 0 else 1 end) end as errors,
    max(datediff(ss, BatchTimeStamp, LastMergeAttemptUTCTime))/(3600.) as max_queue_wait_hours,
    max(datediff(ss, BatchTimeStamp, LastMergeAttemptUTCTime))/60. as max_queue_wait_minutes
from t2 left join (
    select datediff(ss, LastMergeAttemptUTCTime, getutcdate())/(time_span*60) delta, *
    from AgentBatches with(nolock)
    cross join preferences p1
) as t1 on t2.n = t1.delta
cross join preferences as p2
group by n
order by n
