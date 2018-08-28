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
	
	[pn].[FileName] LIKE N'powershell.exe'
	AND [na].[IP] NOT LIKE '172.1[6-9].%'
	AND [na].[IP] NOT LIKE '172.2[0-9].%'
	AND [na].[IP] NOT LIKE '172.3[0-1].%'
	AND [na].[IP] NOT LIKE '10.%'
	AND [na].[IP] NOT LIKE '192.168%'
	AND [na].[IP] NOT LIKE '127.0.0.1'

	AND [dom].[Domain] NOT LIKE '%.microsoft.com'
	AND [dom].[Domain] NOT LIKE '%.windowsupdate.com'
	AND [dom].[Domain] NOT LIKE '%.verisign.com'
	AND [dom].[Domain] NOT LIKE '%.geotrust.com'
	AND [dom].[Domain] NOT LIKE '%.windows.com'
	AND [dom].[Domain] NOT LIKE '%.digicert.com'
	AND [dom].[Domain] NOT LIKE ''
	AND [dom].[Domain] NOT LIKE '%office365.com'
	AND [dom].[Domain] NOT LIKE '%.outlook.com'
	AND [dom].[Domain] NOT LIKE '%.public-trust.com'
	-- AND [dom].[Domain] NOT LIKE '%COMPANY.com'
	
	