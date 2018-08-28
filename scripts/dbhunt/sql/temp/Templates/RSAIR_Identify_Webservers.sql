SELECT DISTINCT
     MA.MachineName,
     ISNULL(ADM.Description,‘None’) AS AdminStatus,
      CASE
        WHEN MP.NetworkListen = 1 THEN ‘Listening’
        WHEN MP.NetworkListen = 0 THEN ‘Not Listening’
      END AS ‘Listening’,
     FN2.FileName AS Module,
     FN.FileName AS Process,
     LA.LaunchArguments,
     DO.Domain,
     NA.Port,
     NA.TotalSent,
     NA.TotalReceived,    
     NA.IP,
     NA.UserAgent,
     MP.MarkedAsDeleted,
     MB.BiasStatus,
     MP.FileADS,
     MA.OperatingSystem
     
FROM
     dbo.mocNetAddresses AS NA WITH(NOLOCK)
     left JOIN dbo.MachineModulePaths AS MP WITH(NOLOCK) ON MP.PK_MachineModulePaths = NA.FK_MachineModulePaths
     INNER JOIN dbo.FileNames AS FN WITH(NOLOCK) ON FN.PK_FileNames = NA.FK_FileNames__Process
     INNER JOIN dbo.Domains AS DO WITH(NOLOCK) ON DO.PK_Domains = NA.FK_Domains__DomainHost
     INNER JOIN dbo.FileNames AS FN2 WITH(NOLOCK) ON FN2.PK_FileNames = MP.FK_FileNames
     INNER JOIN dbo.ModuleBiasStatus AS MB WITH(NOLOCK) ON MB.FK_Modules = MP.FK_Modules
     INNER JOIN dbo.Machines AS MA WITH(NOLOCK)  ON MA.PK_Machines = NA.FK_Machines
     INNER JOIN dbo.LaunchArguments AS LA WITH(NOLOCK) ON LA.PK_LaunchArguments = NA.FK_LaunchArguments
     LEFT JOIN dbo.MachineAdminInfo AS MAI WITH(NOLOCK) ON MAI.FK_Machines = MA.PK_Machines
     LEFT JOIN dbo.AdminStatus AS ADM  WITH(NOLOCK) ON ADM.PK_AdminStatus = MAI.FK_AdminStatus

WHERE
    MP.NetworkListen = ‘True’
    AND NA.Port IN (‘80’,‘443’)
    AND NA.IP = ‘0.0.0.0’
    AND OperatingSystem LIKE N’%server%'
    /*Toggle this on and off as you see fit */
    AND FN2.FileName != ‘skype.exe’

ORDER BY MachineName asc