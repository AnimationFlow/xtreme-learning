public interface IUrlShortenerGrain : IGrainWithStringKey
{
    Task SetUrl(string fullUrl);
    Task<string?> GetUrl();

    // Only for Orleans Dashboard inspection purposes
    Task<UrlDetails> GetStateAsync();
}

public sealed class UrlShortenerGrain(
    [PersistentState(stateName: "url", storageName: "urls")]
    IPersistentState<UrlDetails> state
) : Grain, IUrlShortenerGrain
{
    public async Task SetUrl(string fullUrl)
    {
        if (state.RecordExists && state.State.FullUrl == fullUrl)
            return;

        state.State = new()
        {
            ShortenedRouteSegment = this.GetPrimaryKeyString(),
            FullUrl = fullUrl
        };

        await state.WriteStateAsync();
    }

    public Task<string?> GetUrl()
    {
        if (!state.RecordExists || string.IsNullOrEmpty(state.State.FullUrl))
            return Task.FromResult<string?>(null);

        return Task.FromResult<string?>(state.State.FullUrl);
    }

    public Task<UrlDetails> GetStateAsync()
    {
        return Task.FromResult(state.State);
    }
}

[GenerateSerializer, Alias(nameof(UrlDetails))]
public class UrlDetails
{
    [Id(0)]
    public string FullUrl { get; set; } = string.Empty;

    [Id(1)]
    public string ShortenedRouteSegment { get; set; } = string.Empty;
}
