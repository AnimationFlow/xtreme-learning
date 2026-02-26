// URL shortener API using ASP.NET Core minimal APIs

// using Orleans.Runtime;
using Orleans.Dashboard;
using System.IO.Hashing;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

var orleansConnectionString = builder.Configuration.GetConnectionString("Orleans");

var envVarPgHost = Environment.GetEnvironmentVariable("PGHOST");
if (!string.IsNullOrEmpty(envVarPgHost))
{
    // Override PGHOST if set, to allow easier configuration when running in Docker
    var orleansConnectionStringBuilder = new Npgsql.NpgsqlConnectionStringBuilder(orleansConnectionString)
    {
        Host = envVarPgHost
    };

    orleansConnectionString = orleansConnectionStringBuilder.ToString();
}

builder.Host.UseOrleans(siloBuilder =>
{
    siloBuilder
        .AddAdoNetGrainStorage("urls", grainStorageOptions =>
        {
            grainStorageOptions.Invariant = "Npgsql";
            grainStorageOptions.ConnectionString = orleansConnectionString;
        })
        .UseAdoNetClustering(clusteringSiloOptions =>
        {
            clusteringSiloOptions.Invariant = "Npgsql";
            clusteringSiloOptions.ConnectionString = orleansConnectionString;
        })
        .AddDashboard();
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
    app.MapOrleansDashboard();

app.MapGet("/shorten",
    static async (IGrainFactory grainFactory, HttpRequest request, string? url) =>
    {
        var host = $"{request.Scheme}://{request.Host.Value}";

        if (string.IsNullOrWhiteSpace(url))
        {
            return Results.BadRequest("url query parameter is required");
        }

        if (!Uri.IsWellFormedUriString(url, UriKind.Absolute))
        {
            return Results.BadRequest("url query parameter should be a well formed absolute url");
        }

        var shortenedRouteSegment = Crc32.HashToUInt32(Encoding.UTF8.GetBytes(url)).ToString("x");

        var shortenerGrain = grainFactory.GetGrain<IUrlShortenerGrain>(shortenedRouteSegment);

        await shortenerGrain.SetUrl(url);

        var resultBuilder = new UriBuilder(host)
        {
            Path = $"/go/{shortenedRouteSegment}"
        };

        return Results.Ok(resultBuilder.Uri);
    }
);

app.MapGet("/go/{shortenedRouteSegment:required}",
    static async (IGrainFactory grainFactory, string shortenedRouteSegment) =>
    {
        var shortenerGrain = grainFactory.GetGrain<IUrlShortenerGrain>(shortenedRouteSegment);

        var url = await shortenerGrain.GetUrl();

        if(string.IsNullOrEmpty(url))
        {
            return Results.NotFound("Shortened URL not found");
        }

        return Results.Redirect(url);
    }
);

await app.RunAsync();
