namespace Connect4.Domain;

public class Player
{
    public string Name { get; set; } = string.Empty;

    public Player(string name)
    {
        Name = name;
    }
}
