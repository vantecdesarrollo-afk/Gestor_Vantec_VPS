------------------------------------------------------------------------------------------------------------
-- FECHA CREACION:		    25/04/2023
-- PROYECTO Y DESCRIPCION:	SCISA_01885_GESTOR_CFDI_V4.
--							Creacion de tablas:
------------------------------------------------------------------------------------------------------------
PRINT 'GENERANDO TABLAS DE APLICACIÓN GESTORCFDI_V4'

USE efact_cfdi;
--Tabla CatEntity
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'CatEntity' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA CatEntity'
	CREATE TABLE [CatEntity](
	[EntityID] [int] IDENTITY(1,1) NOT NULL,
	[RFC] [varchar](13) NOT NULL,
	[Name] [varchar](200) NOT NULL,
	[MailTemplateID] [int] NULL,
	[LogoID] [varbinary](max) NULL,
	[IsLegalPerson] [int] NOT NULL CONSTRAINT [DF_CatEntity_IsLegalPerson]  DEFAULT ('1'),
	[IsForeign] [int] NOT NULL CONSTRAINT [DF_CatEntity_IsForeign]  DEFAULT ('1'),
	[IsActive] [bit] NOT NULL CONSTRAINT [DF_CatEntity_IsActive]  DEFAULT ('1'),
	[SDKLicense] [varchar](255) NULL,
	[IncomingMailReception] varchar(100) NULL,
	[Version] [timestamp] NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](50) NULL,

 CONSTRAINT [PK_EntityID] PRIMARY KEY CLUSTERED 
(
	[EntityID] ASC
)) ON [PRIMARY]

END
GO

--Tabla CatScheduledTaskType
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'CatScheduledTaskType' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA CatScheduledTaskType'
CREATE TABLE [CatScheduledTaskType](
	[ScheduledTaskTypeID] [int] IDENTITY(1,1) NOT NULL,
	[TaskCode] [varchar](255) NOT NULL,
	[TaskType] [int] NULL,
	[TaskSubType] [int] NULL,
	[TaskCategoryCode] [varchar](255) NULL,
	[IsActive] [bit] NOT NULL CONSTRAINT [DF_CatScheduledTaskType_IsActive]  DEFAULT ('1'),
 CONSTRAINT [PK_ScheduledTaskTypeID] PRIMARY KEY CLUSTERED 
(
	[ScheduledTaskTypeID] ASC
)) ON [PRIMARY]

END
GO

--Tabla CatRFCAuthorizedRelation
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'CfgRFCAuthorizedRelation' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [CfgRFCAuthorizedRelation]'
	CREATE TABLE [CfgRFCAuthorizedRelation](
	[UserEntityRelationID] [int] IDENTITY(1,1) NOT NULL,
	[UserID] [uniqueidentifier] NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
	[EntityID] [int] NOT NULL,
	[Version] [timestamp] NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_UserEntityRelationID] PRIMARY KEY NONCLUSTERED 
(
	[UserEntityRelationID] ASC
)) ON [PRIMARY]

END
GO

--Tabla CatScheduledTask
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'CfgScheduledTask' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [CfgScheduledTask]'
	CREATE TABLE [CfgScheduledTask](
	[ScheduledTaskID] [int] NOT NULL,
	[ScheduledTaskTypeID] [int] NOT NULL,
	[EntityID] [int] NULL,
	[Frequency] [int] NULL,
	[StartHour] [time](7) NULL,
	[EndHour] [time](7) NULL,
	[Days] [varchar](50) NULL,
	[IsActive] [bit] NULL CONSTRAINT [DF_CfgScheduledTask_IsActive]  DEFAULT ('1'),
	[Version] [timestamp] NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_ScheduledTaskID] PRIMARY KEY CLUSTERED 
(
	[ScheduledTaskID] ASC
)) ON [PRIMARY]

END
GO

