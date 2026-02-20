// Receive Logs - Topic

using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;

if (args.Length == 0)
{
    var filename = Path.GetFileName(Environment.ProcessPath);
    Console.Error.WriteLine($"Usage: {filename} [routingKey...]");

    Environment.ExitCode = 1;
    return;
}

var factory = new ConnectionFactory { HostName = "localhost" };
using var connection = await factory.CreateConnectionAsync();
using var channel = await connection.CreateChannelAsync();

await channel.ExchangeDeclareAsync(
    exchange: "topic_logs",
    type: ExchangeType.Topic
);

var queueDeclareResult = await channel.QueueDeclareAsync();
string queueName = queueDeclareResult.QueueName;

foreach (var routingKey in args)
{
    await channel.QueueBindAsync(
        queueName,
        exchange: "topic_logs",
        routingKey
    );
}

Console.WriteLine(" Press <Enter> to exit\n");
Console.WriteLine(" Waiting for messages with routing keys:");
foreach (var key in args)
{
    Console.WriteLine($" - {key}");
}
Console.WriteLine();

var consumer = new AsyncEventingBasicConsumer(channel);

consumer.ReceivedAsync += (model, ea) =>
{
    var body = ea.Body.ToArray();
    var message = Encoding.UTF8.GetString(body);
    Console.WriteLine($" -> Received : {ea.RoutingKey} - {message}");

    return Task.CompletedTask;
};

await channel.BasicConsumeAsync(queueName, autoAck: true, consumer);

Console.ReadLine();
