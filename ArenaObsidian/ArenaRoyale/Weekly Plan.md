---
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