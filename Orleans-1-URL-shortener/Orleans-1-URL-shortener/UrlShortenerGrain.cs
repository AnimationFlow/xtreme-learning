public interface IUrlShortenerGrain : IGrainWithStringKey
{
    Task SetUrl(string fullUrl);
    Task<string> GetUrl();
    Task<UrlDetails> GetStateAsync();
}

public sealed class UrlShortenerGrain(
    [PersistentState(stateName: "url", storageName: "urls")]
    IPersistentState<UrlDetails> state
) : Grain, IUrlShortenerGrain
{
    public async Task SetUrl(string fullUrl)
    {
        state.State = new()
        {
            ShortenedRouteSegment = this.GetPrimaryKeyString(),
            FullUrl = fullUrl
        };

        await state.WriteStateAsync();
    }

    public Task<string> GetUrl() => Task.FromResult(state.State.FullUrl);

    public Task<UrlDetails> GetStateAsync() => Task.FromResult(state.State);
}

[GenerateSerializer, Alias(nameof(UrlDetails))]
public class UrlDetails
{
    [Id(0)]
    public string FullUrl { get; set; } = string.Empty;

    [Id(1)]
    public string ShortenedRouteSegment { get; set; } = string.Empty;
}
