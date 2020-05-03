--Commands to be processed by Analyst Username
select mc.UserName as 'Commands to be processed by Analyst Username', count(*) as 'count'
FROM [dbo].[MachineCommands] AS mc
WHERE
   --mc.Comment LIKE 'Download RSA rmt_0_downloader_%'
   mc.Comment LIKE '%RSA%'
	AND mc.Type = 256  
	AND mc.Processed = 0
   group by mc.Username
   order by 'count' desc

--Commands to be processed by Comment
select mc.comment as 'Summary of RMT download commands to be processed', count(*) as 'count'
FROM [dbo].[MachineCommands] AS mc
WHERE
   --mc.Comment LIKE 'Download RSA rmt_0_downloader_%'
   mc.Comment LIKE '%RSA%'
	AND mc.Type = 256  
	AND mc.Processed = 0
   group by mc.comment
   order by 'count' desc


--Commands to be processed by Machine Name
select mn.machinename as 'Commands to be processed by Machine Name', count(*) as 'count'
FROM [dbo].[MachineCommands] AS mc
LEFT JOIN [dbo].[Machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [mc].[FK_Machines]
WHERE
   --mc.Comment LIKE 'Download RSA rmt_0_downloader_%'
   mc.Comment LIKE '%RSA%'
	AND mc.Type = 256  
	AND mc.Processed = 0
   group by mn.machinename
   order by 'count' desc


/*
select 
mn.machinename
,mc.Processed
,mc.CreateUTCTime
,mc.ProcessUTCTime
,mc.Comment
,mc.IsAutomatic
,mc.RetrieveCount
,mc.UserName
,mc.WorkStation
,mc.RetrieveUTCTime
,mc.Canceled
,mc.CancelUserName
,mc.ErrorMessage
,mc.ErrorCode
,mc.MachineCommandError
from uvw_MachineCommands as mc
LEFT JOIN [dbo].[Machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [mc].[FK_Machines]
WHERE
mc.Comment LIKE 'Download RSA rmt_0_downloader_windows %'
AND mc.Type = 256  
AND mc.Processed = 0
*/
