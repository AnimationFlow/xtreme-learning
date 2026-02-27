<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# <q>What's good

```
IPersistentState<UrlDetails> injection via constructor — correct modern Orleans pattern, much better than Grain<TState>.
```

[GenerateSerializer] + [Alias] + [Id] on UrlDetails — proper Orleans serializer setup.

sealed on the grain class — good, prevents accidental inheritance.</q> let's leave jaeger as is for now and summarize what's done and some best practices (like the referenced piece of chat) so that i have it all in one place

Here's everything you built and the best practices behind each decision.

***

## What You Built

A URL shortener service using **Microsoft Orleans** on **.NET 10** with:

- AdoNet clustering + persistence via **PostgreSQL**
- **2 replicas** of the silo running as Docker containers
- **Jaeger** for distributed tracing (OTLP)
- Orleans **Dashboard** in Development
- Clean **multi-stage Dockerfile** + **docker-compose** orchestration

***

## Orleans Grain Best Practices

### Grain implementation

```csharp
public sealed class UrlShortenerGrain(
    [PersistentState(stateName: "url", storageName: "urls")]
    IPersistentState<UrlDetails> state
) : Grain, IUrlShortenerGrain
```

- **`sealed`** — prevents accidental inheritance; grains are not designed to be subclassed

```
- **Constructor injection of `IPersistentState<T>`** — modern Orleans pattern, cleaner than inheriting `Grain<TState>`
```

- **`stateName`** = logical name for the state slot, **`storageName`** = maps to the registered storage provider (`"urls"` → `AddAdoNetGrainStorage("urls", ...)`)


### Serialization

```csharp
[GenerateSerializer, Alias(nameof(UrlDetails))]
public class UrlDetails
{
    [Id(0)] public string FullUrl { get; set; } = string.Empty;
    [Id(1)] public string ShortenedRouteSegment { get; set; } = string.Empty;
}
```

- **`[GenerateSerializer]`** — tells Orleans source generator to emit fast serialization code; required for all grain state/message types
- **`[Alias]`** — stable type name for serialization; survives namespace/class renames without breaking persisted state
- **`[Id(N)]`** — stable field index; never reuse or reorder IDs, only add new ones


### Idempotent `SetUrl`

```csharp
public async Task SetUrl(string fullUrl)
{
    if (state.RecordExists && state.State.FullUrl == fullUrl)
        return; // skip redundant write

    state.State = new UrlDetails { ... };
    await state.WriteStateAsync();
}
```

- Check `state.RecordExists` before writing — avoids unnecessary DB round-trips
- Idempotent: calling `SetUrl` twice with same URL is a no-op


### Null-safe `GetUrl`

```csharp
public Task<string?> GetUrl()
{
    if (!state.RecordExists || string.IsNullOrEmpty(state.State.FullUrl))
        return Task.FromResult<string?>(null);
    return Task.FromResult<string?>(state.State.FullUrl);
}
```

- Return `null` on miss, not `string.Empty` — makes caller intent explicit

***

## Program.cs Best Practices

### Fail fast on missing config

```csharp
var orleansConnectionString = builder.Configuration.GetConnectionString("Orleans")
    ?? throw new InvalidOperationException("Missing required connection string 'Orleans'.");
```

- Crash at startup with a clear message rather than silently passing `null` to Npgsql


### Orleans setup order

```csharp
siloBuilder
    .Configure<SiloOptions>(opts => opts.SiloName = siloName)  // identity first
    .UseAdoNetClustering(...)     // clustering before storage
    .AddAdoNetGrainStorage(...)   // then persistence
    .AddActivityPropagation()     // trace context crosses grain boundaries
    .AddDashboard();
```

- `SiloName` from `Dns.GetHostName()` → unique per container, visible in logs + dashboard
- `AddActivityPropagation()` is **required** for OpenTelemetry traces to connect HTTP spans → grain call spans


### Guard dashboard behind environment

