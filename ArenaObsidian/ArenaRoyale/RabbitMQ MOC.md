---
tags: [moc, rabbitmq]
created: 2026-02-17
---
# RabbitMQ MOC (Map of Content)

> Using the **raw RabbitMQ.Client** library – no MassTransit abstraction.

## Core Concepts
- [[What is RabbitMQ]]
- [[AMQP Protocol Basics]]
- [[Exchanges]]
- [[Queues]]
- [[Bindings and Routing Keys]]
- [[Message Acknowledgment]]

## Exchange Types
- [[Direct Exchange]]
- [[Fanout Exchange]]
- [[Topic Exchange]]
- [[Headers Exchange]]

## .NET Integration
- [[RabbitMQ.Client Setup]]
- [[ConnectionFactory and Channels]]
- [[Publishing Messages]]
- [[Consuming Messages]]
- [[AsyncEventingBasicConsumer]]
- [[Message Serialization (JSON)]]
- [[Durable Queues and Persistent Messages]]

## Patterns
- [[Pub-Sub with RabbitMQ]]
- [[Work Queues (Competing Consumers)]]
- [[Request-Reply Pattern]]
- [[Dead Letter Exchanges]]
- [[Retry with Delayed Requeue]]

## Integration with Orleans
- [[Orleans + RabbitMQ – When to Use What]]
- [[Publishing from Grains]]

## Docker Setup
```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=guest \
  -e RABBITMQ_DEFAULT_PASS=guest \
  rabbitmq:3-management
```
Management UI: http://localhost:15672