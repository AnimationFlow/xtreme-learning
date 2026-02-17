
import os, shutil

base = "PlayNirvana_Learning_Vault"

# Remove old MassTransit-focused files
old_files = [
    f"{base}/04 - RabbitMQ + MassTransit/RabbitMQ + MassTransit MOC.md",
    f"{base}/04 - RabbitMQ + MassTransit/What is MassTransit.md",
    f"{base}/04 - RabbitMQ + MassTransit/Orleans + RabbitMQ – When to Use What.md",
]
for f in old_files:
    if os.path.exists(f):
        os.remove(f)

# Rename folder
if os.path.exists(f"{base}/04 - RabbitMQ + MassTransit"):
    os.rename(f"{base}/04 - RabbitMQ + MassTransit", f"{base}/04 - RabbitMQ")

files = {}

# ─── UPDATED RabbitMQ MOC ───
files[f"{base}/04 - RabbitMQ/RabbitMQ MOC.md"] = """---
tags: [moc, rabbitmq]
created: 2026-02-17
---
# RabbitMQ MOC (Map of Content)

> Using the **raw RabbitMQ.Client** library – no MassTransit abstraction.

## Core Concepts
- [[What is RabbitMQ]]
- [[AMQP Protocol Basics]]
- [[Exchanges]]
- [[Queues]]
- [[Bindings and Routing Keys]]
- [[Message Acknowledgment]]

## Exchange Types
- [[Direct Exchange]]
- [[Fanout Exchange]]
- [[Topic Exchange]]
- [[Headers Exchange]]

## .NET Integration
- [[RabbitMQ.Client Setup]]
- [[ConnectionFactory and Channels]]
- [[Publishing Messages]]
- [[Consuming Messages]]
- [[AsyncEventingBasicConsumer]]
- [[Message Serialization (JSON)]]
- [[Durable Queues and Persistent Messages]]

## Patterns
- [[Pub-Sub with RabbitMQ]]
- [[Work Queues (Competing Consumers)]]
- [[Request-Reply Pattern]]
- [[Dead Letter Exchanges]]
- [[Retry with Delayed Requeue]]

## Integration with Orleans
- [[Orleans + RabbitMQ – When to Use What]]
- [[Publishing from Grains]]

## Docker Setup
```bash
docker run -d --name rabbitmq \\
  -p 5672:5672 -p 15672:15672 \\
  -e RABBITMQ_DEFAULT_USER=guest \\
  -e RABBITMQ_DEFAULT_PASS=guest \\
  rabbitmq:3-management
```
Management UI: http://localhost:15672
"""

files[f"{base}/04 - RabbitMQ/What is RabbitMQ.md"] = """---
tags: [rabbitmq, concept, fundamental]
created: 2026-02-17
---
# What is RabbitMQ?

**RabbitMQ** is an open-source message broker that implements the AMQP (Advanced Message Queuing Protocol). It acts as a middleman between applications that produce messages and those that consume them.

## Core Components

| Component | Role |
|---|---|
| **Producer** | Application that sends messages |
| **Exchange** | Receives messages from producers and routes them to queues |
| **Queue** | Buffer that stores messages until consumed |
| **Binding** | Rule connecting an exchange to a queue |
| **Consumer** | Application that receives and processes messages |
| **Routing Key** | Label attached to a message, used by exchanges to route |

## Message Flow
```
Producer → Exchange → Binding(routing key) → Queue → Consumer
```

## Why Use It?
- **Decoupling**: Producers and consumers don't need to know about each other
- **Buffering**: Messages wait in queue if consumer is slow/down
- **Load balancing**: Multiple consumers share work from one queue
- **Guaranteed delivery**: Messages persist until acknowledged

## Links
- [[Exchanges]]
- [[Queues]]
- [[Bindings and Routing Keys]]
- [Official RabbitMQ Tutorials](https://www.rabbitmq.com/tutorials)
"""

