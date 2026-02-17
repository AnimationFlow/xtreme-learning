---
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