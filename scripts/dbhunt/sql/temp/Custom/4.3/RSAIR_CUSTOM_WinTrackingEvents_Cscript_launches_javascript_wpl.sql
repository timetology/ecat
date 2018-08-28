--===== RSA_IR-SuspiciousActivity_cscript launches javascript wpl ========--
-- Potential javascript downloader activity --

---- DB QUERY ----
SELECT  mn.MachineName, 
		se.EventUTCTime, 
		pa.Path as 'SourcePath', 
		fn.Filename as 'SourceFile', 
		se.Path_Target, 
		se.FileName_Target, 
		se.LaunchArguments_Target, 
		la.LaunchArguments as 'SourceArguments',
		se.Username
FROM
	--[dbo].[WinTrackingEventsCache] AS [se] WITH(NOLOCK)
	[dbo].[WinTrackingEvents_P0] AS [se] WITH(NOLOCK)
	--[dbo].[WinTrackingEvents_P1] AS [se] WITH(NOLOCK)
	INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [se].[FK_MachineModulePaths])
	--INNER JOIN [dbo].[Modules] AS [mo] WITH(NOLOCK) ON ([mo].[PK_Modules] = [mp].[FK_Modules])
	INNER JOIN [dbo].[FileNames] AS [fn] WITH(NOLOCK) ON ([fn].[PK_FileNames] = [mp].[FK_FileNames])
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [se].[FK_Machines]
	--INNER JOIN [dbo].[LinkedServers] AS [ls] WITH(NOLOCK) ON [ls].[PK_LinkedServers] = [mn].[FK_LinkedServers] 
	INNER JOIN [dbo].[LaunchArguments] AS [la] WITH(NOLOCK) ON [la].[PK_LaunchArguments] = [se].[FK_LaunchArguments__SourceCommandLine]
    INNER JOIN [dbo].[paths] as [pa] with(NOLOCK) on [mp].[FK_Paths] = [pa].[PK_Paths]
WHERE 
	[se].[BehaviorProcessCreateProcess] = 1 
	AND [fn].Filename = 'cmd.exe' 
	AND se.FileName_Target = 'cscript.exe' 
	AND sla.LaunchArguments LIKE N'%javascript%'
	AND sla.LaunchArguments LIKE N'%.wpl%'
	
	UNION
	
SELECT  mn.MachineName, 
		se.EventUTCTime, 
		pa.Path as 'SourcePath', 
		fn.Filename as 'SourceFile', 
		se.Path_Target, 
		se.FileName_Target, 
		se.LaunchArguments_Target, 
		la.LaunchArguments as 'SourceArguments',
		se.Username
FROM
	--[dbo].[WinTrackingEventsCache] AS [se] WITH(NOLOCK)
	--[dbo].[WinTrackingEvents_P0] AS [se] WITH(NOLOCK)
	[dbo].[WinTrackingEvents_P1] AS [se] WITH(NOLOCK)
	INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [se].[FK_MachineModulePaths])
	--INNER JOIN [dbo].[Modules] AS [mo] WITH(NOLOCK) ON ([mo].[PK_Modules] = [mp].[FK_Modules])
	INNER JOIN [dbo].[FileNames] AS [fn] WITH(NOLOCK) ON ([fn].[PK_FileNames] = [mp].[FK_FileNames])
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [se].[FK_Machines]
	--INNER JOIN [dbo].[LinkedServers] AS [ls] WITH(NOLOCK) ON [ls].[PK_LinkedServers] = [mn].[FK_LinkedServers] 
	INNER JOIN [dbo].[LaunchArguments] AS [la] WITH(NOLOCK) ON [la].[PK_LaunchArguments] = [se].[FK_LaunchArguments__SourceCommandLine]
    INNER JOIN [dbo].[paths] as [pa] with(NOLOCK) on [mp].[FK_Paths] = [pa].[PK_Paths]
WHERE 
	[se].[BehaviorProcessCreateProcess] = 1 
	AND [fn].Filename = 'cmd.exe' 
	AND se.FileName_Target = 'cscript.exe' 
	AND sla.LaunchArguments LIKE N'%javascript%'
	AND sla.LaunchArguments LIKE N'%.wpl%'

ORDER BY se.EventUTCTime desc



/* IIOC QUERY
SELECT DISTINCT
	[se].[FK_Machines],
	[se].[FK_MachineModulePaths],
	[se].[PK_WinTrackingEvents] AS [FK_mocSentinelEvents]

FROM
	[dbo].[WinTrackingEventsCache] AS [se] WITH(NOLOCK)
	INNER JOIN [dbo].[Machines] AS [mn] WITH(NOLOCK) ON ([mn].[PK_Machines] = [se].[FK_Machines])
	INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [se].[FK_MachineModulePaths])
	INNER JOIN [dbo].[FileNames] AS [sfn] WITH(NOLOCK) ON ([sfn].[PK_FileNames] = [mp].[FK_FileNames])
	INNER JOIN [dbo].[LaunchArguments] AS [sla] WITH(NOLOCK) ON [sla].[PK_LaunchArguments] = [se].[FK_LaunchArguments__SourceCommandLine]
	
WHERE 
	[se].[BehaviorProcessCreateProcess] = 1 
	AND [sfn].Filename = 'cmd.exe' 
	AND se.FileName_Target = 'cscript.exe' 
	AND sla.LaunchArguments LIKE N'%javascript%'
	AND sla.LaunchArguments LIKE N'%.wpl%'
*/