---

tags: [moc, postgresql, efcore]

created: 2026-02-17

---

# PostgreSQL + EF Core MOC

  

## Setup

- [[PostgreSQL Docker Setup]]

- [[Npgsql EF Core Provider]]

- [[Connection Strings]]

  

## EF Core Essentials

- [[DbContext Configuration]]

- [[Code-First Migrations]]

- [[Fluent API vs Data Annotations]]

- [[LINQ Queries with EF Core]]

  

## PostgreSQL Specifics

- [[PostgreSQL Data Types in EF Core]]

- [[JSON Columns (jsonb)]]

- [[Array Columns]]

- [[Case Sensitivity – Snake Case Convention]]

  

## Orleans Integration

- [[Orleans ADO.NET Persistence with PostgreSQL]]

- [[Orleans Clustering with PostgreSQL]]

  

## Docker Setup

```bash

docker run -d --name pg-dev \

-e POSTGRES_PASSWORD=devpass \

-e POSTGRES_DB=arena_royale \

-p 5432:5432 \

-v pgdata:/var/lib/postgresql/data \

postgres:17

```