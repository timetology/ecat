SELECT mn.machineName, sfn.filename, pa2.Path, la.LaunchArguments, sn.servicename, sndn.servicename as 'Service Display Name'

FROM

	[dbo].[mocServices] AS [ms] WITH(NOLOCK)
	INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [ms].[FK_MachineModulePaths])
	INNER JOIN [dbo].[FileNames] AS [sfn] WITH(NOLOCK) ON ([sfn].[PK_FileNames] = [mp].[FK_FileNames])
	INNER JOIN [dbo].[Paths] AS [pa2] WITH(NOLOCK) ON [pa2].[PK_Paths] = [mp].[FK_Paths]
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [ms].[FK_Machines] 
	INNER JOIN [dbo].[LaunchArguments] AS [la] WITH(NOLOCK) ON ([la].[PK_LaunchArguments] = [ms].[FK_LaunchArguments])
	INNER JOIN [dbo].ServiceNames as [sn] WITH(NOLOCK) ON sn.PK_ServiceNames = ms.FK_ServiceNames
	INNER JOIN [dbo].ServiceNames as [sndn] WITH(NOLOCK) ON sndn.PK_ServiceNames = ms.FK_ServiceNames__DisplayName
WHERE
(
	pa2.path LIKE '%:\windows\system32\_\' OR
	pa2.path LIKE '%:\windows\system32\__\' OR
	pa2.path LIKE '%:\windows\system32\___\' OR
	(pa2.path LIKE '%:\windows\system32\____\'
		AND (
			pa2.path NOT LIKE '%:\windows\system32\wbem\' AND
			(sfn.filename NOT LIKE 'WMIsvc.dll' OR
			sfn.filename NOT LIKE 'WMIAPSRV.EXE')
			)
	) 
	--OR
	--pa2.path LIKE '%:\windows\system32\_____\' OR
	--pa2.path LIKE '%:\windows\system32\______\' OR
	--pa2.path LIKE '%:\windows\system32\_______\'
)

	-- FILTER --
	AND pa2.path NOT LIKE '%:\windows\system32\WAT\'
	