files[f"{base}/04 - RabbitMQ/Exchanges.md"] = """---
tags: [rabbitmq, concept, exchange]
created: 2026-02-17
---
# Exchanges

An **Exchange** receives messages from producers and routes them to queues based on exchange type and bindings.

## Exchange Types

| Type | Routing Logic | Use Case |
|---|---|---|
| **Direct** | Exact match on routing key | Point-to-point, specific routing |
| **Fanout** | Broadcasts to ALL bound queues | Notifications, broadcast events |
| **Topic** | Pattern match on routing key (`*`, `#`) | Flexible topic-based routing |
| **Headers** | Match on message headers | Complex routing rules |

## Direct Exchange
Routes to queues where binding key == routing key exactly.
```
Producer publishes with key "match.completed"
→ Only queues bound with key "match.completed" receive it
```

## Fanout Exchange
Ignores routing key, sends to ALL bound queues.
```
Producer publishes "MatchCompleted" event
→ LeaderboardQueue receives it
→ NotificationQueue receives it
→ AnalyticsQueue receives it
```

## Topic Exchange
Pattern matching with wildcards:
- `*` matches exactly one word
- `#` matches zero or more words
```
Binding: "match.*.completed" → matches "match.arena1.completed"
Binding: "match.#" → matches "match.arena1.round3.completed"
```

## Code Example
```csharp
// Declare a fanout exchange
await channel.ExchangeDeclareAsync(
    exchange: "game-events",
    type: ExchangeType.Fanout,
    durable: true
);

// Declare a direct exchange
await channel.ExchangeDeclareAsync(
    exchange: "game-commands",
    type: ExchangeType.Direct,
    durable: true
);
```

## Links
- [[Bindings and Routing Keys]]
- [[Pub-Sub with RabbitMQ]]
- [[Direct Exchange]]
"""

files[f"{base}/04 - RabbitMQ/RabbitMQ.Client Setup.md"] = """---
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
"""

files[f"{base}/04 - RabbitMQ/Publishing Messages.md"] = """---
tags: [rabbitmq, dotnet, producer]
created: 2026-02-17
---
# Publishing Messages

How to send messages to RabbitMQ using the raw .NET client.

## Simple Publish
```csharp
// Declare queue (idempotent – safe to call multiple times)
await channel.QueueDeclareAsync(
    queue: "match-completed",
    durable: true,       // survives broker restart
    exclusive: false,
    autoDelete: false
);

// Create message
var matchResult = new MatchCompletedEvent
{
    MatchId = Guid.NewGuid(),
    WinnerId = playerId,
    Score = 150,
    CompletedAt = DateTime.UtcNow
};

var body = Encoding.UTF8.GetBytes(
    JsonSerializer.Serialize(matchResult)
);

// Set message properties
var props = new BasicProperties
{
    ContentType = "application/json",
    DeliveryMode = DeliveryModes.Persistent,  // survives restart
    MessageId = Guid.NewGuid().ToString(),
    Timestamp = new AmqpTimestamp(DateTimeOffset.UtcNow.ToUnixTimeSeconds())
};

// Publish
await channel.BasicPublishAsync(
    exchange: "",                    // default exchange
    routingKey: "match-completed",   // queue name as routing key
    mandatory: false,
    basicProperties: props,
    body: body
);
```

## Publish to Exchange (Fanout)
```csharp
// Declare exchange
await channel.ExchangeDeclareAsync("game-events", ExchangeType.Fanout, durable: true);

// Publish – routing key ignored for fanout
await channel.BasicPublishAsync(
    exchange: "game-events",
    routingKey: "",
    basicProperties: props,
    body: body
);
```

## Key Points
- Always set `DeliveryMode = Persistent` for important messages
- Use JSON serialization for interoperability
- The default exchange ("") routes by queue name
- Named exchanges use bindings to route

## Links
- [[Consuming Messages]]
- [[Exchanges]]
- [[Durable Queues and Persistent Messages]]
"""

