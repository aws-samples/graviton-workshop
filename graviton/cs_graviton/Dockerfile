# Learn about building .NET container images:
# https://github.com/dotnet/dotnet-docker/blob/main/samples/README.md
FROM mcr.microsoft.com/dotnet/sdk:10.0-noble AS build
WORKDIR /source

# Copy project file and restore as distinct layers
COPY aspnetapp/*.csproj .
RUN dotnet restore 

# Copy source code and publish app
COPY --link aspnetapp/. .
RUN dotnet publish --no-restore -o /app


# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:10.0-noble
WORKDIR /app
COPY --link --from=build /app .
USER $APP_UID
ENTRYPOINT ["./aspnetapp"]