SELECT
	mn.MachineName
	--,se.EventUTCTime
  ,CONVERT(VARCHAR, SE.EventUTCTime,120) AS eventutctime, 
	--,sfn.FileName
	,se.Path__TargetProcessPathName
	,se.FileName__TargetProcessImageFileName
  ,se.Target
	,se.SourceCommandLine
	,se.TargetCommandLine
  ,se.UserName
  ,se.Pid
  ,se.IP
  ,convert(binary(32),se.HashSHA256) AS HashSHA256 
  ,convert(binary(32),se.HashSHA256__Target) AS SHA256 
  
FROM [dbo].[uvw_mocSentinelEvents] AS [se] WITH(NOLOCK)
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [se].[FK_Machines] 
	--INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [se].[FK_MachineModulePaths])
	--INNER JOIN [dbo].[FileNames] AS [sfn] WITH(NOLOCK) ON ([sfn].[PK_FileNames] = [mp].[FK_FileNames])
  --INNER JOIN [dbo].[Modules] AS [mo] WITH(NOLOCK) ON ([mo].[PK_Modules] = [mp].[FK_Modules])

WHERE 
