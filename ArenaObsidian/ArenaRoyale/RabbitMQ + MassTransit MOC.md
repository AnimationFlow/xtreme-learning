---

tags: [moc, rabbitmq, masstransit]

created: 2026-02-17

---

# RabbitMQ + MassTransit MOC

  

## RabbitMQ Fundamentals

- [[What is RabbitMQ]]

- [[Exchanges and Queues]]

- [[Routing and Bindings]]

- [[Message Acknowledgment]]

  

## MassTransit

- [[What is MassTransit]]

- [[MassTransit Configuration]]

- [[Consumers]]

- [[Publish vs Send]]

- [[Request-Response Pattern]]

- [[Saga State Machine]]

  

## Patterns

- [[Pub-Sub with MassTransit]]

- [[Event-Driven Architecture]]

- [[Outbox Pattern]]

- [[Retry and Error Handling]]

  

## Integration

- [[Orleans + RabbitMQ – When to Use What]]

- [[MassTransit + PostgreSQL for Saga State]]

  

## Docker Setup

```bash

docker run -d --name rabbitmq \

-p 5672:5672 -p 15672:15672 \

-e RABBITMQ_DEFAULT_USER=guest \

-e RABBITMQ_DEFAULT_PASS=guest \

rabbitmq:3-management

```

Management UI: http://localhost:15672