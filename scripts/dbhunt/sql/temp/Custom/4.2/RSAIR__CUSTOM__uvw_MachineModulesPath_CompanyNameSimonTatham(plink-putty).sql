select distinct 
	mp.Filename
	--,mp.path
	--,cn.CompanyName 
	--,mo.Description
from 
uvw_MachineModulePaths as mp
inner join uvw_Modules as mo on mp.fk_modules = mo.pk_modules
inner join uvw_CompanyNames as cn on mo.FK_CompanyNames = cn.PK_CompanyNames
where 
	cn.CompanyName = N'Simon Tatham' 
	--OR 
	--mo.Description like N'%ssh%'