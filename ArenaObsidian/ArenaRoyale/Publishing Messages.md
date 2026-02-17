---
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