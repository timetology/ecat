--Machine Command Stats
SELECT COUNT(*) AS Count, State, Command  FROM (SELECT UserName, Comment, ErrorMessage
   ,CASE 
        WHEN [Type] = 256 THEN 'File Request'
        WHEN [Type] = 257 THEN 'Scan Command'
        WHEN [Type] = 258 THEN 'Update Agent Command'
        WHEN [Type] = 265 THEN 'Kernel Update'
        WHEN [Type] = 266 THEN 'Blocking Hash'
        WHEN [Type] = 270 THEN 'Cloud Relay'
        WHEN [Type] = 515 THEN 'Machine Identification Request'
        WHEN [Type] = 517 THEN 'Full Memory Dump Request Command'
        WHEN [Type] = 519 THEN 'Cancel Scan Command'
		else 'Other'
   END AS Command
  ,CASE 
            WHEN [Alertable] = 1 THEN 'Alertable'
			WHEN [Processed] = 1 THEN 'Processed'
            WHEN [Propagated] = 1 THEN 'Propagated'
            WHEN [Canceled] = 1 THEN 'Cancelled'
			WHEN [MarkedAsDeleted] = 1 THEN 'Deleted'
			ELSE 'Pending'
  END AS State
  FROM [dbo].[MachineCommands]) AS t
  GROUP BY State, Command
  ORDER BY Count DESC

--Pending File Requests from RMT Script
Select mc.comment, count(*) as 'count' from  [dbo].[MachineCommands] as mc
WHERE 
mc.[Type] = 256  
AND mc.[Processed] = 0
AND mc.[comment] LIKE 'Download RSA File Download%'
group by mc.comment
order by 'count' desc

 --File Request Commands by Username
 select t.username, count(*) as 'count'
   FROM [dbo].[MachineCommands] AS t
   where t.type = 256
   group by t.username
   order by 'count' desc

--File Request by Comment : Filename with count > 1
select t.comment, count(*) as 'count'
   FROM [dbo].[MachineCommands] AS t
   where t.type = 256 and 'count' <> '1'
   group by t.comment
   having count(*) > 1
   order by 'count' desc
