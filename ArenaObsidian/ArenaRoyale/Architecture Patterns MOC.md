---
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