```csharp
if (app.Environment.IsDevelopment())
    app.MapOrleansDashboard();
```

- Never expose Orleans Dashboard publicly


### 404 before redirect

```csharp
var url = await grain.GetUrl();
return string.IsNullOrEmpty(url)
    ? Results.NotFound("Shortened URL not found")
    : Results.Redirect(url);
```

- Always guard redirect — an empty URL would produce a broken `Results.Redirect("")`

***

## Configuration Best Practices

### Connection string via env var (compose → ASP.NET Core)

```yaml
# compose.yaml
environment:
  ConnectionStrings__Orleans: "Host=postgres;Database=orleans;Username=devuser;Password=devpass"
```

```csharp
// Program.cs
builder.Configuration.GetConnectionString("Orleans")
```

- Double underscore `__` maps to nested config sections in ASP.NET Core — `ConnectionStrings__Orleans` → `ConnectionStrings:Orleans`
- Overrides `appsettings.json` at runtime; no code change needed between local and Docker


### No hardcoded env var hacks

Remove patterns like:

```csharp
// ❌ don't do this
var pgHost = Environment.GetEnvironmentVariable("PGHOST");
if (!string.IsNullOrEmpty(pgHost))
    connectionString = new NpgsqlConnectionStringBuilder(connectionString) { Host = pgHost }.ToString();
```

Use the config system properly — it handles overrides via env vars, JSON, secrets etc. in the right priority order.

***

## Docker Best Practices

### Multi-stage Dockerfile

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build   # compile
...
FROM mcr.microsoft.com/dotnet/aspnet:10.0          # runtime only
```

- SDK image (~900MB) never ships to production; runtime image (~220MB) only contains what's needed


### Replicas with port range

```yaml
deploy:
  replicas: 2
ports:
  - "5175-5176:8080"
```

- `deploy.replicas` works in Compose v2 without Swarm
- Port range assigns `5175` → replica 1, `5176` → replica 2 automatically
- No `container_name` when using replicas — fixed name prevents scaling


### Healthcheck before dependent services start

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

- Prevents silos from starting before PostgreSQL is ready to accept connections; avoids startup race conditions


### Orleans SQL scripts via init volume

```yaml
volumes:
  - ./orleans-scripts:/docker-entrypoint-initdb.d
```

- PostgreSQL runs all `.sql` files in that directory on first start, in filename order — hence the `01-`, `02-`, `03-`, `04-` prefix naming

***

## Observability Stack

| Pillar | Tool | What you see |
| :-- | :-- | :-- |
| **Logs** | ASP.NET Core console + `SiloName` | Which replica handled each request |
| **Traces** | OpenTelemetry → Jaeger (`:16686`) | Full span tree: HTTP → grain call → DB write |
| **Cluster health** | Orleans Dashboard (`:5175`) | Silo ring %, grain activations, membership |

### OpenTelemetry sources for Orleans

```csharp
.AddSource("Microsoft.Orleans.Runtime")
.AddSource("Microsoft.Orleans.Application")
```

Both are required — `Runtime` covers clustering/lifecycle, `Application` covers grain calls and state operations.

***

## Known Gotchas Fixed Along the Way

| Issue | Fix |
| :-- | :-- |
| `CleanupDefunctSiloEntriesKey` missing from official SQL | Append INSERT to `02-PostgreSQL-Clustering.sql` in `setup.sh` |
| `orleansgrainstate` table not found | It's `orleansstorage` with AdoNet provider — different table name |
| CRC32 collision risk | Fine for dev/learning; use longer hash (XxHash64 + base62) for production |
| `libgssapi_krb5.so.2` warning | Npgsql trying GSSAPI auth you don't use — suppress via log level or install lib |
| `ASPNETCORE_URLS` + `HTTP_PORTS` warning | Remove `ASPNETCORE_URLS`, let `HTTP_PORTS=8080` (image default) handle it |

