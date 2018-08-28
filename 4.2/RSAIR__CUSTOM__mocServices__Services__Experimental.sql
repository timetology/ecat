SELECT DISTINCT mn.MachineName, sn.ServiceName, la.LaunchArguments, pa2.Path, sfn.FileName
--SELECT DISTINCT sn.ServiceName, pa2.Path, sfn.FileName
	

FROM

	[dbo].[mocServices] AS [ms] WITH(NOLOCK)
	INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [ms].[FK_MachineModulePaths])
	INNER JOIN [dbo].[FileNames] AS [sfn] WITH(NOLOCK) ON ([sfn].[PK_FileNames] = [mp].[FK_FileNames])
	INNER JOIN [dbo].[Paths] AS [pa2] WITH(NOLOCK) ON [pa2].[PK_Paths] = [mp].[FK_Paths]
	INNER JOIN [dbo].[ServiceNames] AS [sn] WITH(NOLOCK) ON ([sn].[PK_ServiceNames] = [ms].[FK_ServiceNames])
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON ([mn].[PK_Machines] = [ms].[FK_Machines])
	INNER JOIN [dbo].[LaunchArguments] AS [la] WITH(NOLOCK) ON [la].[PK_LaunchArguments] = [ms].[FK_LaunchArguments]
	 
	--INNER JOIN [dbo].[FileNames] AS [tfn] WITH(NOLOCK) ON ([tfn].[PK_FileNames] = [ms].[FK_FileNames__TargetProcessImageFileName])

	/*
	[dbo].[uvw_mocSentinelEvents] AS [se] WITH(NOLOCK)
	INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [se].[FK_MachineModulePaths])
	INNER JOIN [dbo].[FileNames] AS [tfn] WITH(NOLOCK) ON ([tfn].[PK_FileNames] = [se].[FK_FileNames__TargetProcessImageFileName])
	INNER JOIN [dbo].[FileNames] AS [sfn] WITH(NOLOCK) ON ([sfn].[PK_FileNames] = [mp].[FK_FileNames])
	INNER JOIN [dbo].[Paths] AS [pa2] WITH(NOLOCK) ON [pa2].[PK_Paths] = [se].[FK_Paths__TargetProcessPathName]
	
	
	*/
WHERE
	--sn.ServiceName = N'MicrosoftSer'
	--OR sn.ServiceName = N'Remote Service'
	/*
	sfn.filename like '%.exe'
	and pa2.path NOT LIKE '%OfficeSoftwareProtection%'
	and pa2.path NOT LIKE '%windows\ccm\remctrl\'
	and pa2.path NOT LIKE '%windows\system32\%'
	and pa2.path NOT LIKE '%\Microsoft.Net\%'
	and pa2.path NOT LIKE '%\Windows\servicing\%'
	and sn.ServiceName NOT LIKE 'PerfHost'
	*/

	sfn.filename like '%.exe'
	AND
	(pa2.path LIKE '%windows\temp\' OR
	 pa2.path LIKE '%:\windows\_\' OR
	 pa2.path LIKE '%:\windows\__\' OR
	 pa2.path LIKE '%:\windows\___\')

	 AND pa2.path NOT LIKE '%windows\CCM\'
	 
ORDER BY
	pa2.Path


	--Abel
	--syshost32
	--Remote Service