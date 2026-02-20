// Emit Logs - Topic

using RabbitMQ.Client;
using System.Text;

if (args.Length < 2)
{
    var filename = Path.GetFileName(Environment.ProcessPath);
    Console.Error.WriteLine($"Usage: {filename} [routingKey] [message...]");

    Environment.ExitCode = 1;
    return;
}

var routingKey = args[0];

var factory = new ConnectionFactory { HostName = "localhost" };
using var connection = await factory.CreateConnectionAsync();
using var channel = await connection.CreateChannelAsync();

await channel.ExchangeDeclareAsync(
    exchange: "topic_logs",
    type: ExchangeType.Topic
);

string[] messages = GetMessages(args);

foreach (var message in messages)
{
    var body = Encoding.UTF8.GetBytes(message);

    await channel.BasicPublishAsync(
        exchange: "topic_logs",
        routingKey,
        body
    );

    Console.WriteLine($" -> Sent : {routingKey} - {message}");
}

static string[] GetMessages(string[] args)
{
    return (args.Length > 1) ? args.Skip(1).ToArray() : ["Hello World!"];
}