--Tabla CatScheduledTaskParam
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'CfgScheduledTaskParam' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [CfgScheduledTaskParam]'
	CREATE TABLE [CfgScheduledTaskParam](
	[ScheduledTaskParamID] [int] IDENTITY(1,1) NOT NULL,
	[ScheduledTaskID] [int] NOT NULL,
	[ParamName] [varchar](255) NOT NULL,
	[ParamValue] [varchar](255) NOT NULL,
	[IsActive] [bit] NOT NULL CONSTRAINT [DF_CfgScheduledTaskParam_IsActive] DEFAULT ('1'),
	[Version] [timestamp] NOT NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_ScheduledTaskParamID] PRIMARY KEY CLUSTERED 
(
	[ScheduledTaskParamID] ASC
)) ON [PRIMARY]

END
GO

--Tabla CfgTagSettings
IF not exists (select * from sysobjects ,syscolumns	
                 where sysobjects.name = 'CfgTagSettings' and
                       sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREATE TABLE CfgTagSettings'

	CREATE TABLE CfgTagSettings
	(	TagSettingsID	INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
		EntityID INT NULL,
		ModuleType INT NOT NULL,
		FilterSettingPath VARCHAR(255) NOT NULL,
		FilterSettingTag VARCHAR(50) NOT NULL,
		FilterNumber INT NOT NULL,
		Version timestamp NULL, 
		DateCreated datetime NULL,
		CreatedBy varchar(50) NULL,
		DateUpdated datetime NULL,
		UpdatedBy	VARCHAR(50),
		SearchType INT NOT NULL DEFAULT (0),
		CONSTRAINT FK_EntityID_CatEntity FOREIGN KEY (EntityID) REFERENCES CatEntity(EntityID))

	CREATE UNIQUE INDEX UIDX_CfgTagSettings
	ON CfgTagSettings (EntityID, ModuleType, FilterNumber);

END
GO

--Tabla CatSystemLog
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'SystemLog' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [SystemLog]'
	CREATE TABLE [SystemLog](
	[SystemLogId] [int] IDENTITY(1,1) NOT NULL,
	[EntityName] [varchar](255) NULL,
	[ApplicationName] [varchar](100) NULL,
	[LogUser] [varchar](30) NULL,
	[CorrelationId] [varchar](100) NULL,
	[IP] [varchar](15) NULL,
	[Code] [varchar](70) NULL,
	[Action] [varchar](100) NULL,
	[LogTable] [varchar](40) NULL,
	[AdditionalInfo] [varchar](max) NULL,
	[LogDate] [datetime] NULL,
	[LogHour] [varchar](50) NULL,
	[Operation] [varchar](255) NULL,
	[Portfolio] [varchar](255) NULL,
	[Message360T] [varchar](max) NULL,
	[SystemLogType] [varchar](100) NULL,
	[BusinessReference] [varchar](255) NULL,
 CONSTRAINT [PK_SystemLog] PRIMARY KEY CLUSTERED 
(
	[SystemLogId] ASC
)) ON [PRIMARY]

END
GO

--Tabla TraAttachment
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'TraAttachment' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [TraAttachment]'
	CREATE TABLE [TraAttachment](
	[AttachmentID] [int] IDENTITY(1,1) NOT NULL,
	[AttachmentName] [varchar](max) NOT NULL,
	[AttachmentSize] [bigint] NOT NULL CONSTRAINT [DF_TraAttachment_AttachmentSize]  DEFAULT ((0)),
 CONSTRAINT [PK_AttachmentID] PRIMARY KEY CLUSTERED 
(
	[AttachmentID] ASC
)) ON [PRIMARY]

END
GO

--Tabla TraCFDI
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'TraCFDI' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [TraCFDI]'
	CREATE TABLE [TraCFDI](
	[CFDIID] [int] IDENTITY(1,1) NOT NULL,
	[CFDIUUID] [uniqueidentifier] NOT NULL,
	[Origin] [char](1) NOT NULL,
	[XMLID] [int] NULL,
	[PDFID] [int] NULL,
	[CFDISeries] [varchar](30) NULL,
	[CFDIFolio] [varchar](30) NULL,
	[NumericFolio] [int] NOT NULL,
	[CFDIType] [char](1) NOT NULL,
	[CFDIRFCEmisor] [varchar](13) NOT NULL,
	[CFDIRFCReceptor] [varchar](13) NOT NULL,
	[CFDIEmitionDate] [datetime] NULL,
	[CFDIStampingDate] [datetime] NULL,
	[CFDISubTotal] [numeric](22, 6) NULL,
	[CFDITotal] [numeric](22, 6) NULL,
	[CFDIDiscount] [numeric](22, 6) NULL,
	[CFDIVersion] [varchar](10) NULL,
	[Status] [char](1) NULL,
	[CFDIStampingProvider] [varchar](13) NULL,
	[IsActive] [bit] NOT NULL CONSTRAINT [DF_TraCFDI_IsActive]  DEFAULT ('1'),
	[Version] [timestamp] NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](50) NULL,
	[CFDIEmisor] [varchar](254) NULL,
	[CFDIReceptor] [varchar](254) NULL,
	[CFDIMoneda] [varchar](3) NULL,
	[CFDIMetodoPago] [varchar](3) NULL,
	[CFDIFormaPago] [varchar](2) NULL,
	[CFDISucursal] [varchar](60) NULL,
	[CFDITipoCambio] [numeric](22, 6) NOT NULL CONSTRAINT [DF_TraCFDI_CFDITipoCambio]  DEFAULT ((1)),
	[CFDIIva] [numeric](22, 6) NOT NULL CONSTRAINT[DF_TraCFDI_CFDIIva] DEFAULT ((0))
 CONSTRAINT [PK_CFDIID] PRIMARY KEY CLUSTERED 
(
	[CFDIID] ASC
),CONSTRAINT [UIDX_TraCFDI] UNIQUE NONCLUSTERED 
(
	[CFDIUUID] ASC,
	[Origin] ASC
)) ON [PRIMARY]

