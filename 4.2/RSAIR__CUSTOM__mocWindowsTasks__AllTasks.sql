SELECT mn.MachineName, wt.TaskName, wt.LastRunUTCTime, wt.NextRunUTCTime, fn.FileName, wt.TriggerString, la.LaunchArguments

FROM
	dbo.mocWindowsTasks AS [wt] WITH(NOLOCK)
	INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON [mp].[PK_MachineModulePaths] = [wt].[FK_MachineModulePaths]
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [wt].[FK_Machines]
	INNER JOIN [dbo].[LaunchArguments] AS [la] WITH(NOLOCK) ON [la].[PK_LaunchArguments] = [wt].[FK_LaunchArguments]
	INNER JOIN [dbo].[FileNames] AS [fn] WITH(NOLOCK) ON [fn].[PK_FileNames] = [mp].[FK_FileNames]
