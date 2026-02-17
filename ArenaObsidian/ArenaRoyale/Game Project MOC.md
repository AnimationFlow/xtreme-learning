---
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