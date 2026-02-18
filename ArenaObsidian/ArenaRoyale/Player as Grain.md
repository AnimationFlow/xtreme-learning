---

tags: [orleans, pattern, game]

created: 2026-02-17

---

# Player as Grain

  

In game backends with Orleans, each **player is represented as a grain**.

  

## Why?

- Each player has unique state (name, score, inventory, session)

- Players need to handle concurrent actions safely

- Orleans single-threaded execution eliminates race conditions

- Players activate when they log in, deactivate when idle

  

## Implementation

```csharp

public interface IPlayerGrain : IGrainWithGuidKey

{

Task<PlayerState> GetState();

Task JoinArena(Guid arenaId);

Task LeaveArena();

Task AddScore(int points);

Task<List<Item>> GetInventory();

Task AddItem(Item item);

}

  

[GenerateSerializer]

public class PlayerState

{

[Id(0)] public string Name { get; set; } = "";

[Id(1)] public int Score { get; set; }

[Id(2)] public Guid? CurrentArenaId { get; set; }

[Id(3)] public List<Item> Inventory { get; set; } = new();

}

  

public class PlayerGrain : Grain, IPlayerGrain

{

private readonly IPersistentState<PlayerState> _state;

  

public PlayerGrain(

[PersistentState("player", "PostgresStore")]

IPersistentState<PlayerState> state)

{

_state = state;

}

  

public Task<PlayerState> GetState() => Task.FromResult(_state.State);

  

public async Task AddScore(int points)

{

_state.State.Score += points;

await _state.WriteStateAsync();

}

  

public async Task JoinArena(Guid arenaId)

{

_state.State.CurrentArenaId = arenaId;

await _state.WriteStateAsync();

  

// Tell the arena grain about this player

var arena = GrainFactory.GetGrain<IArenaGrain>(arenaId);

await arena.PlayerJoined(this.GetPrimaryKey());

}

  

// ... other methods

}

```

  

## Key Points

- Use `IPersistentState<T>` to persist to PostgreSQL

- Grain-to-grain communication is just method calls

- The `GrainFactory` gives you references to other grains

  

## Links

- [[Grains]]

- [[Grain State]]

- [[Game Session as Grain]]