files[f"{base}/04 - RabbitMQ/Consuming Messages.md"] = """---
tags: [rabbitmq, dotnet, consumer]
created: 2026-02-17
---
# Consuming Messages

How to receive and process messages from RabbitMQ using the raw .NET client.

## Basic Consumer
```csharp
// Declare the same queue (idempotent)
await channel.QueueDeclareAsync(
    queue: "match-completed",
    durable: true,
    exclusive: false,
    autoDelete: false
);

// Prefetch: only deliver 1 message at a time per consumer
await channel.BasicQosAsync(prefetchSize: 0, prefetchCount: 1, global: false);

// Create async consumer
var consumer = new AsyncEventingBasicConsumer(channel);

consumer.ReceivedAsync += async (sender, ea) =>
{
    try
    {
        var body = ea.Body.ToArray();
        var message = Encoding.UTF8.GetString(body);
        var matchEvent = JsonSerializer.Deserialize<MatchCompletedEvent>(message);

        Console.WriteLine($"Match {matchEvent.MatchId} won by {matchEvent.WinnerId}");

        // Process the message (update leaderboard, etc.)
        await ProcessMatchCompleted(matchEvent);

        // Acknowledge – message removed from queue
        await channel.BasicAckAsync(ea.DeliveryTag, multiple: false);
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error processing message: {ex.Message}");

        // Reject and requeue (or send to dead letter)
        await channel.BasicNackAsync(ea.DeliveryTag, multiple: false, requeue: false);
    }
};

// Start consuming
await channel.BasicConsumeAsync(
    queue: "match-completed",
    autoAck: false,          // MANUAL ack – important!
    consumer: consumer
);
```

## As a Background Service (ASP.NET Core)
```csharp
public class MatchCompletedConsumer : BackgroundService
{
    private readonly IConnection _connection;
    private IChannel? _channel;

    public MatchCompletedConsumer(IConnection connection)
    {
        _connection = connection;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _channel = await _connection.CreateChannelAsync();

        await _channel.QueueDeclareAsync("match-completed", durable: true,
            exclusive: false, autoDelete: false);

        await _channel.BasicQosAsync(0, 1, false);

        var consumer = new AsyncEventingBasicConsumer(_channel);
        consumer.ReceivedAsync += HandleMessage;

        await _channel.BasicConsumeAsync("match-completed",
            autoAck: false, consumer: consumer);

        // Keep running until cancelled
        await Task.Delay(Timeout.Infinite, stoppingToken);
    }

    private async Task HandleMessage(object sender, BasicDeliverEventArgs ea)
    {
        // ... deserialize and process
        await _channel!.BasicAckAsync(ea.DeliveryTag, false);
    }
}
```

## Key Points
- **Always use manual ack** (`autoAck: false`) in production
- `BasicAck` = message processed successfully, remove from queue
- `BasicNack` with `requeue: false` = send to dead letter exchange
- `BasicNack` with `requeue: true` = put back in queue (careful: infinite loop risk)
- Use `BasicQos` to control prefetch count

## Links
- [[Message Acknowledgment]]
- [[Dead Letter Exchanges]]
- [[AsyncEventingBasicConsumer]]
"""

files[f"{base}/04 - RabbitMQ/Orleans + RabbitMQ – When to Use What.md"] = """---
tags: [orleans, rabbitmq, architecture, decision]
created: 2026-02-17
---
# Orleans vs RabbitMQ – When to Use What

This is a critical architectural decision in the PlayNirvana stack.

## Use Orleans Grain Calls When:
- **Synchronous request-response** within the game logic
- Player does action → immediate response needed
- Grain-to-grain coordination (player joins arena)
- Low-latency, in-process communication
- State changes that need immediate consistency

## Use RabbitMQ When:
- **Fire-and-forget** events (match completed, score updated)
- Cross-service communication (game service → analytics service)
- **Guaranteed delivery** is more important than speed
- Decoupling: publisher doesn't need to know about consumers
- Background processing (leaderboard recalculation, notifications)
- Work queue pattern: distribute load across multiple consumers

## In Our Game Project
```
Player attacks → ArenaGrain (Orleans grain call, synchronous)
Match ends → Publish MatchCompleted to RabbitMQ (fanout exchange, async)
              → LeaderboardConsumer updates read model
              → NotificationConsumer sends push notification
              → AnalyticsConsumer logs to data warehouse
```

## Publishing from an Orleans Grain
```csharp
public class MatchGrain : Grain, IMatchGrain
{
    private readonly IChannel _channel;

    public MatchGrain(IChannel channel)
    {
        _channel = channel;
    }

    public async Task CompleteMatch(Guid winnerId)
    {
        // Update grain state...

        // Publish event to RabbitMQ
        var evt = new MatchCompletedEvent
        {
            MatchId = this.GetPrimaryKey(),
            WinnerId = winnerId,
            CompletedAt = DateTime.UtcNow
        };

        var body = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(evt));
        var props = new BasicProperties
        {
            ContentType = "application/json",
            DeliveryMode = DeliveryModes.Persistent
        };

        await _channel.BasicPublishAsync(
            exchange: "game-events",
            routingKey: "match.completed",
            basicProperties: props,
            body: body
        );
    }
}
```

## Decision Matrix
| Scenario | Orleans | RabbitMQ |
|---|:---:|:---:|
| Player action in game | ✅ | |
| Update leaderboard after match | | ✅ |
| Real-time game state sync | ✅ | |
| Send email notification | | ✅ |
| Cross-service integration | | ✅ |
| Grain-to-grain within cluster | ✅ | |
| Guaranteed event processing | | ✅ |
| Load distribution (work queues) | | ✅ |

## Links
- [[Orleans Streams]] – Orleans' built-in streaming (alternative for some cases)
- [[Publishing Messages]]
- [[Consuming Messages]]
"""