END
GO

--Tabla TraCFDIAdditionaInfo
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'TraCFDIAdditionalInfo' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [TraCFDIAdditionalInfo]'
	CREATE TABLE [TraCFDIAdditionalInfo](
	[CFDIAdditionalInfoID] [int] IDENTITY(1,1) NOT NULL,
	[CFDIID] [int] NOT NULL,
	[Branch] [varchar](20) NOT NULL,
	[Mail] [varchar](200) NULL,
 CONSTRAINT [PK_CFDIAdditionalInfoID] PRIMARY KEY CLUSTERED 
(
	[CFDIAdditionalInfoID] ASC
),CONSTRAINT [UQ_TraCFDIAdditionalInfo] UNIQUE NONCLUSTERED 
(
	[CFDIID] ASC
)) ON [PRIMARY]

END
GO

--Tabla TraCFDICancellation
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'TraCFDICancellation' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [TraCFDICancellation]'
	CREATE TABLE [TraCFDICancellation](
	[CFDICancellationID] [int] IDENTITY(1,1) NOT NULL,
	[CFDIEmitionDate] [datetime] NULL,
	[CFDIRFCEmisor] [varchar](13) NOT NULL,
	[XMLID] [int] NULL,
	[IsActive] [bit] NOT NULL CONSTRAINT [DF_TraCFDICancellation_IsActive]  DEFAULT ((1)),
	[Version] [timestamp] NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_CFDICancellationID] PRIMARY KEY CLUSTERED 
(
	[CFDICancellationID] ASC
)) ON [PRIMARY]

END
GO

--Tabla TraCFDICancellationFolio
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'TraCFDICancellationFolio' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [TraCFDICancellationFolio]'
	CREATE TABLE [TraCFDICancellationFolio](
	[CFDICancellationFolioID] [int] IDENTITY(1,1) NOT NULL,
	[CancellationID] [int] NOT NULL,
	[UUID] [uniqueidentifier] NOT NULL,
	[CancellationStatus] [int] NOT NULL,
	[IsActive] [bit] NOT NULL CONSTRAINT [DF_TraCFDICancellationFolio_IsActive]  DEFAULT ('1'),
	[Version] [timestamp] NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_CFDICancellationFolioID] PRIMARY KEY CLUSTERED 
