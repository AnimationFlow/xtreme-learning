# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY Orleans-1-URL-shortener/Orleans-1-URL-shortener/*.csproj ./
RUN dotnet restore

COPY Orleans-1-URL-shortener/Orleans-1-URL-shortener/ ./
RUN dotnet publish -c Release -o /app/publish

# Stage 2: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app/publish .

EXPOSE 8080
ENTRYPOINT ["dotnet", "Orleans-1-URL-shortener.dll"]
