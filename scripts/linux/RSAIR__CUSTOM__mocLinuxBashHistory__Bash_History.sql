SELECT 
      MachineName
      ,[UserName]
      ,[Command]

 FROM [ECAT$PRIMARY].[dbo].[uvw_mocLinuxBashHistory] as BH
  INNER JOIN dbo.Machines AS MA WITH(NOLOCK) ON MA.AgentID = BH.AgentID