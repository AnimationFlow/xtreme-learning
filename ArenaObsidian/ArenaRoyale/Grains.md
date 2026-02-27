---

tags: [orleans, concept, grain]

created: 2026-02-17

---

# Grains

  

Grains are the **fundamental building blocks** of Orleans – they're virtual actors.

  

## Properties

- **Unique Identity**: Each grain has a key (Guid, long, string, or compound)
- **Single-threaded**: Only one request processes at a time (no locks needed!)
- **Location-transparent**: You don't know/care which silo hosts it
- **Activate on demand**: Created when first called, garbage collected when idle
- **Stateful or stateless**: Can hold in-memory state or use persistence

## Anatomy of a Grain

  

```csharp

// 1. Define the interface

public interface IPlayerGrain : IGrainWithGuidKey

{

Task<string> GetName();

Task SetName(string name);

Task<int> GetScore();

Task AddScore(int points);

}

  

// 2. Implement the grain

public class PlayerGrain : Grain, IPlayerGrain

{

private string _name = "";

private int _score = 0;

  

public Task<string> GetName() => Task.FromResult(_name);

public Task SetName(string name) { _name = name; return Task.CompletedTask; }

public Task<int> GetScore() => Task.FromResult(_score);

public Task AddScore(int points) { _score += points; return Task.CompletedTask; }

}

```

  

## Grain Key Types

| Interface | Key Type | Use Case |
|---|---|---|
| `IGrainWithGuidKey` | Guid | Players, sessions |
| `IGrainWithIntegerKey` | long | Sequential entities |
| `IGrainWithStringKey` | string | Named lookups |
| `IGrainWithGuidCompoundKey` | Guid + string | Multi-tenant |

## Links

- [[Grain Lifecycle]]
- [[Grain State]]
- [[Grain Identity]]
- [[Player as Grain]]
