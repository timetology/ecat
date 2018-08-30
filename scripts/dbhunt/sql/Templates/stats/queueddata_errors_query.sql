select top 100 ScanTypeList, AgentID, BatchTimeStamp, Processed,
  case when (MergeDuration is not null and MergeDuration > 0) then 1 else 0 end as MergeCompleted,
  ErrorMessage
from AgentBatches
where Processed = 0 and ErrorMessage is not null and ErrorMessage != ''
  and BatchTimeStamp > dateadd(MINUTE, -24*60, getUTCDate())
order by BatchTimeStamp desc