(
	[CFDICancellationFolioID] ASC
),CONSTRAINT [UIDX_TraCFDICancellationFolio] UNIQUE NONCLUSTERED 
(
	[CancellationID] ASC,
	[UUID] ASC
)) ON [PRIMARY]

END
GO

--Tabla TraCFDIComments
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'TraCFDIComments' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [TraCFDIComments]'
	CREATE TABLE [TraCFDIComments](
	[CFDICommentsID] [int] IDENTITY(1,1) NOT NULL,
	[CFDIID] [int] NOT NULL,
	[AsignedUserID] [int] NOT NULL,
	[IsReviewed] [bit] NULL,
	[Comment] [varchar](500) NULL,
	[IsActive] [bit] NOT NULL CONSTRAINT [DF_TraCFDIComments_IsActive]  DEFAULT ('1'),
	[Version] [timestamp] NOT NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_CFDICommentsID] PRIMARY KEY CLUSTERED 
(
	[CFDICommentsID] ASC
)) ON [PRIMARY]

END
GO

--Tabla TraCFDIDocument
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'TraCFDIDocument' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [TraCFDIDocument]'
	CREATE TABLE [TraCFDIDocument](
	[CFDIDocumentID] [int] IDENTITY(1,1) NOT NULL,
	[CFDIID] [int] NOT NULL,
	[AttachmentID] [int] NULL,
	[IsActive] [bit] NOT NULL CONSTRAINT [DF_TraCFDIDocument_IsActive]  DEFAULT ('1'),
	[Version] [timestamp] NOT NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_CFDIDocumentID] PRIMARY KEY CLUSTERED 
(
	[CFDIDocumentID] ASC
)) ON [PRIMARY]

END
GO

--Tabla TraCFDIReceptionLog
IF not exists (select *
                 from sysobjects ,syscolumns	
                 where sysobjects.name = 'TraCFDIReceptionLog' and
                       sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREATE TABLE TraCFDIReceptionLog'
	
	CREATE TABLE TraCFDIReceptionLog
	(	CFDIReceptionLogID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
		CFDIUUID VARCHAR(50) NOT NULL,
		CFDIRFCEmisor VARCHAR(50) NOT NULL,
		CFDIRFCReceptor VARCHAR(50) NOT NULL,
		IsLastVersion BIT NOT NULL,
		CorrectAmaounts BIT NOT NULL,
		StatusInSAT VARCHAR(255) NOT NULL,
		StructureDetails VARCHAR (500) NOT NULL,
		StampStatus VARCHAR(50) NOT NULL,
		BlackListStatus varchar (100) NOT NULL,
		Version TIMESTAMP NOT NULL,
		DateCreated DATETIME NULL,
		CreatedBy VARCHAR(50) NULL,
		DateUpdated DATETIME NULL,
		UpdatedBy VARCHAR(50) NULL,
	)
END
GO

--Tabla TraCFDIRelations
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'TraCFDIRelations' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [TraCFDIRelations]'
	CREATE TABLE [TraCFDIRelations](
	[CFDIRelatedID] [int] IDENTITY(1,1) NOT NULL,
	[UUIDParent] [uniqueidentifier] NOT NULL,
	[OriginParent] [char](1) NOT NULL,
	[UUIDChild] [uniqueidentifier] NULL,
	[OriginChild] [char](1) NULL,
	[RelationType] [char](2) NULL,
	[IsActive] [bit] NOT NULL CONSTRAINT [DF_TraCFDIRelations_IsActive]  DEFAULT ('1'),
	[CFDITotal] [numeric](22, 6) NULL DEFAULT ((0)),
	[CFDITipoCambio] [numeric](22, 6) NULL CONSTRAINT [DF_Relations_TCDefault]  DEFAULT ((1)),
	[CFDIMoneda] [varchar](3) NULL,
 CONSTRAINT [PK_CFDIRelatedID] PRIMARY KEY CLUSTERED 
(
	[CFDIRelatedID] ASC
),CONSTRAINT [UIDX_CFDIRelations] UNIQUE NONCLUSTERED 
(
	[UUIDParent] ASC,
	[OriginParent] ASC,
	[UUIDChild] ASC,
	[OriginChild] ASC
)) ON [PRIMARY]

END
GO

--Tabla TraPLDScheduledTaskLog
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'TraScheduledTaskLog' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [TraScheduledTaskLog]'
	CREATE TABLE [TraScheduledTaskLog](
	[ScheduledTaskLogID] [int] IDENTITY(1,1) NOT NULL,
	[ScheduledTaskID] [int] NOT NULL,
	[ScheduledTaskTypeID] [int] NOT NULL,
	[EntityID] [int] NULL,
	[ExecutionID] [varchar](255) NULL,
	[RequestID] [varchar](255) NULL,
	[CorrelationID] [varchar](255) NULL,
	[ProcessDate] [datetime] NOT NULL,
	[IsSuccessful] [bit] NOT NULL CONSTRAINT [DF_TraScheduledTaskLog_IsSuccessful]  DEFAULT ((1)),
	[IsManual] [bit] NULL,
	[ResultDescription] [varchar](max) NOT NULL,
	[UserID] [varchar](50) NULL,
	[Version] [timestamp] NOT NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_ScheduledTaskLogID] PRIMARY KEY CLUSTERED 
(
	[ScheduledTaskLogID] ASC
)) ON [PRIMARY]

