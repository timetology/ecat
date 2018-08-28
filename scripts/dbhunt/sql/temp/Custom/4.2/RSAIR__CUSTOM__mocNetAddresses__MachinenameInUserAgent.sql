--Machine Name in User Agent
SELECT mn.MachineName,
 na.FirstConnectionUTC,
 na.LastConnectionUTC,
 pn.filename,
 pa.path,
 na.IP,
 dom.domain,
 na.UserAgent,
 na.TotalSent,
 na.TotalReceived,
 la.LaunchArguments

FROM

	[dbo].[mocNetAddresses] AS [na] WITH(NOLOCK)
	--INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [na].[FK_MachineModulePaths])
	--INNER JOIN [dbo].[FileNames] AS [sfn] WITH(NOLOCK) ON ([sfn].[PK_FileNames] = [mp].[FK_FileNames])
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [na].[FK_Machines]
	INNER JOIN [dbo].[Filenames] AS [pn] WITH(NOLOCK) ON ([pn].[PK_FileNames] = [na].[FK_FileNames__Process])
	INNER JOIN [dbo].[Paths] as [pa] WITH(NOLOCK) ON ([pa].[PK_Paths] = [na].[FK_Paths__Process])
	INNER JOIN [dbo].[Domains] AS [dom]  WITH(NOLOCK) ON ([dom].[PK_Domains] = [na].[FK_Domains__DomainHost])
	INNER JOIN [dbo].[LaunchArguments] as [la] WITH(NOLOCK) ON ([la].[PK_LaunchArguments] = [na].[FK_LaunchArguments])
	
WHERE

	na.UserAgent LIKE '%'+ mn.MachineName + '%' AND LEN(mn.MachineName) > 4
	
	order by LastConnectionUTC desc