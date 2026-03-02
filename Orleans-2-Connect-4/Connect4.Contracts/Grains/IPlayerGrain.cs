using Connect4.Domain;

namespace Connect4.Contracts.Grains;

public interface IPlayerGrain : IGrainWithStringKey
{
    Task<Player> RegisterPlayerAsync();
}
