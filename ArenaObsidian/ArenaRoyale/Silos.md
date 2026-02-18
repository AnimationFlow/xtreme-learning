---

tags: [orleans, concept, silo]

created: 2026-02-17

---

# Silos

  

A **Silo** is the runtime host for Orleans grains.

  

## What it does

- Hosts and manages grain activations

- Handles messaging between grains

- Participates in cluster membership

- Manages grain lifecycle (activation, deactivation, garbage collection)

  

## Configuration (minimal .NET 8)

```csharp

var builder = WebApplication.CreateBuilder(args);

  

builder.Host.UseOrleans(siloBuilder =>

{

siloBuilder.UseLocalhostClustering(); // dev only

siloBuilder.AddMemoryGrainStorage("Default"); // dev only

});

  

var app = builder.Build();

app.Run();

```

  

## Production Setup

- Use ADO.NET clustering (PostgreSQL) instead of localhost

- Use persistent grain storage

- Multiple silos form a [[Clusters|Cluster]]

  

## Links

- [[Clusters]]

- [[Orleans + PostgreSQL Persistence]]

- [[What is Orleans]]