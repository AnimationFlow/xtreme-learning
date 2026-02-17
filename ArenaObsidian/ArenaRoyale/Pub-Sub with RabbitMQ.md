---
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