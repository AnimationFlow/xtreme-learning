// Emit Logs

using RabbitMQ.Client;
using System.Text;

var factory = new ConnectionFactory { HostName = "localhost" };
using var connection = await factory.CreateConnectionAsync();
using var channel = await connection.CreateChannelAsync();

await channel.ExchangeDeclareAsync(
    exchange: "logs",
    type: ExchangeType.Fanout
);

string[] messages = GetMessages(args);

foreach (var message in messages)
{
    var body = Encoding.UTF8.GetBytes(message);

    await channel.BasicPublishAsync(
        exchange: "logs",
        routingKey: string.Empty,
        body: body
    );

    Console.WriteLine($" -> Sent : {message}");
}

static string[] GetMessages(string[] args)
{
    return ((args.Length > 0) ? args : ["Hello World!"]);
}
