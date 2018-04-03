SELECT DISTINCT
		[mn].[MachineName]
	FROM uvw_MachineDownloaded as md
	INNER JOIN [dbo].[Machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [md].[FK_Machines] 
	WHERE
		md.RemoteFileName = N'NTUSER.DAT'