END
GO

--Tabla TraXML
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'TraXML' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [TraXML]'
	CREATE TABLE [TraXML](
	[XMLID] [int] IDENTITY(1,1) NOT NULL,
	[XMLContent] [varchar](max) NOT NULL,
	[XMLName] [varchar](max) NOT NULL,
 CONSTRAINT [PK_XMLID] PRIMARY KEY CLUSTERED 
(
	[XMLID] ASC
)) ON [PRIMARY]

END
GO



/*------------------------------------------------------------------
---------CREATE TABLE TABLE TraCFDIAdditionalInfoSettings-----------
-------------------------------------------------------------------*/
IF not exists (select * from sysobjects ,syscolumns	
                 where sysobjects.name = 'TraCFDIAdditionalInfoSettings' and
                       sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREATE TABLE TraCFDIAdditionalInfoSettings'
	
	CREATE TABLE TraCFDIAdditionalInfoSettings
	(	CFDIAdditionalInfoID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
		TagSettingsID INT NULL,
		CFDIID INT NOT NULL,
		AdditionalInfoValue VARCHAR(55) NOT NULL,
		CONSTRAINT FK_CFDIID_TraCFDI FOREIGN KEY (CFDIID) REFERENCES TraCFDI(CFDIID),
		CONSTRAINT FK_TagSettingsID_TraCFDI FOREIGN KEY (TagSettingsID) REFERENCES CfgTagSettings(TagSettingsID))
END
GO

IF NOT EXISTS(Select *
				from sysobjects, syscolumns
				where sysobjects.name = 'CatBlackList69BPerson' AND sysobjects.id = syscolumns.id)
BEGIN
	PRINT 'CREATE TABLE CatBlackList69BPerson'

	CREATE TABLE [dbo].[CatBlackList69BPerson](
		[BlackList69BPersonID] [int] IDENTITY(1,1) NOT NULL,
		[PersonName69B] [varchar](400) NOT NULL,
		[RFC] [varchar](15) NULL,
		[TaxpayerSituation] [varchar](200) NULL,
		[SATNumDateGloPresumptionOffice] [varchar](200) NULL,
		[PublicationOfTheAllegedSATPage] [varchar](200) NULL,
		[DOFNumDateGloPresumptionOffice] [varchar](200) NULL,
		[DOFPublicationSuspected] [varchar](100) NULL,
		[PublicationTheDistortedSATPage] [varchar](200) NULL,
		[NumDateGlobOffiTaxpayDistorted] [varchar](200) NULL,
		[DOFPublicationMismatched] [varchar](200) NULL,
		[DefinitiveGlobalTradeDateNum] [varchar](200) NULL,
		[FinalSATPagePublication] [varchar](200) NULL,
		[FinalDOFPublication] [varchar](200) NULL,
		[SATNumDateGlobOfficeFavorRul] [varchar](200) NULL,
		[SATPublicationFavorableRuling] [varchar](200) NULL,
		[DOFNumDateGlobOfficeFavorRul] [varchar](200) NULL,
		[DOFPublicationFavorableRuling] [varchar](200) NULL
	) ON [PRIMARY]
END
GO

IF NOT EXISTS(Select *
				from sysobjects, syscolumns
				where sysobjects.name = 'CatBlackList69BHeader' AND sysobjects.id = syscolumns.id)
BEGIN
	PRINT 'CREATE TABLE CatBlackList69BHeader'

	CREATE TABLE [dbo].[CatBlackList69BHeader](
	[BlackList69BHeaderID] [int] IDENTITY(1,1) NOT NULL,
	[BlackListReleaseDate] [datetime] NOT NULL,
	[IsActive] [bit] NOT NULL DEFAULT ('1'),
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL
) ON [PRIMARY]
END
GO

IF NOT EXISTS(Select *
				from sysobjects, syscolumns
				where sysobjects.name = 'CfgMailTemplates' AND sysobjects.id = syscolumns.id)
BEGIN
	PRINT 'CREATE TABLE CfgMailTemplates'

	CREATE TABLE CfgMailTemplates
	(
	MailTemplateID int IDENTITY(1,1) NOT NULL,
	EntityID int NOT NULL,
	Name varchar(100) NOT NULL,
	Description varchar(200) NULL DEFAULT ('No Description'),
	Subject varchar(200) NULL DEFAULT ('No Subject'),
	Body varchar(max) NULL DEFAULT ('No Body Defined'),
	IsActive bit NOT NULL,
	Version timestamp NOT NULL,
	DateCreated datetime NULL,
	CreatedBy varchar(50) NULL,
	DateUpdated datetime NULL,
	UpdatedBy varchar(50) NULL,
	CONSTRAINT FK_EntityID_CatEntityMailTemp FOREIGN KEY (EntityID) REFERENCES CatEntity(EntityID)
	)
END
GO




------------------------------------------------------------------------------------------------------------
PRINT 'Generando Tablas de ScisaFramework'
------------------------------------------------------------------------------------------------------------

USE scisaframework_cfdi;
--Tabla Scisa_Application
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_Application' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_Application]'
CREATE TABLE [Scisa_Application](
	[ApplicationID] [uniqueidentifier] NOT NULL,
	[ApplicationName] [varchar](256) NULL,
	[ApplicationVersion] [varchar](19) NULL,
	[ApplicationVersionInfo] [varchar](256) NULL,
	[ApplicationData] [varbinary](max) NULL,
	[ApplicationDataPS] [varbinary](max) NULL,
 CONSTRAINT [PK_Scisa_Application] PRIMARY KEY CLUSTERED 
(
	[ApplicationID] ASC
)) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
END
GO

--Tabla Scisa_ApplicationConfigurationSettings
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_ApplicationConfigurationSettings' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_ApplicationConfigurationSettings]'
CREATE TABLE [Scisa_ApplicationConfigurationSettings](
	[ApplicationID] [uniqueidentifier] NOT NULL,
	[Context] [varchar](100) NULL,
	[Property] [varchar](100) NOT NULL,
	[Value] [varchar](max) NULL,
 CONSTRAINT [PK_Scisa_ApplicationConfigurationSettings] PRIMARY KEY CLUSTERED 
(
	[ApplicationID] ASC,
	[Property] ASC
)) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
END
GO

--Tabla Scisa_ApplicationDesktopSettings
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_ApplicationDesktopSettings' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_ApplicationDesktopSettings]'
	CREATE TABLE [Scisa_ApplicationDesktopSettings](
	[ApplicationID] [uniqueidentifier] NOT NULL,
	[UserID] [uniqueidentifier] NOT NULL,
	[WindowID] [uniqueidentifier] NOT NULL,
	[OpenedWindowsQueue] [varchar](max) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[LastUpdated] [datetime] NULL,
 CONSTRAINT [PK_Scisa_ApplicationDesktopSettings] PRIMARY KEY CLUSTERED 
(
	[ApplicationID] ASC,
	[UserID] ASC,
	[WindowID] ASC
)) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

END
GO

--Tabla Scisa_ApplicationSettings
IF NOT EXISTS(Select *
				from sysobjects, syscolumns
				where sysobjects.name = 'Scisa_ApplicationSettings' AND sysobjects.id = syscolumns.id)
BEGIN
	PRINT 'CREANDO TABLA [Scisa_ApplicationSettings]'
	CREATE TABLE [Scisa_ApplicationSettings](
	[ApplicationID] [uniqueidentifier] NOT NULL,
	[Context] [varchar](100) NULL,
	[Property] [varchar](100) NOT NULL,
	[Value] [varchar](max) NULL,
 CONSTRAINT [PK_Scisa_ApplicationSettings] PRIMARY KEY CLUSTERED 
(
	[ApplicationID] ASC,
	[Property] ASC
)
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
END
GO

--Tabla Scisa_ApplicationsLicenses
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_ApplicationsLicenses' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_ApplicationsLicenses]'
	CREATE TABLE [Scisa_ApplicationsLicenses](
	[ApplicationID] [uniqueidentifier] NOT NULL,
	[LicenseIssueDate] [date] NOT NULL,
	[LicenseType] [int] NOT NULL,
	[LicensedTo] [varchar](512) NOT NULL,
	[LicensedToData] [varchar](512) NULL,
	[LicenseKey] [varchar](40) NOT NULL,
 CONSTRAINT [PK_ApplicationsLicenses] UNIQUE NONCLUSTERED 
(
	[ApplicationID] ASC,
	[LicenseIssueDate] ASC,
	[LicenseType] ASC
)) ON [PRIMARY]
END
GO

--Tabla Scisa_ApplicationsMemberships
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_ApplicationsMemberships' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_ApplicationsMemberships]'
	CREATE TABLE [Scisa_ApplicationsMemberships](
	[MembershipID] [uniqueidentifier] NOT NULL,
	[ApplicationID] [uniqueidentifier] NOT NULL,
	[UserID] [uniqueidentifier] NOT NULL,
	[Created] [datetime] NOT NULL,
	[CreatedBy] [varchar](60) NULL,
	[LastLogin] [datetime] NULL CONSTRAINT [DF_Scisa_User_LastLogin]  DEFAULT ('1753-01-01 00:00:00.000'),
	[AccountLockedOut] [bit] NULL CONSTRAINT [DF_Scisa_ApplicationsMemberships_AccountLockedOut]  DEFAULT ((0)),
	[SessionsNumber] [int] NULL CONSTRAINT [DF_Scisa_ApplicationsMemberships_SessionsNumber]  DEFAULT ((1)),
 CONSTRAINT [PK_Scisa_ApplicationsMemberships] PRIMARY KEY CLUSTERED 
(
	[MembershipID] ASC
)) ON [PRIMARY]

END
GO

--Tabla Scisa_Role
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_Role' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_Role]'
	CREATE TABLE [Scisa_Role](
	[RoleID] [uniqueidentifier] NOT NULL,
	[ApplicationID] [uniqueidentifier] NOT NULL,
	[Name] [varchar](150) NOT NULL,
	[Version] [timestamp] NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](60) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](60) NULL,
 CONSTRAINT [PK_Scisa_Role] PRIMARY KEY CLUSTERED 
(
	[RoleID] ASC
)
) ON [PRIMARY]

