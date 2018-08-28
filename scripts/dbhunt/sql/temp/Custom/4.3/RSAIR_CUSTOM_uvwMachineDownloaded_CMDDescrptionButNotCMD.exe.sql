-- RSAIR__CUSTOM__uvwMachineDownloaded_CMDDescrptionButNotCMD.exe.sql
SELECT
	[mn].[MachineName]
	,mn.localip
	,[mn].[OperatingSystem]
	,[md].[RemotePath]
	,[md].[RemoteFileName]
	,[md].[AuditUTCDate]
	,[md].[RelativeFileName]
	,CONCAT(mo.size, nmo.size) as SIZE
	--,mo.size
	--,nmo.size
	,mo.HashMD5
	--,nmo.HashMD5
	--,mo.FirstSeenUTCDate
	,mo.PEUTCTimeDateStamp
	,mo.Description

FROM uvw_MachineDownloaded as md
LEFT JOIN [dbo].[Machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [md].[FK_Machines]
LEFT JOIN uvw_modules as mo WITH(NOLOCK) ON md.fk_Modules = mo.pk_Modules
LEFT JOIN uvw_NonModules as nmo WITH(NOLOCK) ON md.fk_NonModules = nmo.pk_NonModules


WHERE
	md.RemoteFileName <> N'cmd.exe'
	--AND md.error = '0'
	AND mo.Description = N'Windows Command Processor'
	--order by MachineName,AuditUTCDate desc
	--order by AuditUTCDate desc
	--order by mo.HashMD5
	--order by [md].[RemoteFileName]