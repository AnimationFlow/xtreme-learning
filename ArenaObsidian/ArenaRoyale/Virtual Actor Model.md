---

tags: [orleans, concept, actor-model]

created: 2026-02-17

---

# Virtual Actor Model

  

The **Virtual Actor Model** is Orleans' key innovation over traditional Actor Model (Akka, Erlang).

  

## Traditional Actor Model

- You must explicitly create and destroy actors

- You manage actor references

- You handle actor placement

  

## Virtual Actor Model (Orleans)

- Actors (grains) **always exist conceptually**

- You just get a reference and call it – Orleans activates if needed

- No explicit lifecycle management

- Automatic placement across the cluster

  

## Why "Virtual"?

Like virtual memory: the grain may not be in physical memory right now, but you can address it as if it is. Orleans handles the activation transparently.

  

## Game Example

```csharp

// You don't check if Player #42 "exists"

// You just talk to it – Orleans handles the rest

var player = grainFactory.GetGrain<IPlayerGrain>(playerId);

await player.AddScore(100); // activates if not already active

```

  

## Links

- [[Grains]]

- [[What is Orleans]]

- [[Grain Lifecycle]]