END
GO

--Tabla  Scisa_RolesPermissions
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_RolesPermissions' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_RolesPermissions]'
	CREATE TABLE [Scisa_RolesPermissions](
	[RoleID] [uniqueidentifier] NOT NULL,
	[PermissionID] [varchar](256) NOT NULL,
	[Created] [datetime] NULL,
	[CreatedBy] [varchar](60) NULL,
 CONSTRAINT [PK_Scisa_RolesPermissions] PRIMARY KEY CLUSTERED 
(
	[RoleID] ASC,
	[PermissionID] ASC
)) ON [PRIMARY]

END
GO

--Tabla Scisa_User
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_User' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_User]'
	CREATE TABLE [Scisa_User](
	[UserID] [uniqueidentifier] NOT NULL,
	[UserName] [varchar](256) NOT NULL,
	[Name] [varchar](200) NOT NULL,
	[PaternalSurname] [varchar](60) NOT NULL,
	[LoginAttempts] [int] NOT NULL,
	[AccountLockedOut] [bit] NOT NULL,
	[AccountType] [smallint] NOT NULL,
	[MaternalSurname] [varchar](60) NULL,
	[Password] [varchar](512) NULL,
	[PasswordChangeRequired] [bit] NULL,
	[LastLogin] [datetime] NULL,
	[AccountLockedOutReason] [smallint] NULL,
	[Email] [varchar](256) NULL,
	[Active] [bit] NOT NULL,
	[Version] [timestamp] NOT NULL,
	[DateCreated] [datetime] NULL,
	[CreatedBy] [varchar](60) NULL,
	[DateUpdated] [datetime] NULL,
	[UpdatedBy] [varchar](60) NULL,
 CONSTRAINT [PK_Scisa_User] PRIMARY KEY CLUSTERED 
(
	[UserID] ASC
)) ON [PRIMARY]