files[f"{base}/04 - RabbitMQ/Pub-Sub with RabbitMQ.md"] = """---
tags: [rabbitmq, pattern, pubsub]
created: 2026-02-17
---
# Pub/Sub with RabbitMQ (Raw Client)

The Publish/Subscribe pattern using fanout exchanges – one message delivered to ALL consumers.

## Architecture
```
Producer → Fanout Exchange → Queue A → Consumer A (Leaderboard)
                           → Queue B → Consumer B (Notifications)
                           → Queue C → Consumer C (Analytics)
```

## Setup (Publisher Side)
```csharp
// Declare fanout exchange
await channel.ExchangeDeclareAsync(
    exchange: "game-events",
    type: ExchangeType.Fanout,
    durable: true
);

// Publish event (routing key ignored for fanout)
var body = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(gameEvent));
await channel.BasicPublishAsync("game-events", "", body: body);
```

## Setup (Each Subscriber)
```csharp
// Declare the same exchange
await channel.ExchangeDeclareAsync("game-events", ExchangeType.Fanout, durable: true);

// Declare OWN queue
await channel.QueueDeclareAsync("leaderboard-updates", durable: true,
    exclusive: false, autoDelete: false);

// Bind queue to exchange
await channel.QueueBindAsync("leaderboard-updates", "game-events", "");

// Consume from own queue
var consumer = new AsyncEventingBasicConsumer(channel);
consumer.ReceivedAsync += async (sender, ea) =>
{
    // Process message...
    await channel.BasicAckAsync(ea.DeliveryTag, false);
};
await channel.BasicConsumeAsync("leaderboard-updates", autoAck: false, consumer: consumer);
```

## Key Points
- Each subscriber gets **its own queue** bound to the exchange
- Fanout exchange **copies** the message to every bound queue
- Adding a new subscriber = declare new queue + bind to exchange
- Producer doesn't know or care how many subscribers exist

## Links
- [[Exchanges]]
- [[Work Queues (Competing Consumers)]]
- [[Orleans + RabbitMQ – When to Use What]]
"""

# ─── UPDATE Dashboard and Game Project files ───

