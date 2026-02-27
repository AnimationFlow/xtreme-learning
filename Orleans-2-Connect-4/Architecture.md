
## User Flows

### Lobby flow
```
Open app → See lobby:
  ├── Active games list (InProgress / WaitingForPlayer)
  ├── Player list (online / idle)
  └── [New Game] button

Click "New Game" → creates game, you're Player 1, waiting for opponent
Click "Join" on open game → you become Player 2, game starts
Click "Invite" on player → sends invite to that player
Invited player sees notification → accepts/declines
```

### Game flow
```
Game starts → both consoles/tabs show board
Player 1 drops piece → board updates for both
Player 2 drops piece → board updates for both
Win / Draw → game over screen → back to lobby
```

### Observer flow
```
Click "Watch" on InProgress game → read-only board, live updates
No moves allowed, just spectating
```

***

## What this reveals architecturally

You need **three grain types** not two, and a **lobby concept** that didn't exist before:

1. **`IGameGrain`** — the game itself (board, moves, state)
2. **`IPlayerGrain`** — player identity + presence + active games + pending invites
3. **`ILobbyGrain`** — **singleton** grain (key = `"lobby"`) that tracks all active/open games and online players; the "directory"

RabbitMQ gets richer too — it's not just game events, it also carries lobby events:
- `PlayerOnlineEvent`, `PlayerOfflineEvent`
- `GameCreatedEvent`, `GameOpenedEvent` (waiting for 2nd player)
- `InviteSentEvent`, `InviteResponseEvent`

***

## Revised Full Architecture

```
Connect-4/
├── Connect-4.slnx
│
├── Connect4.Domain/                    # pure C#, zero framework deps
│   ├── Board.cs                        # 7x6 grid, drop, win detection
│   ├── GameState.cs                    # board + status + players + turn
│   ├── PlayerInfo.cs                   # id, display name, color
│   ├── GameSummary.cs                  # lightweight lobby entry (id, status, players)
│   ├── MoveResult.cs                   # Ok / InvalidColumn / ColumnFull / GameOver / NotYourTurn
│   ├── GameStatus.cs                   # enum: Open / InProgress / Finished / Abandoned
│   └── InviteStatus.cs                 # enum: Pending / Accepted / Declined
│
├── Connect4.Contracts/
│   ├── Grains/
│   │   ├── IGameGrain.cs
│   │   ├── IPlayerGrain.cs
│   │   └── ILobbyGrain.cs
│   └── Events/                         # RMQ message contracts
│       ├── Lobby/
│       │   ├── GameCreatedEvent.cs
│       │   ├── GameStartedEvent.cs
│       │   ├── GameFinishedEvent.cs
│       │   └── PlayerPresenceEvent.cs  # Online / Offline
│       └── Game/
│           ├── MoveMadeEvent.cs
│           ├── GameOverEvent.cs
│           └── InviteEvent.cs          # Sent / Accepted / Declined
│
├── Connect4.Api/                       # co-hosted silo + HTTP API
│   ├── Program.cs
│   ├── Grains/
│   │   ├── GameGrain.cs                # internal sealed
│   │   ├── PlayerGrain.cs              # internal sealed
│   │   └── LobbyGrain.cs              # internal sealed, singleton
│   ├── Publishing/
│   │   └── GameEventPublisher.cs       # wraps RMQ publish, called from grains
│   └── Connect4.Api.csproj
│
└── Connect4.Client/                    # game client
    ├── Program.cs
    ├── Screens/
    │   ├── LobbyScreen.cs              # shows games + players
    │   ├── GameScreen.cs               # board + input
    │   └── InviteScreen.cs             # pending invite notification
    ├── Rendering/
    │   ├── IRenderer.cs
    │   └── ConsoleRenderer.cs
    ├── Http/
    │   └── GameApiClient.cs            # typed HTTP client wrapping API calls
    ├── Messaging/
    │   └── GameEventConsumer.cs        # RMQ subscriber, dispatches to screens
    └── Connect4.Client.csproj
```

***

## Grain Responsibilities

### `ILobbyGrain` — singleton, key = `"lobby"`
```csharp
public interface ILobbyGrain : IGrainWithStringKey
{
    Task<List<GameSummary>> GetOpenGames();
    Task<List<GameSummary>> GetActiveGames();
    Task<List<PlayerInfo>> GetOnlinePlayers();
    Task RegisterGame(string gameId);
    Task RemoveGame(string gameId);
    Task PlayerOnline(string playerId, string displayName);
    Task PlayerOffline(string playerId);
}
```
The lobby is the **directory** — it doesn't play the game, it just tracks what exists. Clients poll it (or receive `LobbyUpdatedEvent` via RMQ) to render the lobby screen.