END
GO

--Tabla Scisa_UserPasswordHistory
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_UserPasswordHistory' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_UserPasswordHistory]'
	CREATE TABLE [Scisa_UserPasswordHistory](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[UserID] [uniqueidentifier] NOT NULL,
	[Password] [varchar](512) NULL,
	[DateCreated] [datetime] NOT NULL,
	[CreatedBy] [varchar](50) NOT NULL,
	[DateUpdated] [datetime] NOT NULL,
	[UpdatedBy] [varchar](50) NOT NULL,
	[Version] [timestamp] NOT NULL,
 CONSTRAINT [PK_Scisa_UserPasswordHistory] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)) ON [PRIMARY]

END
GO

--Tabla Scisa_UserSettings
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_UserSettings' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_UserSettings]'
	CREATE TABLE [Scisa_UserSettings](
	[ApplicationID] [uniqueidentifier] NOT NULL,
	[UserID] [uniqueidentifier] NOT NULL,
	[WindowID] [uniqueidentifier] NOT NULL,
	[Context] [varchar](100) NULL,
	[Property] [varchar](100) NOT NULL,
	[Value] [varchar](max) NULL,
 CONSTRAINT [PK_Scisa_UserSettings] PRIMARY KEY CLUSTERED 
(
	[ApplicationID] ASC,
	[UserID] ASC,
	[WindowID] ASC,
	[Property] ASC
)) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

