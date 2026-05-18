using System.Text.Json;
using System.Text.Json.Serialization;

namespace OSCLeash.Models;

public class ConfigSettings
{
	public string IP { get; set; } = "127.0.0.1";
	public int ListeningPort { get; set; } = 9001;
	public int SendingPort { get; set; } = 9000;
	public bool UseOSCQuery { get; set; } = false;

	public float RunDeadzone { get; set; } = 0.70f;
	public float WalkDeadzone { get; set; } = 0.15f;
	public float StrengthMultiplier { get; set; } = 1.2f;
	public float UpDownCompensation { get; set; } = 1.0f;
	public float UpDownDeadzone { get; set; } = 0.5f;

	public bool TurningEnabled { get; set; } = false;
	public float TurningMultiplier { get; set; } = 0.80f;
	public float TurningDeadzone { get; set; } = 0.15f;
	public float TurningGoal { get; set; } = 90f;

	public bool PickupEnabled { get; set; } = false;
	public float PickupMultiplier { get; set; } = 1.0f;
	public float PickupDeadzone { get; set; } = 0.15f;
	public float PickupSmoothing { get; set; } = 0.8f;
	public float PickupCompensation { get; set; } = 45f;

	public bool GravityEnabled { get; set; } = false;
	public float GravityStrength { get; set; } = 9.81f;
	public float TerminalVelocity { get; set; } = 15.0f;

	public int ActiveDelayMs { get; set; } = 20;
	public int InactiveDelayMs { get; set; } = 500;
	public bool Logging { get; set; } = false;

	public string[] PhysboneParameters { get; set; } = { "Leash" };
	public DirectionalParams DirectionalParameters { get; set; } = new();

	public class DirectionalParams
	{
		[JsonPropertyName("Z_Positive_Param")] public string Z_Positive { get; set; } = "Leash_Z+";
		[JsonPropertyName("Z_Negative_Param")] public string Z_Negative { get; set; } = "Leash_Z-";
		[JsonPropertyName("X_Positive_Param")] public string X_Positive { get; set; } = "Leash_X+";
		[JsonPropertyName("X_Negative_Param")] public string X_Negative { get; set; } = "Leash_X-";
		[JsonPropertyName("Y_Positive_Param")] public string Y_Positive { get; set; } = "Leash_Y+";
		[JsonPropertyName("Y_Negative_Param")] public string Y_Negative { get; set; } = "Leash_Y-";
	}
}