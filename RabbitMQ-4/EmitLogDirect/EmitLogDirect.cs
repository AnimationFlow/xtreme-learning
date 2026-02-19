// EmitLogsDirect

using RabbitMQ.Client;
using System.Text;

if (args.Length < 1 || args[0] is not ("info" or "warning" or "error"))
{
    var filename = Path.GetFileName(Environment.ProcessPath);
    Console.Error.WriteLine($"Usage: {filename} [info|warning|error] [message...]");

    Environment.ExitCode = 1;
    return;
}

var severity = args[0];

var factory = new ConnectionFactory { HostName = "localhost" };
using var connection = await factory.CreateConnectionAsync();
using var channel = await connection.CreateChannelAsync();

await channel.ExchangeDeclareAsync(
    exchange: "direct_logs",
    type: ExchangeType.Direct
);

string[] messages = GetMessages(args);

foreach (var message in messages)
{
    var body = Encoding.UTF8.GetBytes(message);

    await channel.BasicPublishAsync(
        exchange: "direct_logs",
        routingKey: severity,
        body: body
    );

    Console.WriteLine($" -> Sent : {severity} - {message}");
}

static string[] GetMessages(string[] args)
{
    return (args.Length > 1) ? args.Skip(1).ToArray() : ["Hello World!"];
}
