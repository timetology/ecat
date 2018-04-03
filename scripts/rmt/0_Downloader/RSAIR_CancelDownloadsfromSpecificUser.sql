UPDATE [dbo].[MachineCommands]
SET [dbo].[MachineCommands].[Canceled] = 1, [dbo].[MachineCommands].[Processed] = 1
WHERE 
[dbo].[MachineCommands].[UserName] = 'ANALYST_USERNAME' 
AND [dbo].[MachineCommands].[Type] = 256  
AND [dbo].[MachineCommands].[Processed] = 0