CREATE OR ALTER PROCEDURE dbo.train
    @MaterialName VARCHAR(100)
AS
BEGIN
    SELECT 
        [quote_id], 
        [client_id],
        [material]
    FROM [dbo].[quotes]
    WHERE [material] = @MaterialName;
END
GO
