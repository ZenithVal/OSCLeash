namespace OSCLeash.Models;

public class LeashData
{
	public string Name { get; }
	public string Direction { get; }

	public float Stretch { get; set; }
	public float Z_Pos { get; set; }
	public float Z_Neg { get; set; }
	public float X_Pos { get; set; }
	public float X_Neg { get; set; }
	public float Y_Pos { get; set; }
	public float Y_Neg { get; set; }

	public bool Grabbed { get; set; }
	public bool WasGrabbed { get; set; }
	public bool Active { get; set; }

	public float NetX => X_Pos - X_Neg;
	public float NetY => Y_Pos - Y_Neg;
	public float NetZ => Z_Pos - Z_Neg;

	public LeashData(string name)
	{
		Name = name;
		var parts = name.Split('_');
		Direction = parts.Length > 1 ? parts[^1] : "North";
	}

	public void ResetMovement()
	{
		Z_Pos = Z_Neg = X_Pos = X_Neg = Y_Pos = Y_Neg = 0;
	}
}