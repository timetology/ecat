SELECT
mn.machinename
,mc.Processed
,mc.CreateUTCTime
,mc.ProcessUTCTime
,mc.Comment
,mc.IsAutomatic
,mc.RetrieveCount
,mc.UserName
,mc.WorkStation
,mc.RetrieveUTCTime
,mc.Canceled
,mc.CancelUserName
,mc.ErrorMessage
,mc.ErrorCode
,mc.MachineCommandError
from uvw_MachineCommands as mc
LEFT JOIN [dbo].[Machines] AS [mn] WITH(NOLOCK) ON [mn].[PK_Machines] = [mc].[FK_Machines]
WHERE
mc.Comment LIKE 'Download RSA rmt_0_downloader_windows %'
AND mc.Type = 256  
AND mc.Processed = 0
