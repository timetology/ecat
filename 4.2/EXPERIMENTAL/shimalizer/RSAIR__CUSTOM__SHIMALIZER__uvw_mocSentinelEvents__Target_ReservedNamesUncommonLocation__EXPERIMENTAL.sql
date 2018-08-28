--SHIMALIZER - Target Reserved Names Uncommon Location

SELECT
	[mn].[MachineName]
	,[se].[EventUTCTime]
	,[sp].[path] as 'SourcePath'
	,[sfn].[FileName] as 'SourceFileName'
	,[se].[Path__TargetProcessPathName] as 'TargetPath'
	,[se].[FileName__TargetProcessImageFileName] as 'TargetFileName'
	,[se].[SourceCommandLine]
	,[se].[TargetCommandLine]
  
FROM [dbo].[uvw_mocSentinelEvents] AS [se] WITH(NOLOCK)
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [se].[FK_Machines] 
	INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [se].[FK_MachineModulePaths])
	INNER JOIN [dbo].[Modules] AS [mo] WITH(NOLOCK) ON ([mo].[PK_Modules] = [mp].[FK_Modules])
	INNER JOIN [dbo].[FileNames] AS [sfn] WITH(NOLOCK) ON ([sfn].[PK_FileNames] = [mp].[FK_FileNames])
	INNER JOIN [dbo].[paths] AS [sp] WITH(NOLOCK) ON ([sp].[pk_paths] = [mp].[fk_paths])
WHERE 
	--r'(explorer.exe|iexplore.exe|svchost.exe|ctfmon.exe|dllhost.exe)' : 'reservedNames.txt',
	([se].[FileName__TargetProcessImageFileName] = N'explorer.exe' AND [se].[Path__TargetProcessPathName] <> N'C:\Windows\')
	OR
	([se].[FileName__TargetProcessImageFileName] = N'iexplore.exe' AND ([se].[Path__TargetProcessPathName] <> N'C:\Program Files (x86)\Internet Explorer\' AND [se].[Path__TargetProcessPathName] <> N'C:\Program Files\Internet Explorer\'))
	OR
	([se].[FileName__TargetProcessImageFileName] = N'svchost.exe' AND ([se].[Path__TargetProcessPathName] <> N'C:\Windows\System32\' AND [se].[Path__TargetProcessPathName] <> N'C:\Windows\SysWOW64\'))
	OR
	([se].[FileName__TargetProcessImageFileName] = N'ctfmon.exe' AND ([se].[Path__TargetProcessPathName] <> N'C:\Windows\System32\' AND [se].[Path__TargetProcessPathName] <> N'C:\Windows\SysWOW64\'))
	OR
	([se].[FileName__TargetProcessImageFileName] = N'dllhost.exe' AND ([se].[Path__TargetProcessPathName] <> N'C:\Windows\System32\' AND [se].[Path__TargetProcessPathName] <> N'C:\Windows\SysWOW64\'))

--order by EventUTCTime desc