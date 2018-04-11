select * from [dbo].[MachineCommands]
WHERE 
[dbo].[MachineCommands].[UserName] = 'ANALYST_USERNAME' 
AND [dbo].[MachineCommands].[Type] = 256  
AND [dbo].[MachineCommands].[Processed] = 0