---
tags: [rabbitmq, dotnet, setup]
created: 2026-02-17
---
# RabbitMQ.Client Setup in .NET

Using the **official RabbitMQ.Client** NuGet package – no abstraction layer.

## Installation
```bash
dotnet add package RabbitMQ.Client
```

## Connection Setup (.NET 8)
```csharp
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;
using System.Text.Json;

// Create connection factory
var factory = new ConnectionFactory
{
    HostName = "localhost",
    Port = 5672,
    UserName = "guest",
    Password = "guest"
};

// Create connection and channel
await using var connection = await factory.CreateConnectionAsync();
await using var channel = await connection.CreateChannelAsync();
```

## Key Concepts
- **Connection**: TCP connection to RabbitMQ broker (expensive, reuse it)
- **Channel**: Lightweight virtual connection within a Connection (one per thread)
- Keep connections long-lived, create channels as needed
- Modern RabbitMQ.Client uses async API

## In ASP.NET Core (DI Registration)
```csharp
// Register as singleton in Program.cs
builder.Services.AddSingleton<IConnection>(sp =>
{
    var factory = new ConnectionFactory
    {
        HostName = builder.Configuration["RabbitMQ:Host"],
        UserName = builder.Configuration["RabbitMQ:User"],
        Password = builder.Configuration["RabbitMQ:Pass"]
    };
    return factory.CreateConnectionAsync().GetAwaiter().GetResult();
});
```

## Links
- [[Publishing Messages]]
- [[Consuming Messages]]
- [[ConnectionFactory and Channels]]