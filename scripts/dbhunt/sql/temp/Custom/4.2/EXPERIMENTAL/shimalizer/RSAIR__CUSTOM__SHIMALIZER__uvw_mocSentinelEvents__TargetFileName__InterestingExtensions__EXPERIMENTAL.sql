--SHIMALIZER - Interesting Extensions

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
--(\.bin,|\.dat,|\.log,|\.gif,|\.txt,|\.jpg,|\.rar,|\.tar,|\.sql,|\.zip,)
	[se].[FileName__TargetProcessImageFileName] LIKE '%.bin'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.dat'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.log'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.txt'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.gif'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.jpg'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.png'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.rar'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.tar'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.tar.gz'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.zip'
	OR [se].[FileName__TargetProcessImageFileName] LIKE '%.sql'

--order by EventUTCTime desc