### `IGameGrain` — key = `gameId`
```csharp
public interface IGameGrain : IGrainWithStringKey
{
    Task<GameState> Create(string playerOneId);
    Task<MoveResult> Join(string playerTwoId);
    Task<MoveResult> MakeMove(string playerId, int column);
    Task<GameState> GetState();
    Task Resign(string playerId);
    Task AddObserver(string observerId);    // for spectators
}
```

### `IPlayerGrain` — key = `playerId`
```csharp
public interface IPlayerGrain : IGrainWithStringKey
{
    Task SetOnline(string displayName);
    Task SetOffline();
    Task<PlayerInfo> GetInfo();
    Task AddActiveGame(string gameId);
    Task RemoveActiveGame(string gameId);
    Task<List<string>> GetActiveGames();    // multi-game support
    Task ReceiveInvite(string fromPlayerId, string gameId);
    Task<List<InviteInfo>> GetPendingInvites();
    Task RespondToInvite(string gameId, bool accepted);
}
```

***

## RabbitMQ Exchange Design

One **topic exchange** `connect4`, routing keys by domain:

```
lobby.game.created          → GameCreatedEvent       (new open game)
lobby.game.started          → GameStartedEvent       (2nd player joined)
lobby.game.finished         → GameFinishedEvent      (game over / abandoned)
lobby.player.online         → PlayerPresenceEvent
lobby.player.offline        → PlayerPresenceEvent

game.{gameId}.move          → MoveMadeEvent
game.{gameId}.over          → GameOverEvent
game.{gameId}.invite        → InviteEvent
```

**Client bindings:**
- Lobby screen binds to `lobby.*` — gets all lobby updates
- Game screen binds to `game.{gameId}.*` — gets only its game's updates
- A spectator binds to `game.{gameId}.*` read-only — same queue, no writes

This is why RMQ shines here: the same event infrastructure handles players, spectators, and future web clients without changing the silo.

***

## HTTP API Surface

```
# Lobby
GET    /lobby/games                     → open + active games
GET    /lobby/players                   → online players

# Players
POST   /players                         → register + go online   { displayName }
DELETE /players/{playerId}              → go offline
GET    /players/{playerId}/invites      → pending invites
POST   /players/{playerId}/invites/{gameId}  → respond to invite { accepted: bool }

# Games
POST   /games                           → create new game        { playerId }
POST   /games/{gameId}/join             → join open game         { playerId }
GET    /games/{gameId}                  → get full game state
POST   /games/{gameId}/move             → make move              { playerId, column }
POST   /games/{gameId}/resign           → resign                 { playerId }
POST   /games/{gameId}/observe          → add observer           { playerId }
```

***

## Phases

### Phase 1 — Core game, no lobby, no invites
- `Connect4.Domain`: `Board`, `GameState`, `MoveResult`, `GameStatus`
- `Connect4.Contracts`: `IGameGrain`, `MoveMadeEvent`, `GameOverEvent`
- `Connect4.Api`: `GameGrain` + `/games` endpoints + RMQ publisher
- `Connect4.Client`: `GameScreen` + `ConsoleRenderer` + `GameEventConsumer`
- Two players on same machine, two console windows, same `gameId`
- **Validates:** Orleans grain state, RMQ fan-out to two consoles, board logic

### Phase 2 — Player identity + lobby
- `IPlayerGrain`, `ILobbyGrain` + grain impls
- `/lobby`, `/players` endpoints
- `LobbyScreen` in client
- `PlayerPresenceEvent`, `GameCreatedEvent`, `GameStartedEvent`
- **Validates:** multi-grain coordination, lobby pattern, presence

### Phase 3 — Invites + multi-game
- `InviteEvent`, `IPlayerGrain.ReceiveInvite/RespondToInvite`
- `InviteScreen` in client
- Multiple simultaneous games per player
- **Validates:** player grain as real stateful entity

### Phase 4 — Docker + 2 silos
- Update `Dockerfile` context for multi-project solution
- `compose.yaml` with 2 `connect4-api` replicas
- Verify grain migration between silos
- **Validates:** clustering with real game traffic

### Phase 5 — Angular front-end
- New project `Connect4.Web` (Angular)
- SignalR hub in `Connect4.Api` alongside RMQ consumer
- RMQ events → SignalR push to browser
- `Connect4.Client` console stays as reference/debug tool
- **Validates:** event-driven architecture with multiple consumer types

***
