SELECT  mn.MachineName
,pa.path
,ar.type
,la.LaunchArguments

FROM
	[dbo].[mocAutoruns] AS [ar] WITH(NOLOCK)
	LEFT JOIN [dbo].[Paths] AS [pa] WITH(NOLOCK) ON ([pa].[PK_Paths] = [ar].[FK_Paths__RegistryPath])
	LEFT JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [ar].[FK_MachineModulePaths] AND [mp].[FK_Machines] = [ar].[FK_Machines])
	LEFT JOIN [dbo].[Modules] AS [mo] WITH(NOLOCK) ON ([mo].[PK_Modules] = [mp].[FK_Modules])
 LEFT JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [ar].[FK_Machines]
 LEFT JOIN dbo.LaunchArguments as la WITH(NOLOCK) ON la.PK_LaunchArguments = ar.FK_LaunchArguments 
WHERE 
	[ar].[Type] = 12 AND
	(
		[pa].[Path] LIKE '%Image File Execution Options\sethc.exe @Debugger' OR
		[pa].[Path] LIKE '%Image File Execution Options\magnify.exe @Debugger' OR
		[pa].[Path] LIKE '%Image File Execution Options\narrator.exe @Debugger' OR
		[pa].[Path] LIKE '%Image File Execution Options\osk.exe @Debugger' OR
		[pa].[Path] LIKE '%Image File Execution Options\utilman.exe @Debugger' OR
		[pa].[Path] LIKE '%Image File Execution Options\displayswitch.exe @Debugger'
	) AND
	[ar].[MarkedAsDeleted] = 0

