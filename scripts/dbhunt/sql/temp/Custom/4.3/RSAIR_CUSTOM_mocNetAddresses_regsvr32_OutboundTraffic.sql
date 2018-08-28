SELECT 
mn.MachineName, 
na.FirstConnectionUTC, 
na.LastConnectionUTC, 
pn.Filename, 
sfn.Filename, 
na.Port, 
dom.Domain, 
na.IP, 
na.UserAgent, 
LaunchArguments


FROM
    [dbo].[mocNetAddresses] AS [na] WITH(NOLOCK)
	LEFT JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [na].[FK_MachineModulePaths])
	LEFT JOIN [dbo].[FileNames] AS [sfn] WITH(NOLOCK) ON ([sfn].[PK_FileNames] = [mp].[FK_FileNames])
	LEFT JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [na].[FK_Machines]
	LEFT JOIN [dbo].[Filenames] AS [pn] WITH(NOLOCK) ON ([pn].[PK_FileNames] = [na].[FK_FileNames__Process])
	LEFT JOIN [dbo].[Domains] AS [dom]  WITH(NOLOCK) ON ([dom].[PK_Domains] = [na].[FK_Domains__DomainHost])
	LEFT JOIN [dbo].[LaunchArguments] as [sla] WITH(NOLOCK) ON ([sla].[PK_LaunchArguments] = [na].[FK_LaunchArguments])

WHERE
    

    [pn].[FileName] LIKE 'regsvr32.exe'

	--AND [na].[IP] NOT LIKE 'x.x.%'                            -- Customer Public IP range

	--AND [dom].[Domain] NOT LIKE '%Company.com'                    -- Customer Domain

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
 
    
ORDER BY mn.MachineName