// RPC Server

using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;

const string queueName = "rpc_queue";

var factory = new ConnectionFactory { HostName = "localhost" };
using var connection = await factory.CreateConnectionAsync();
using var channel = await connection.CreateChannelAsync();

await channel.QueueDeclareAsync(
    queue: queueName,
    durable: false,
    exclusive: false,
    autoDelete: false,
    arguments: null
);

await channel.BasicQosAsync(
    prefetchSize: 0,
    prefetchCount: 1,
    global: false
);

Console.WriteLine(" Waiting for RPC requests");
Console.WriteLine(" Press <Enter> to exit");

var consumer = new AsyncEventingBasicConsumer(channel);

consumer.ReceivedAsync += async (object senderObject, BasicDeliverEventArgs ea) =>
{
    var sender = (AsyncEventingBasicConsumer)senderObject;
    var channel = sender.Channel;
    string responseMessage = string.Empty;

    var requestProps = ea.BasicProperties;
    var responseProps = new BasicProperties
    {
        CorrelationId = requestProps.CorrelationId
    };

    try
    {
        var requestBytes = ea.Body.ToArray();
        var requestMessage = Encoding.UTF8.GetString(requestBytes);
        Console.WriteLine($" -> Received : {requestMessage}");

        int n = int.Parse(requestMessage);
        responseMessage = Fib(n).ToString();
        Console.WriteLine($" -> Fib({n}) = {responseMessage}");
    }
    catch (Exception ex)
    {
        Console.WriteLine($" --> Exception : {ex.Message}");
        responseMessage = string.Empty;
    }
    finally
    {
        var responseBytes = Encoding.UTF8.GetBytes(responseMessage);
        await channel.BasicPublishAsync(
            exchange: string.Empty,
            routingKey: requestProps.ReplyTo!,
            mandatory: true,
            basicProperties: responseProps,
            body: responseBytes
        );

        await channel.BasicAckAsync(
            deliveryTag: ea.DeliveryTag,
            multiple: false
        );
    }
};

await channel.BasicConsumeAsync(
    queue: queueName,
    autoAck: false,
    consumer: consumer
);

Console.ReadLine();


static int Fib(int n)
{
    if (n is 0 or 1)
    {
        return n;
    }

    return Fib(n - 1) + Fib(n - 2);
}
