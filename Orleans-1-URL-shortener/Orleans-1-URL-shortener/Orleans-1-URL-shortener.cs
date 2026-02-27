// URL shortener API using ASP.NET Core minimal APIs

// using Orleans.Runtime;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using Orleans.Configuration;
using Orleans.Dashboard;
using System.IO.Hashing;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

var orleansConnectionString = builder.Configuration.GetConnectionString("Orleans")
    ?? throw new InvalidOperationException("Missing required connection string 'Orleans'.");


var siloName = System.Net.Dns.GetHostName(); // unique per container replica
var jaegerEndpoint = builder.Configuration["Jaeger:Endpoint"] ?? "http://jaeger:4317";

// Observability
builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService(
        serviceName: "url-shortener",
        serviceInstanceId: siloName))   // tells Jaeger which replica this is
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddSource("Microsoft.Orleans.Runtime")
        .AddSource("Microsoft.Orleans.Application")
        .AddOtlpExporter(otlp => otlp.Endpoint = new Uri(jaegerEndpoint)));


builder.Host.UseOrleans(siloBuilder =>
{
    siloBuilder
        .Configure<SiloOptions>(opts => opts.SiloName = siloName)
        .UseAdoNetClustering(clusteringSiloOptions =>
        {
            clusteringSiloOptions.Invariant = "Npgsql";
            clusteringSiloOptions.ConnectionString = orleansConnectionString;
        })
        .AddAdoNetGrainStorage("urls", grainStorageOptions =>
        {
            grainStorageOptions.Invariant = "Npgsql";
            grainStorageOptions.ConnectionString = orleansConnectionString;
        })
        .AddActivityPropagation()   // propagates trace context across grain calls
        .AddDashboard();
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
    app.MapOrleansDashboard();


app.MapGet("/shorten",
    static async (IGrainFactory grainFactory, HttpRequest request, string? url) =>
    {
        if (string.IsNullOrWhiteSpace(url))
            return Results.BadRequest("url query parameter is required");

        if (!Uri.IsWellFormedUriString(url, UriKind.Absolute))
            return Results.BadRequest("url query parameter should be a well formed absolute url");

        var shortenedRouteSegment = Crc32.HashToUInt32(Encoding.UTF8.GetBytes(url)).ToString("x");
        var shortenerGrain = grainFactory.GetGrain<IUrlShortenerGrain>(shortenedRouteSegment);
        await shortenerGrain.SetUrl(url);

        var host = $"{request.Scheme}://{request.Host.Value}";
        return Results.Ok(new Uri($"{host}/go/{shortenedRouteSegment}"));
    }
);

app.MapGet("/go/{shortenedRouteSegment:required}",
    static async (IGrainFactory grainFactory, string shortenedRouteSegment) =>
    {
        var shortenerGrain = grainFactory.GetGrain<IUrlShortenerGrain>(shortenedRouteSegment);
        var url = await shortenerGrain.GetUrl();

        return string.IsNullOrEmpty(url)
            ? Results.NotFound("Shortened URL not found")
            : Results.Redirect(url);
    }
);

await app.RunAsync();
