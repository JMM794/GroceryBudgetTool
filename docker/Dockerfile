# Use Microsoft's official SQL Server image
FROM mcr.microsoft.com/mssql/server:2022-latest

# Set required environment variables
ENV ACCEPT_EULA=Y
# Password is passed at runtime for securitydocker exec -it grocery-db /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P "Project_002FINC"

# Set working directory inside the container
WORKDIR /usr/src/app

# Copy your SQL scripts into the container
COPY init/ /usr/src/app/init/

# Run SQL Server and execute your scripts
CMD ["/opt/mssql/bin/sqlservr"]