END
GO

--Tabla Scisa_UsersPermissions
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_UsersPermissions' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_UsersPermissions]'
	CREATE TABLE [Scisa_UsersPermissions](
	[MembershipID] [uniqueidentifier] NOT NULL,
	[PermissionID] [varchar](256) NOT NULL,
	[Denied] [bit] NOT NULL DEFAULT ((0)),
	[Created] [datetime] NULL,
	[CreatedBy] [varchar](60) NULL,
 CONSTRAINT [PK_Scisa_UsersPermissions] PRIMARY KEY CLUSTERED 
(
	[MembershipID] ASC,
	[PermissionID] ASC
)) ON [PRIMARY]

END
GO

--Tabla Scisa_UsersRoles
IF  NOT EXISTS (select *
                from sysobjects ,syscolumns	
                where sysobjects.name = 'Scisa_UsersRoles' and
                      sysobjects.id = syscolumns.id ) 
BEGIN
	PRINT 'CREANDO TABLA [Scisa_UsersRoles]'
	CREATE TABLE [Scisa_UsersRoles](
	[UserID] [uniqueidentifier] NOT NULL,
	[RoleID] [uniqueidentifier] NOT NULL,
	[Created] [datetime] NULL,
	[CreatedBy] [varchar](60) NULL,
 CONSTRAINT [PK_Scisa_UsersRoles] PRIMARY KEY CLUSTERED 
(
	[UserID] ASC,
	[RoleID] ASC
)) ON [PRIMARY]

END
GO


