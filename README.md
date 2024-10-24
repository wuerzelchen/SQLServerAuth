## Example for using Azure Managed Identity with Azure SQL Database

### Prerequisites
- Have an Azure SQL Database running.
- Have an Azure App Service or Azure Container App running with a system assigned managed identity with the right permissions in the Azure SQL Database.

### Assign the right permissions to the system assigned managed identity in the Azure SQL Database

In this case, we are going to assign the rights to an Entra ID group. In this group is our system assigned managed identity.

```sql
CREATE USER [myAzureSQLDBAccessGroup] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [myAzureSQLDBAccessGroup];
ALTER ROLE db_datawriter ADD MEMBER [myAzureSQLDBAccessGroup];
ALTER ROLE db_ddladmin ADD MEMBER [myAzureSQLDBAccessGroup];
```

### Check if your user has the right permissions in the DB

```sql
SELECT 
    pr.name AS PrincipalName,
    dp.name AS RoleName
FROM 
    sys.database_role_members AS drm
JOIN 
    sys.database_principals AS pr ON drm.member_principal_id = pr.principal_id
JOIN 
    sys.database_principals AS dp ON drm.role_principal_id = dp.principal_id
WHERE 
    pr.name = 'myAzureSQLDBAccessGroup';  -- Replace 'your_username' with the actual username, the name of the Entra ID group or the name of the system assigned managed identity (the name of the app service/container app)
```

### Set the environment variables

Before running the application, you need to set the environment variables.

```bash
export SQL_SERVER_NAME="your_sql_server_name"
export SQL_DATABASE_NAME="your_sql_database_name"
```

### Start the application.
  
```bash
python app.py
```

## Deploy the application to Azure App Service or Azure Container App
### Build and check the Docker image

```bash
docker build -t my-python-app .
docker run -p 5000:5000 -e SQL_SERVER_NAME="your_sql_server_name" -e SQL_DATABASE_NAME="your_sql_database_name" my-python-app
```

if everything is working as expected, you can push the image to the Azure Container Registry.

### Push the Docker image to the Azure Container Registry

```bash
az acr login --name your_acr_name
docker tag my-python-app your_acr_name.azurecr.io/my-python-app
docker push your_acr_name.azurecr.io/my-python-app
```

Now you can deploy the image to the Azure Container App or Azure App Service.