// Receive Logs - Topic

using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;

if (args.Length == 0)
{
    args = ["info", "warning", "error"];
}
else if (args.Any(arg => arg is not ("info" or "warning" or "error")))
{
    var filename = Path.GetFileName(Environment.ProcessPath);
    Console.Error.WriteLine($"Usage: {filename} [info|warning|error] [message...]");

    Environment.ExitCode = 1;
    return;
}

var factory = new ConnectionFactory { HostName = "localhost" };
using var connection = await factory.CreateConnectionAsync();
using var channel = await connection.CreateChannelAsync();

await channel.ExchangeDeclareAsync(
    exchange: "direct_logs",
    type: ExchangeType.Direct
);

var queueDeclareResult = await channel.QueueDeclareAsync();
string queueName = queueDeclareResult.QueueName;

foreach (var severity in args)
{
    await channel.QueueBindAsync(
        queue: queueName,
        exchange: "direct_logs",
        routingKey: severity
    );
}

Console.WriteLine($" Waiting for messages : {string.Join(", ", args)}");
Console.WriteLine(" Press <Enter> to exit");

var consumer = new AsyncEventingBasicConsumer(channel);

consumer.ReceivedAsync += (model, ea) =>
{
    var body = ea.Body.ToArray();
    var message = Encoding.UTF8.GetString(body);
    Console.WriteLine($" -> Received : {ea.RoutingKey} - {message}");

    return Task.CompletedTask;
};

await channel.BasicConsumeAsync(queueName, autoAck: true, consumer: consumer);

Console.ReadLine();
