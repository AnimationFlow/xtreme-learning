// Connect4.Api/Program.cs
using Connect4.Contracts.Grains;
using Orleans.Configuration;
using Orleans.Dashboard;

var builder = WebApplication.CreateBuilder(args);

var orleansConnectionString = builder.Configuration.GetConnectionString("Orleans")
    ?? throw new InvalidOperationException("Missing required connection string 'Orleans'.");

var siloName = System.Net.Dns.GetHostName();

builder.Host.UseOrleans(siloBuilder =>
{
    siloBuilder
        .Configure<SiloOptions>(opts => opts.SiloName = siloName)
        .Configure<ClusterOptions>(opts =>
        {
            opts.ClusterId = "dev";
            opts.ServiceId = "Connect4Service";
        })
        .UseAdoNetClustering(opt =>
        {
            opt.Invariant = "Npgsql";
            opt.ConnectionString = orleansConnectionString;
        })
        .AddAdoNetGrainStorage("connect4", opt =>
        {
            opt.Invariant = "Npgsql";
            opt.ConnectionString = orleansConnectionString;
        })
        .Configure<GrainCollectionOptions>(opts =>
            opts.CollectionAge = TimeSpan.FromMinutes(10))
        .AddDashboard();
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
    app.MapOrleansDashboard();

var api = app.MapGroup("/connect4");


// Routes

// Players
api.MapPost("/player/register", async (IGrainFactory grains, RegisterPlayerRequest req) =>
{
    var name = req.Name ?? $"Player-{Random.Shared.Next(1000, 9999)}";

    var player = grains.GetGrain<IPlayerGrain>(name);

    return Results.Ok(player);
});


await app.RunAsync();


// Request records
record RegisterPlayerRequest(string Name);
