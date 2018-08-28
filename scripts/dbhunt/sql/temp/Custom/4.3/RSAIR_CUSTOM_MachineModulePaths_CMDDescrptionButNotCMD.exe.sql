SELECT
mn.machinename
,sfn.filename
,ofn.filename as 'OriginalFilename'
,pa.path
,mo.Description
,mo.HashMD5
,mo.size
,mo.DaysSinceCompilation
--,mo.DaysSinceCreation
,mp.FileUTCTimeCreated
,mp.FileUTCTimeModified
,mo.NameImportedDlls
,mo.SectionsNames

from dbo.MachineModulePaths as mp
	INNER JOIN dbo.machines as mn with(nolock) on mn.pk_machines = mp.fk_machines
	INNER JOIN dbo.filenames as sfn with(nolock) on sfn.pk_filenames = mp.fk_filenames
	INNER JOIN dbo.modules as mo with(nolock) on mo.pk_modules = mp.fk_modules
	INNER JOIN dbo.paths as pa with(nolock) on pa.pk_paths = mp.fk_paths
	INNER JOIN dbo.filenames as ofn with(nolock) on ofn.pk_filenames = mo.fk_filenames__original
	
where
	mo.description = N'Windows Command Processor'
	AND sfn.filename <> N'cmd.exe'