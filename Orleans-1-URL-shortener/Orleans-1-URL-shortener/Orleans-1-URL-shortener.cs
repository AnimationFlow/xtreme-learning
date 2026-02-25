// URL shortener API using ASP.NET Core minimal APIs

using Orleans.Runtime;

var builder = WebApplication.CreateBuilder(args);

var app = builder.Build();

app.MapGet("/", () => "Hello World!");

app.Run();