files[f"{base}/00 - Dashboard/🗺️ Learning Map.md"] = """---
tags: [moc, dashboard]
created: 2026-02-17
---
# 🗺️ PlayNirvana Onboarding – Learning Map

> **Goal:** In 7 days, reach working proficiency in C# + Orleans + PostgreSQL + RabbitMQ so I can contribute to real projects at PlayNirvana / Xtreme Software Solutions.

## 🔗 Core Concept Maps
- [[Orleans MOC]]
- [[RabbitMQ MOC]]
- [[PostgreSQL + EF Core MOC]]
- [[Architecture Patterns MOC]]
- [[Game Project MOC]]

## 📅 Weekly Plan
- [[Day 1 – Environment + C# Refresher]]
- [[Day 2 – Orleans Deep Dive]]
- [[Day 3 – Orleans Persistence + PostgreSQL]]
- [[Day 4 – RabbitMQ Deep Dive]]
- [[Day 5 – Game Project Scaffold]]
- [[Day 6 – Game Project Integration]]
- [[Day 7 – Polish + Review + Gaps]]

## 🎓 Courses & Resources
- [[Recommended Courses]]
- [[Key YouTube Channels]]
- [[Official Docs Links]]

## 🧠 Key Questions to Answer
- [ ] How do grains map to game entities (players, sessions, matches)?
- [ ] How does Orleans persist state to PostgreSQL?
- [ ] When do we use RabbitMQ vs Orleans Streams?
- [ ] What does the CQRS + Event-Driven flow look like in our stack?
- [ ] How do exchange types (direct, fanout, topic) map to our use cases?
- [ ] How do we manage connections/channels in ASP.NET Core DI?
"""

files[f"{base}/00 - Dashboard/Weekly Plan.md"] = """---
tags: [plan, weekly]
created: 2026-02-17
---
# 📅 7-Day Learning Sprint

## Day 1 (Tue) – Environment Setup + C# Refresher
- [ ] Install/verify: Visual Studio 2022, .NET 8 SDK, Docker Desktop
- [ ] Docker: PostgreSQL 17 + RabbitMQ 3 (with management plugin)
- [ ] Create blank solution `ArenaRoyale` with folder structure
- [ ] Refresh: async/await, generics, interfaces, DI in .NET 8
- [ ] Read: Microsoft Orleans docs overview (30 min)

## Day 2 (Wed) – Orleans Deep Dive
- [ ] Complete Orleans "Hello World" sample
- [ ] Study: Grains, Silos, Clusters, Grain Identity, Grain Lifecycle
- [ ] Build: PlayerGrain, GameSessionGrain with in-memory state
- [ ] Study: Grain persistence providers
- [ ] Watch: "Building a Game with .NET and Orleans" (On .NET Live)

## Day 3 (Thu) – Orleans Persistence + PostgreSQL
- [ ] Set up PostgreSQL in Docker with volume
- [ ] Install Npgsql.EntityFrameworkCore.PostgreSQL
- [ ] Create DbContext, models, migrations
- [ ] Configure Orleans ADO.NET persistence with PostgreSQL
- [ ] Build: LeaderboardGrain with persisted state

## Day 4 (Fri) – RabbitMQ with Raw .NET Client
- [ ] Explore RabbitMQ Management UI (http://localhost:15672)
- [ ] Study: AMQP model – Exchanges, Queues, Bindings, Routing Keys
- [ ] Complete RabbitMQ official .NET tutorials (Hello World, Work Queues, Pub/Sub)
- [ ] Install RabbitMQ.Client NuGet package
- [ ] Build: Publisher (MatchCompleted event) with fanout exchange
- [ ] Build: Consumer as BackgroundService with manual ack
- [ ] Study: Direct vs Fanout vs Topic exchanges
- [ ] Study: Dead letter exchanges, message persistence

## Day 5 (Sat) – Game Project Scaffold
- [ ] Design game entities: Player, Arena, Match, Weapon, Score
- [ ] Implement grain interfaces for all entities
- [ ] Create REST API endpoints (ASP.NET Core Minimal API)
- [ ] Wire up EF Core + PostgreSQL for read models
- [ ] Orleans for write/command side, EF Core for queries

## Day 6 (Sun) – Full Integration
- [ ] Connect Orleans grains → RabbitMQ publisher (raw client)
- [ ] MatchGrain publishes MatchCompleted → fanout exchange → multiple consumers
- [ ] LeaderboardConsumer (BackgroundService) updates PostgreSQL read model
- [ ] End-to-end: API → Orleans → PostgreSQL → RabbitMQ → Consumer
- [ ] Write integration tests

## Day 7 (Mon) – Polish + Review + Gaps
- [ ] Review all Obsidian notes, fill gaps
- [ ] Refactor code for clean architecture patterns
- [ ] Prepare questions for team
- [ ] Review: CQRS, Event Sourcing, DDD concepts
- [ ] Practice explaining the architecture
"""

