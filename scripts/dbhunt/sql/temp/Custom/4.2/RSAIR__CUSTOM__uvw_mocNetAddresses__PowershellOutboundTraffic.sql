--Powershell Outbound traffic

SELECT 
	mn.MachineName
	,[na].[FirstConnectionUTC]
	,[na].[LastConnectionUTC]
	,[na].[Path__Process]
	,[na].[FileName__Process]
	,[na].[LaunchArguments]
	,[na].[Protocol]
	,[na].[Port]
	,[na].[IP]
	,[na].[Domain__DomainHost]
	,[na].[UserAgent]
	,[na].[TotalSent]
	,[na].[TotalReceived]
	,[na].[ConnectCount]
	,[na].[FailConnectCount]
	,[na].[BurstCount]
	,[na].[BurstIntervalMean]
	,[na].[BurstIntervalDeviation]
	,[na].[NonRoutable]

FROM
	[dbo].[uvw_mocNetAddresses] AS [na] WITH(NOLOCK)
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [na].[FK_Machines]
WHERE
	[na].[FileName__Process] LIKE 'powershell.exe'
	AND [na].[IP] NOT LIKE '172.1[6-9].%'
	AND [na].[IP] NOT LIKE '172.2[0-9].%'
	AND [na].[IP] NOT LIKE '172.3[0-1].%'
	AND [na].[IP] NOT LIKE '10.%'
	AND [na].[IP] NOT LIKE '192.168%'
	AND [na].[IP] NOT LIKE '127.0.0.1'

	AND [na].[Domain__DomainHost] NOT LIKE '%.microsoft.com'
	AND [na].[Domain__DomainHost] NOT LIKE '%.windowsupdate.com'
	AND [na].[Domain__DomainHost] NOT LIKE '%.verisign.com'
	AND [na].[Domain__DomainHost] NOT LIKE '%.geotrust.com'
	AND [na].[Domain__DomainHost] NOT LIKE '%.windows.com'
	AND [na].[Domain__DomainHost] NOT LIKE '%.digicert.com'
	AND [na].[Domain__DomainHost] NOT LIKE ''
	AND [na].[Domain__DomainHost] NOT LIKE '%office365.com'
	AND [na].[Domain__DomainHost] NOT LIKE '%.outlook.com'
	AND [na].[Domain__DomainHost] NOT LIKE '%.public-trust.com'
	-- AND [na].[Domain__DomainHost] NOT LIKE '%COMPANY.com'