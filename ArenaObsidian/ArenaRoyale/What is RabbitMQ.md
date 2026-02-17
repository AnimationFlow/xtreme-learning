---
tags: [rabbitmq, concept, fundamental]
created: 2026-02-17
---
# What is RabbitMQ?

**RabbitMQ** is an open-source message broker that implements the AMQP (Advanced Message Queuing Protocol). It acts as a middleman between applications that produce messages and those that consume them.

## Core Components

| Component | Role |
|---|---|
| **Producer** | Application that sends messages |
| **Exchange** | Receives messages from producers and routes them to queues |
| **Queue** | Buffer that stores messages until consumed |
| **Binding** | Rule connecting an exchange to a queue |
| **Consumer** | Application that receives and processes messages |
| **Routing Key** | Label attached to a message, used by exchanges to route |

## Message Flow
```
Producer → Exchange → Binding(routing key) → Queue → Consumer
```

## Why Use It?
- **Decoupling**: Producers and consumers don't need to know about each other
- **Buffering**: Messages wait in queue if consumer is slow/down
- **Load balancing**: Multiple consumers share work from one queue
- **Guaranteed delivery**: Messages persist until acknowledged

## Links
- [[Exchanges]]
- [[Queues]]
- [[Bindings and Routing Keys]]
- [Official RabbitMQ Tutorials](https://www.rabbitmq.com/tutorials)