# ─── UPDATE Game Project MOC ───
files[f"{base}/06 - Game Project/Game Project MOC.md"] = """---
tags: [moc, project, game]
created: 2026-02-17
---
# 🎮 Game Project: Arena Royale

A learning project combining all stack components into a mini battle-arena game.

## Concept
Players join arenas, fight in matches, earn scores. Leaderboards update in real-time.

## Architecture
```
[REST API] → [Orleans Silos]
                 ├── PlayerGrain (state: name, score, inventory)
                 ├── ArenaGrain (state: active players, match status)
                 ├── MatchGrain (state: participants, rounds, winner)
                 └── LeaderboardGrain (state: top players)
                        ↓ publishes events (raw RabbitMQ.Client)
              [RabbitMQ – Fanout Exchange "game-events"]
                        ↓
              [BackgroundService Consumers]
                 ├── LeaderboardConsumer → updates PostgreSQL
                 ├── NotificationConsumer → logs/sends alerts
                 └── AnalyticsConsumer → tracks metrics
                        ↓
              [PostgreSQL Read Models via EF Core]
```

## Solution Structure
```
ArenaRoyale.sln
├── ArenaRoyale.Api              (ASP.NET Core Minimal API + Orleans co-host)
├── ArenaRoyale.GrainInterfaces  (IGrain definitions)
├── ArenaRoyale.Grains           (Grain implementations)
├── ArenaRoyale.Contracts        (Shared DTOs, event classes)
├── ArenaRoyale.Infrastructure   (EF Core, RabbitMQ connection management)
├── ArenaRoyale.Consumers        (BackgroundService consumers)
└── ArenaRoyale.Tests            (xUnit integration tests)
```

## Key NuGet Packages
```
Microsoft.Orleans.Server
Microsoft.Orleans.Client
Microsoft.Orleans.Persistence.AdoNet
Microsoft.Orleans.Clustering.AdoNet
Npgsql.EntityFrameworkCore.PostgreSQL
RabbitMQ.Client
```

## Implementation Phases
- [[Phase 1 – Grain Skeleton]]
- [[Phase 2 – PostgreSQL Integration]]
- [[Phase 3 – RabbitMQ Events]]
- [[Phase 4 – API + End-to-End]]

## Key Learning Outcomes
- Grain design for game entities
- Persistence with PostgreSQL
- Event-driven communication with raw RabbitMQ.Client
- CQRS read/write separation
- BackgroundService consumers in ASP.NET Core
"""

