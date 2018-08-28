-- Find all svchost.exe executions where services.exe was not the parent
-- proc1 is the child, and proc2 is the parent: where parent != services.exe and child = svchost.exe
SELECT DISTINCT mn.MachineName as Machine, fn_child.FileName as Child, fn_parent.FileName as Parent, proc_child.Pid, proc_parent.Pid


FROM

[dbo].[mocProcesses] as [proc_child] WITH(NOLOCK)
INNER JOIN [dbo].[MachineModulePaths] as [mmp_child] WITH(NOLOCK) ON ([proc_child].[FK_MachineModulePaths] = [mmp_child].[PK_MachineModulePaths])
INNER JOIN [dbo].[FileNames] as [fn_child] WITH(NOLOCK) ON ([mmp_child].[FK_FileNames] = [fn_child].[PK_FileNames])
INNER JOIN [dbo].[mocProcesses] as [proc_parent] WITH(NOLOCK) ON ([proc_child].[ParentPid] = [proc_parent].[Pid])
INNER JOIN [dbo].[MachineModulePaths] as [mmp_parent] WITH(NOLOCK) ON ([proc_parent].[FK_MachineModulePaths] = [mmp_parent].[PK_MachineModulePaths])
INNER JOIN [dbo].[FileNames] as [fn_parent] WITH(NOLOCK) ON ([mmp_parent].[FK_FileNames] = [fn_parent].[PK_FileNames])
INNER JOIN [dbo].[Machines] as [mn] WITH(NOLOCK) ON ([mn].[PK_Machines] = [mmp_child].[FK_Machines])


WHERE 

[fn_child].[FileName] = 'svchost.exe' 

AND

[fn_parent].[FileName] <> 'services.exe'