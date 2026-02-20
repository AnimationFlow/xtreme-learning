// RPC Client

using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Collections.Concurrent;
using System.Text;

public class RpcClient : IAsyncDisposable
{
    const string queueName = "rpc_queue";

    private readonly IConnectionFactory _connectionFactory;
    private readonly ConcurrentDictionary<string, TaskCompletionSource<string>> _callbackMapper = new();

    private IConnection? _connection;
    private IChannel? _channel;
    private string? _responseQueueName;

    public RpcClient()
    {
        _connectionFactory = new ConnectionFactory { HostName = "localhost" };
    }

    public async Task ConnectAsync()
    {
        _connection = await _connectionFactory.CreateConnectionAsync();
        _channel = await _connection.CreateChannelAsync();

        var queueDeclareOk = await _channel.QueueDeclareAsync();
        _responseQueueName = queueDeclareOk.QueueName;

        var consumer = new AsyncEventingBasicConsumer(_channel);

        consumer.ReceivedAsync += (sender, ea) =>
        {
            string? correlationId = ea.BasicProperties.CorrelationId;

            if (!string.IsNullOrEmpty(correlationId))
            {
                if (_callbackMapper.TryRemove(correlationId, out var tcs))
                {
                    var responseBytes = ea.Body.ToArray();
                    var responseMessage = Encoding.UTF8.GetString(responseBytes);
                    tcs.TrySetResult(responseMessage);
                }
            }

            return Task.CompletedTask;
        };

        await _channel.BasicConsumeAsync(
            queue: _responseQueueName,
            autoAck: true,
            consumer: consumer
        );
    }

    public async Task<string> CallAsync(
        string requestMessage,
        CancellationToken cancellationToken = default
    )
    {
        if (_channel is null)
        {
            throw new InvalidOperationException("Connection was not established.");
        }

        var correlationId = Guid.NewGuid().ToString();
        var requestProps = new BasicProperties
        {
            CorrelationId = correlationId,
            ReplyTo = _responseQueueName
        };

        var tcs = new TaskCompletionSource<string>(
            TaskCreationOptions.RunContinuationsAsynchronously
        );

        _callbackMapper.TryAdd(correlationId, tcs);

        var requestBytes = Encoding.UTF8.GetBytes(requestMessage);
        await _channel.BasicPublishAsync(
            exchange: string.Empty,
            routingKey: queueName,
            mandatory: true,
            basicProperties: requestProps,
            body: requestBytes
        );

        using CancellationTokenRegistration ctr = cancellationToken.Register(() =>
        {
            _callbackMapper.TryRemove(correlationId, out _);
            tcs.SetCanceled();
        });

        return await tcs.Task;
    }

    public async ValueTask DisposeAsync()
    {
        if (_channel is not null)
        {
            await _channel.CloseAsync();
        }

        if (_connection is not null)
        {
            await _connection.CloseAsync();
        }
    }
}


public class Rpc
{
    public static async Task Main(string[] args)
    {
        Console.WriteLine(" RPC Client");

        var requestMessage = (args.Length > 0) ? args[0] : "42";
        await InvokeAsync(requestMessage);
    }

    private static async Task InvokeAsync(string n)
    {
        var rpcClient = new RpcClient();
        await rpcClient.ConnectAsync();

        Console.WriteLine($" -> Requesting Fib({n})");
        var response = await rpcClient.CallAsync(n);
        Console.WriteLine($" -> Received : Fib({n}) = {response}");
    }
}