# ─── UPDATE Resources/Recommended Courses ───
files[f"{base}/08 - Resources/Recommended Courses.md"] = """---
tags: [resources, courses]
created: 2026-02-17
---
# 🎓 Recommended Courses & Learning Resources

## Udemy Courses

### RabbitMQ for .NET (Priority: HIGH)
1. **"RabbitMQ by Example"** – practical .NET examples using the raw client
   - Covers all exchange types, routing, error handling
   - ⏱️ ~2.5 hours
   
2. **"RabbitMQ: The Complete Guide with Software Architecture Applications"**
   - Architecture-focused, language-agnostic concepts
   - ⏱️ ~1 hour

3. **"Testing Event-Driven Microservices"** by ExecuteAutomation (Karthik KK)
   - Includes RabbitMQ topic publish/consume with C# .NET
   - Udemy: https://www.udemy.com/course/testing-eda-microservices/
   - ⏱️ ~3 hours

### Entity Framework Core + PostgreSQL (Priority: MEDIUM)
4. **"Entity Framework Core - A Full Tour"** by Trevoir Williams
   - Comprehensive EF Core coverage
   - ⏱️ ~5 hours

### Orleans (limited on Udemy)
5. **"Complete Microsoft Orleans .NET: From Zero to Hero"**
   - Only dedicated Orleans course on Udemy
   - Covers grains, silos, clustering, timers, journaled grains
   - ⏱️ ~4 hours

## Free YouTube (BEST value for your stack)

### RabbitMQ with Raw .NET Client ← YOUR TEAM'S APPROACH
- 🎬 **Milan Jovanović** – "Building Messaging Apps Using the Official RabbitMQ Client"
  - https://www.youtube.com/watch?v=sN5YpfOpCHA
  - Covers: producer, consumer, durable queues, manual ack
- 🎬 **A Coder's Journey** – Full RabbitMQ C#.NET series (7 episodes!)
  - Episode 1: https://www.youtube.com/watch?v=uHbnvukJ3sM
  - Episode 2 (Pub/Sub): https://www.youtube.com/watch?v=iBTgZ4aYXpc
  - Covers: basics, pub/sub, routing, topics, headers, RPC
- 🎬 **Publish/Subscribe with .NET 8 and RabbitMQ** (HOW TO)
  - https://www.youtube.com/watch?v=2xLr9NMPZvM
- 🎬 **Stefan Djokic (TheCodeMan)** – "RabbitMQ in .NET from Scratch"
  - Blog: https://thecodeman.net/posts/rabbitmq-in-dotnet-from-scratch

### Orleans
- 🎬 **"Building a Game with .NET and Orleans"** – On .NET Live
  - https://www.youtube.com/watch?v=xDpQt1RNHvw
- 🎬 **Reuben Bond** – "Introduction to Orleans"
- 📄 **Orleans Adventure Game sample** – official Microsoft
  - https://learn.microsoft.com/en-us/dotnet/orleans/tutorials-and-samples/adventure

### Architecture
- 🎬 **Milan Jovanović** – Modular Monolith + CQRS videos

## Official Documentation (Bookmark These)
- [RabbitMQ .NET Tutorials](https://www.rabbitmq.com/tutorials) ← START HERE for Day 4
- [RabbitMQ .NET API Guide](https://www.rabbitmq.com/docs/dotnet-api-guide)
- [Orleans Docs](https://learn.microsoft.com/en-us/dotnet/orleans/)
- [Npgsql EF Core](https://www.npgsql.org/efcore/)

## GitHub Repos to Study
- [dotnet-rabbitmq examples](https://github.com/drminnaar/dotnet-rabbitmq) – all patterns with raw client
- [Orleans Samples](https://github.com/dotnet/orleans/tree/main/samples)
"""

# ─── UPDATE Architecture Patterns MOC ───
files[f"{base}/05 - Architecture Patterns/Architecture Patterns MOC.md"] = """---
tags: [moc, architecture]
created: 2026-02-17
---
# Architecture Patterns MOC

## Patterns Used at PlayNirvana
- [[CQRS Pattern]]
- [[Event-Driven Architecture]]
- [[Domain-Driven Design Basics]]
- [[Clean Architecture in .NET]]

## Communication Patterns
- [[Synchronous vs Asynchronous Communication]]
- [[Orleans + RabbitMQ – When to Use What]]

## Data Patterns
- [[Event Sourcing]]
- [[Outbox Pattern]]
- [[Read Models and Projections]]

## How They Fit Together
```
Client → API → Orleans Grain (Command/Write)
                    ↓
              Grain State (in-memory + persisted to PostgreSQL)
                    ↓
              Publish Event → RabbitMQ (raw RabbitMQ.Client, fanout exchange)
                    ↓
              BackgroundService Consumer → Update Read Model (PostgreSQL via EF Core)
                    ↓
Client ← API ← Query Read Model (EF Core + LINQ)
```

This is the **CQRS + Event-Driven** flow using Orleans + raw RabbitMQ.
"""

# Write all updated files
for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

# Recreate ZIP
if os.path.exists("PlayNirvana_Learning_Vault.zip"):
    os.remove("PlayNirvana_Learning_Vault.zip")
shutil.make_archive("PlayNirvana_Learning_Vault", 'zip', '.', base)

print(f"✅ Updated vault with raw RabbitMQ.Client (no MassTransit)")
print(f"✅ Created {len(files)} updated files")
print(f"✅ ZIP: PlayNirvana_Learning_Vault.zip")
print(f"\nNew RabbitMQ files:")
for path in sorted(files.keys()):
    if "RabbitMQ" in path or "Rabbit" in path or "04 -" in path:
        print(f"  {path}")
