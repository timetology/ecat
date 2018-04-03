SELECT
	[mn].[MachineName]
	,[mn].[OperatingSystem]
	,[md].[RemotePath]
	,[md].[RemoteFileName]
	,[md].[AuditUTCDate]
	,[md].[RelativeFileName]

FROM uvw_MachineDownloaded as md
INNER JOIN [dbo].[Machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [md].[FK_Machines] 

WHERE
	md.RemoteFileName = N'NTUSER.DAT'
	AND md.error = '0'
	order by AuditUTCDate Desc