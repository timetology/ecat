SELECT convert(binary(16),mo.HashMD5) AS HashMD5 
      ,CASE 
        WHEN [bs].BiasStatus = -2 THEN 'Blacklisted'
        WHEN [bs].BiasStatus = 0 THEN 'Neutral'
        WHEN [bs].BiasStatus = 1 THEN 'Graylisted'
        WHEN [bs].BiasStatus = 2 THEN 'Whitelisted'
      END AS Status
      , '' AS VTResultRatio
      , '' AS VTResult
      , '' AS VTScanDate
      , '' AS VTResultPositives
      , '' AS VTResultTotal
      , [mp].GlobalMachineCount 
      , substring((
          SELECT TOP 5 '|'+[mn].MachineName AS [text()]
          FROM  [ECAT$PRIMARY].[dbo].[Machines] AS [mn] WITH(NOLOCK) 
          INNER JOIN  [ECAT$PRIMARY].[dbo].[MachinesModules] AS [mm] WITH(NOLOCK) ON ([mn].[PK_Machines] = [mm].[FK_Machines])
          WHERE ([mm].[FK_Modules] = [mo].[PK_Modules]) 
          For XML PATH ('')
          ), 2, 1000) [Machines]
		, CONVERT(VARCHAR, mp.DownloadedUTCTime,120) AS DownloadedUTCTime
--      ,[mo].HashSHA256


      ,'"'+[mp].RemotePath+'"' As RemotePath
      ,'"'+[mp].RemoteFileName+'"' As RemoteFilename

  FROM [ECAT$PRIMARY].[dbo].[Modules] as [mo] WITH(NOLOCK)
  INNER JOIN [ECAT$PRIMARY].[dbo].[ModuleStatistics] AS [mp] WITH(NOLOCK) ON ([mp].[FK_Modules] = [mo].[PK_Modules])
  INNER JOIN [ECAT$PRIMARY].[dbo].[ModuleIOC] AS [mi] WITH(NOLOCK) ON ([mi].[FK_Modules] = [mo].[PK_Modules])
  INNER JOIN [ECAT$PRIMARY].[dbo].[ModuleBiasStatus] AS [bs] WITH(NOLOCK) ON ([bs].[FK_Modules] = [mo].[PK_Modules])

  WHERE ([mi].IOCLevel1 > 0 OR [mi].IOCLevel0 > 0) AND 
        ([mo].ModuleTypeEXE = 1 OR [mo].ModuleTypeDLL =1) AND
        mp.DownloadedUTCTime IS NOT NULL AND
        mp.GlobalMachineCount < 20 AND
        [mo].PK_Modules > 0 
  
 -- ORDER BY [mo].PK_Modules DESC
    ORDER BY mp.DownloadedUTCTime DESC
