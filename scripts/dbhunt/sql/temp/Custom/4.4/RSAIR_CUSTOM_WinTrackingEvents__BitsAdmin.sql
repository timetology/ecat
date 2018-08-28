--bitsadmin
/*
bitsadmin for persistence:
1.bitsadmin /rawreturn /create NBA
2.bitsadmin /rawreturn /addfile NBA c:\windows\system32\user32.dll c:\temp\a.gif
3.bitsadmin /rawreturn /setnotifycmdline NBA "cmd.exe" "cmd.exe"
4.bitsadmin /rawreturn /setpriority NBA high
5.bitsadmin /resume NBA
*/

SELECT  mn.MachineName, 
		se.EventUTCTime, 
		pa.Path as 'SourcePath', 
		fn.Filename as 'SourceFile', 
		se.Path_Target, 
		se.FileName_Target, 
		se.LaunchArguments_Target, 
		la.LaunchArguments as 'SourceArguments',
		se.Username
FROM
	--[dbo].[WinTrackingEventsCache] AS [se] WITH(NOLOCK)
	[dbo].[WinTrackingEvents_P0] AS [se] WITH(NOLOCK)
	--[dbo].[WinTrackingEvents_P1] AS [se] WITH(NOLOCK)
	INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [se].[FK_MachineModulePaths])
	--INNER JOIN [dbo].[Modules] AS [mo] WITH(NOLOCK) ON ([mo].[PK_Modules] = [mp].[FK_Modules])
	INNER JOIN [dbo].[FileNames] AS [fn] WITH(NOLOCK) ON ([fn].[PK_FileNames] = [mp].[FK_FileNames])
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [se].[FK_Machines]
	--INNER JOIN [dbo].[LinkedServers] AS [ls] WITH(NOLOCK) ON [ls].[PK_LinkedServers] = [mn].[FK_LinkedServers] 
	INNER JOIN [dbo].[LaunchArguments] AS [la] WITH(NOLOCK) ON [la].[PK_LaunchArguments] = [se].[FK_LaunchArguments__SourceCommandLine]
    INNER JOIN [dbo].[paths] as [pa] with(NOLOCK) on [mp].[FK_Paths] = [pa].[PK_Paths]
WHERE 

fn.Filename = N'bitsadmin.exe'
OR se.FileName_Target = N'bitsadmin.exe'

UNION 

SELECT  mn.MachineName, 
		se.EventUTCTime, 
		pa.Path as 'SourcePath', 
		fn.Filename as 'SourceFile', 
		se.Path_Target, 
		se.FileName_Target, 
		se.LaunchArguments_Target, 
		la.LaunchArguments as 'SourceArguments',
		se.Username
FROM
	--[dbo].[WinTrackingEventsCache] AS [se] WITH(NOLOCK)
	--[dbo].[WinTrackingEvents_P0] AS [se] WITH(NOLOCK)
	[dbo].[WinTrackingEvents_P1] AS [se] WITH(NOLOCK)
	INNER JOIN [dbo].[MachineModulePaths] AS [mp] WITH(NOLOCK) ON ([mp].[PK_MachineModulePaths] = [se].[FK_MachineModulePaths])
	--INNER JOIN [dbo].[Modules] AS [mo] WITH(NOLOCK) ON ([mo].[PK_Modules] = [mp].[FK_Modules])
	INNER JOIN [dbo].[FileNames] AS [fn] WITH(NOLOCK) ON ([fn].[PK_FileNames] = [mp].[FK_FileNames])
	INNER JOIN [dbo].[machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [se].[FK_Machines]
	--INNER JOIN [dbo].[LinkedServers] AS [ls] WITH(NOLOCK) ON [ls].[PK_LinkedServers] = [mn].[FK_LinkedServers] 
	INNER JOIN [dbo].[LaunchArguments] AS [la] WITH(NOLOCK) ON [la].[PK_LaunchArguments] = [se].[FK_LaunchArguments__SourceCommandLine]
    INNER JOIN [dbo].[paths] as [pa] with(NOLOCK) on [mp].[FK_Paths] = [pa].[PK_Paths]
WHERE 

fn.Filename = N'bitsadmin.exe'
OR se.FileName_Target = N'bitsadmin.exe'