------------------------------------------------------------------------------------------------------------
---Color-Con Produccion
------------------------------------------------------------------------------------------------------------

USE scisaframework_cfdi;
GO

PRINT 'DATOS LICENCIA'
-- LICENSE GestorCFDI
INSERT [dbo].[Scisa_ApplicationsLicenses] ([ApplicationID], [LicenseIssueDate], [LicenseType], [LicensedTo], [LicensedToData], [LicenseKey]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', CAST(N'2026-9-30' AS Date), 2, N'COLOR-CON DE MEXICO', N'100', N'IO/5-YWCF-VSQ0-OYLM-WYPT-BN1I-M+XC')
GO
-- LICENSE FWK
INSERT [dbo].[Scisa_ApplicationsLicenses] ([ApplicationID], [LicenseIssueDate], [LicenseType], [LicensedTo], [LicensedToData], [LicenseKey]) VALUES (N'fa559889-8a43-4d83-b5f9-517f8a920066', CAST(N'2026-9-30' AS Date), 2, N'COLOR-CON DE MEXICO', N'100', N'R/AD-CGXS-QUAC-96VH-7XKY-CSLM-8NBJ')
GO

-- Conexion
INSERT [dbo].[Scisa_ApplicationConfigurationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'ConnectionInfo', N'S92qDNNn9EmxLUtTnGXrwNTVmMa1jNazBXdyn/1poMynrcf/kRPas0Y+1AJhOYcVMlmZG/YRIBQ8XWqdRh5cH9IjqUdu0dxUfDTHAHIsSKknsskSnQIQZ1ppwgjKdOZrzemXkihnRPSQR1vwrFOIgj1ZoCx2Zgbh0W1m/OAq3Sc=')
GO

PRINT 'DATOS DE FWK'

INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'CfdiFilePath', N'E:\SCISA\GestorCFDI\Files\{0}\')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'CfdiCancellationFilePath', N'E:\SCISA\GestorCFDI\Cancellation\{0}\')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'CfdiInvalidFilePath', N'E:\SCISA\GestorCFDI\Invalid\')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'CfdiPendingFilePath', N'E:\SCISA\GestorCFDI\Pending\')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'CfdiUploadFilePath', N'E:\SCISA\GestorCFDI\Upload\')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'BackupCsvBlFilePath', N'E:\SCISA\GestorCFDI\ListasNegras\')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'CfdiPendingReceptionFilePath', N'E:\SCISA\GestorCFDI\PendingReception\')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailInternalGeneralControl', N'Facturacion@colorcon.com') 
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailAddressErrorControl', N'Facturacion@colorcon.com')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailPasswordErrorControl', N'XWaFphX+gko=')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailErrorControlEnableSSL', N'False')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailErrorControlServer', N'smtpus.colorcon.com')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailErrorControlServerPort', N'25')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailErrorControlUsername', N'XWaFphX+gko=') --Encrypted Email
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'ReceiveValidXmlConfirmation', N'0')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'ReceiveInvalidXmlConfirmation', N'0')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'DisableShowPermission', N'true')
--V4
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value])      VALUES
           ('4196E2BF-4FA6-4551-8C28-2ED5B36B56D2','','MaxCFDISTake'
           ,'1000') --Se puede jugar con este valor para cambiar la cantidad e CFDIs permitidos por peticion de actualizacion
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES ('4196E2BF-4FA6-4551-8C28-2ED5B36B56D2', NULL, 'AttemptToUpload', '3')
INSERT [dbo].[Scisa_ApplicationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES ('4196E2BF-4FA6-4551-8C28-2ED5B36B56D2', NULL, 'TimeToUpload', '3000')
GO
INSERT [dbo].[Scisa_ApplicationConfigurationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailAddress', N'Facturacion@colorcon.com')
INSERT [dbo].[Scisa_ApplicationConfigurationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailEnableSSL', N'False')
INSERT [dbo].[Scisa_ApplicationConfigurationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailPassword', N'XWaFphX+gko=')
INSERT [dbo].[Scisa_ApplicationConfigurationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailServer', N'smtpus.colorcon.com')
INSERT [dbo].[Scisa_ApplicationConfigurationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailServerPort', N'25')
INSERT [dbo].[Scisa_ApplicationConfigurationSettings] ([ApplicationID], [Context], [Property], [Value]) VALUES (N'4196e2bf-4fa6-4551-8c28-2ed5b36b56d2', NULL, N'OutgoingMailUsername', N'XWaFphX+gko=') --Encrypted Email
GO

PRINT 'DATOS APP'

-- SE INCLUYE EL CORREO AL FINAL DEL CATENTITY Y SE ENCRIPTA LA LICENCIA DEL SDK
USE efact_cfdi;
GO
SET IDENTITY_INSERT [dbo].[CatEntity] ON 
GO
INSERT [dbo].[CatEntity] ([EntityID], [RFC], [Name], [MailTemplateID], [IsLegalPerson], [IsForeign], [IsActive], [DateCreated], [CreatedBy], [DateUpdated], [UpdatedBy], [SDKLicense], [IncomingMailReception]) VALUES (1, N'CME9906177E9', N'COLOR-CON DE MEXICO', 1, 1, 1, 1, GETDATE(), N'SYSADM', GETDATE(), N'SYSADM', 'H/AU0LaUUZaXaL/H562w9tsNaUCns9Fc3z628Luon19DH3gZVGqh90MW9tLqOnUwzh7b2qfYtC/zIu4ywY3BICFAmPsehjU3sYmOxH/s0wVJuJXXGUgK4QEPGhjB/D5uhxI7On4epPTvfD/e63BsG7Sgs90iKBpym5yaUP3C8iU=', 'Facturacion@colorcon.com')

GO
SET IDENTITY_INSERT [dbo].[CatEntity] OFF
GO

-- Se hace un insert por cada RFC (se modifica el numerado de UserEntity y EntityID)

SET IDENTITY_INSERT [dbo].[CfgRFCAuthorizedRelation] ON
GO
INSERT [dbo].[CfgRFCAuthorizedRelation] ([UserEntityRelationID], [UserID], [EntityID], [DateCreated], [CreatedBy], [DateUpdated], [UpdatedBy]) VALUES (1, '387B6376-5FA9-4953-A909-203DC9A426BF', 1, GETDATE(), N'SYSADM', GETDATE(), N'SYSADM')

GO
SET IDENTITY_INSERT [dbo].[CfgRFCAuthorizedRelation] OFF
GO

SET IDENTITY_INSERT [dbo].[CatScheduledTaskType] ON
GO
PRINT 'ADDING 4 JOBS'
INSERT [dbo].[CatScheduledTaskType] ([ScheduledTaskTypeID], [TaskCode], [TaskType], [TaskSubType], [TaskCategoryCode], [IsActive]) VALUES (1, N'UploadParser', NULL, NULL, N'GestorCFDI', 1)
GO
INSERT [dbo].[CatScheduledTaskType] ([ScheduledTaskTypeID], [TaskCode], [TaskType], [TaskSubType], [TaskCategoryCode], [IsActive]) VALUES (2, N'CFDIMailSender', NULL, NULL, N'GestorCFDI', 1)
GO
INSERT [dbo].[CatScheduledTaskType] ([ScheduledTaskTypeID], [TaskCode], [TaskType], [TaskSubType], [TaskCategoryCode], [IsActive]) VALUES (3, N'RegenerateCFDI', NULL, NULL, N'GestorCFDI', 1)
GO
INSERT [dbo].[CatScheduledTaskType] ([ScheduledTaskTypeID], [TaskCode], [TaskType], [TaskSubType], [TaskCategoryCode], [IsActive]) VALUES (4, N'RefreshStatusSAT', NULL, NULL, N'GestorCFDI', 1)
GO
SET IDENTITY_INSERT [dbo].[CatScheduledTaskType] OFF
GO

INSERT [dbo].[CfgScheduledTask] ([ScheduledTaskID], [ScheduledTaskTypeID], [Frequency], [StartHour], [EndHour], [Days], [IsActive], [DateCreated], [CreatedBy], [DateUpdated], [UpdatedBy]) VALUES (1, 1, 1, CAST(N'09:00:00' AS Time), CAST(N'10:00:00' AS Time), NULL, 1, GETDATE(), N'SYSADM', GETDATE(), N'SYSADM')
GO
INSERT [dbo].[CfgScheduledTask] ([ScheduledTaskID], [ScheduledTaskTypeID], [Frequency], [StartHour], [EndHour], [Days], [IsActive], [DateCreated], [CreatedBy], [DateUpdated], [UpdatedBy]) VALUES (2, 2, 8, CAST(N'09:00:00' AS Time), CAST(N'10:00:00' AS Time), NULL, 1, GETDATE(), N'SYSADM', GETDATE(), N'SYSADM')
GO
INSERT [dbo].[CfgScheduledTask] ([ScheduledTaskID], [ScheduledTaskTypeID], [Frequency], [StartHour], [EndHour], [Days], [IsActive], [DateCreated], [CreatedBy], [DateUpdated], [UpdatedBy]) 
VALUES (3, 3, 8, CAST(N'09:00:00' AS Time), CAST(N'10:00:00' AS Time), NULL, 1, GETDATE(), N'SYSADM', GETDATE(), N'SYSADM')
GO
INSERT [dbo].[CfgScheduledTask] ([ScheduledTaskID], [ScheduledTaskTypeID], [Frequency], [StartHour], [EndHour], [Days], [IsActive], [DateCreated], [CreatedBy], [DateUpdated], [UpdatedBy]) 
VALUES (4, 4, 8, CAST(N'09:00:00' AS Time), CAST(N'23:00:00' AS Time), NULL, 1, GETDATE(), N'SYSADM', GETDATE(), N'SYSADM')
GO

/*------------------------------------------------------------------*/
Print 'Insertando plantillas'

--Esta primera solo se inserta 1 vez

INSERT [dbo].[CfgMailTemplates] ([EntityID], [Name], [Subject], [Body], [IsActive]) VALUES (1, 'InvalidFile', 'Error al cargar un archivo.', 'El archivo de nombre: "{0}" no fue posible procesarlo, se envió a la carpeta configurada para "<b>Invalid</b>".', 1)

--Estos 5 se deben insertar para cada entidad (RFC) y se modifica el numero del EntityID

INSERT [dbo].[CfgMailTemplates] ([EntityID], [Name], [Subject], [Body], [IsActive]) VALUES (1, 'CFDIStored', 'CFDI cargado al portal exitosamente.', '<div>SIGLO/GestorCFDI recibió el siguiente CFDI:</div><div><b>UUID</b>: {0}</div><div><b>RFCEmisor</b>: {1}</div><div><b>RFCReceptor</b>: {2}</div><div><br></div><div>Obteniendo las siguientes validaciones:</div><div><b>Versión 4.0</b>: {3}</div><div><b>Importes</b>: {4}</div><div><b>Estatus en SAT</b>: {5}</div><div><b>Sello</b>: {6}</div><div><b>Lista Negra</b>: {7}</div><div><b>Estructura</b>: {8}</div><div>Si no pasó alguna validación, el documento no se registrará en nuestro portal</div>', 1)
INSERT [dbo].[CfgMailTemplates] ([EntityID], [Name], [Subject], [Body], [IsActive]) VALUES (1, 'CFDIRejected', 'Problema al cargar CFDI.', '<div>SIGLO/GestorCFDI recibió el siguiente CFDI:</div><div><b>UUID</b>: {0}</div><div><b>RFCEmisor</b>: {1}</div><div><b>RFCReceptor</b>: {2}</div><div>El archivo fue enviado a la ruta configurada para <b>Pending Reception</b>.</div><div><br></div><div>Obteniendo las siguientes validaciones:</div><div><b>Versión 4.0</b>: {3}</div><div><b>Importes</b>: {4}</div><div><b>Estatus en SAT</b>: {5}</div><div><b>Sello</b>: {6}</div><div><b>Lista Negra</b>: {7}</div><div><b>Estructura</b>: {8}</div><div>Si no pasó alguna validación, el documento no se registrará en nuestro portal</div>', 1)
INSERT [dbo].[CfgMailTemplates] ([EntityID], [Name], [Subject], [Body], [IsActive]) VALUES (1, 'SendReceptionRecord', 'Revisión de CFDI','<div>SIGLO/GestorCFDI recibió el siguiente CFDI:</div><div><b>UUID</b>: {0}</div><div><b>RFCEmisor</b>: {1}</div><div><b>RFCReceptor</b>: {2}</div><div><br></div><div>Obteniendo las siguientes validaciones:</div><div><b>Versión 4.0</b>: {3}</div><div><b>Importes</b>: {4}</div><div><b>Estatus en SAT</b>: {5}</div><div><b>Sello</b>: {6}</div><div><b>Lista Negra</b>: {7}</div><div><b>Estructura</b>: {8}</div><div>Si no pasó alguna validación, el documento no se registrará en nuestro portal</div>', 1)
INSERT [dbo].[CfgMailTemplates] ([EntityID], [Name], [IsActive]) VALUES (1, 'SendEmissionAttachments', 1)
INSERT [dbo].[CfgMailTemplates] ([EntityID], [Name], [IsActive]) VALUES (1, 'SendReceptionAttachments', 1)







