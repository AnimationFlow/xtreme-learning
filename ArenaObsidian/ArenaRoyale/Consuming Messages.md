---
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