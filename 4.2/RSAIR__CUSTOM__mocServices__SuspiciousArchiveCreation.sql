select [mn].[MachineName]
	,[se].[EventUTCTime]
	,[se].[EventType]
	,[sfn].[FileName]
	,[se].[Path__TargetProcessPathName]
	,[se].[FileName__TargetProcessImageFileName]
	,[se].[SourceCommandLine]
	,[se].[TargetCommandLine]
	,[se].[MarkedAsDeleted]

FROM [dbo].[uvw_mocSentinelEvents]AS [se] WITH(NOLOCK)
INNER JOIN [dbo].[Machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [se].[FK_Machines] 
INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [se].[FK_MachineModulePaths])
INNER JOIN [dbo].[FileNames] AS [sfn] WITH(NOLOCK) ON ([sfn].[PK_FileNames] = [mp].[FK_FileNames])

WHERE 
	(
		[se].[TargetCommandLine] LIKE '% a % -r%'
		OR [se].[TargetCommandLine] LIKE '% a % -hp%'
	)
	
	-- FILTER PATHS ---
	AND [se].[TargetCommandLine] NOT LIKE '%\WinRAR\WinRAR.exe"%'
	
	--Last Day Results only
	--AND EventUTCTime >= DATEADD(DAY, -1, GETUTCDATE()) AND EventUTCTime <= GETUTCDATE()
	
	order by EventUTCTime desc