---
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
| Scenario                        | Orleans | RabbitMQ |
| ------------------------------- | :-----: | :------: |
| Player action in game           |    ✅    |          |
| Update leaderboard after match  |         |    ✅     |
| Real-time game state sync       |    ✅    |          |
| Send email notification         |         |    ✅     |
| Cross-service integration       |         |    ✅     |
| Grain-to-grain within cluster   |    ✅    |          |
| Guaranteed event processing     |         |    ✅     |
| Load distribution (work queues) |         |    ✅     |

## Links
- [[Orleans Streams]] – Orleans' built-in streaming (alternative for some cases)
- [[Publishing Messages]]
- [[Consuming Messages]]