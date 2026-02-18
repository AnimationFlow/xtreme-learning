// New Task

using RabbitMQ.Client;
using System.Text;

var factory = new ConnectionFactory { HostName = "localhost" };
using var connection = await factory.CreateConnectionAsync();
using var channel = await connection.CreateChannelAsync();

await channel.QueueDeclareAsync(queue: "task_queue", durable: true, exclusive: false, autoDelete: false, arguments: null);

string[] messages = GetMessages(args);

foreach (var message in messages)
{
    var body = Encoding.UTF8.GetBytes(message);

    await channel.BasicPublishAsync(exchange: string.Empty, routingKey: "task_queue", body: body);
    Console.WriteLine($" -> Sent : {message}");
}

Console.WriteLine();

static string[] GetMessages(string[] args)
{
    return ((args.Length > 0) ? args : ["Hello World!"]);
}
