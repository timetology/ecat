--SHIMALIZER - SourcePath WebFolders

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
	--r'(tomcat|inetpub|wwwroot|webapps|clientaccess)' : 'webFolders.txt',
	[sp].[path] LIKE '%\tomcat\%'
	OR [sp].[path] LIKE '%\inetpub\%'
	OR [sp].[path] LIKE '%\wwwroot\%'
	OR [sp].[path] LIKE '%\webapps\%'
	OR [sp].[path] LIKE '%\clientaccess\%'

	
--order by EventUTCTime desc