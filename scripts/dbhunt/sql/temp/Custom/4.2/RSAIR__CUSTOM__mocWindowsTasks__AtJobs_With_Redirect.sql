--At Jobs with Redirect >
select
mn.MachineName
,wt.TaskName
,wt.LastRunUTCTime
,wt.NextRunUTCTime
,mp.path
,mp.filename
,wt.LaunchArguments
,mp.DaysSinceCreation
,wt.TriggerString


	from [dbo].[uvw_mocWindowsTasks] as [wt]
	INNER JOIN [dbo].[uvw_MachineModulePaths] AS [mp] WITH(NOLOCK) ON [mp].[PK_MachineModulePaths] = [wt].[FK_MachineModulePaths]
	INNER JOIN [dbo].[uvw_machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [mp].[FK_Machines]
	where wt.taskName LIKE N'\At%'
		and wt.LaunchArguments LIKE '%>%'