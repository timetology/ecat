select md.RemoteFileName as 'Summary of RMT download Filenames Completed', count(*) as 'count'
FROM uvw_MachineDownloaded as md
WHERE
	md.AuditUTCDate >= DateAdd(hh, -24, GETDATE()) AND

(md.RemoteFileName = N'sethc.exe'
OR md.RemoteFileName = N'utilman.exe'
OR md.RemoteFileName = N'osk.exe'
OR md.RemoteFileName = N'magnify.exe'
OR md.RemoteFileName = N'narrator.exe'
OR md.RemoteFileName = N'DisplaySwitch.exe'
OR md.RemoteFileName = N'AtBroker.exe')
   group by md.RemoteFileName
   order by 'count' desc

SELECT
	mn.MachineName
	,mn.localip
	,mn.OperatingSystem
	,md.RemotePath
	,md.RemoteFileName
	,md.AuditUTCDate
	,md.RelativeFileName
	,CONCAT(mo.size, nmo.size) as SIZE
	--,mo.size
	--,nmo.size
	--,mo.FirstSeenUTCDate
	,mo.PEUTCTimeDateStamp
	,mo.Description
  	,convert(binary(16),mo.HashMD5) AS MD5
  	,convert(binary(20),mo.HashSHA1) AS SHA1
  	,convert(binary(32),mo.HashSHA256) AS SHA256 
	--,mo.HashMD5
	--,nmo.HashMD5
	--,convert(binary(16),nmo.HashMD5) AS NonModuleMD5
  
FROM uvw_MachineDownloaded as md
LEFT JOIN [dbo].[Machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [md].[FK_Machines]
LEFT JOIN uvw_modules as mo WITH(NOLOCK) ON md.fk_Modules = mo.pk_Modules
LEFT JOIN uvw_NonModules as nmo WITH(NOLOCK) ON md.fk_NonModules = nmo.pk_NonModules


WHERE
	--md.RemoteFileName = N'<<<<FILENAME___HERE>>>>'
	-- Last 24 hours
	md.AuditUTCDate >= DateAdd(hh, -24, GETDATE())
	AND
(md.RemoteFileName = N'sethc.exe'
OR md.RemoteFileName = N'utilman.exe'
OR md.RemoteFileName = N'osk.exe'
OR md.RemoteFileName = N'magnify.exe'
OR md.RemoteFileName = N'narrator.exe'
OR md.RemoteFileName = N'DisplaySwitch.exe'
OR md.RemoteFileName = N'AtBroker.exe')
	
	--order by MachineName,AuditUTCDate desc
	--order by AuditUTCDate desc
	--order by MD5
	--order by [md].[RemoteFileName]
