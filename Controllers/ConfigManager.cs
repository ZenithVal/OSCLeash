using System.Text.Json;
using OSCLeash.Models;

namespace OSCLeash.Controllers;

public static class ConfigManager
{
	private const string ConfigPath = "Config.json";

	public static ConfigSettings Load()
	{
		if (!File.Exists(ConfigPath))
		{
			Console.ForegroundColor = ConsoleColor.Red;
			Console.WriteLine("Config file not found. Creating default...");
			Console.ResetColor();

			var defaultConfig = new ConfigSettings();
			Save(defaultConfig);
			return defaultConfig;
		}

		try
		{
			string json = File.ReadAllText(ConfigPath);
			return JsonSerializer.Deserialize(json, ConfigContext.Default.ConfigSettings) ?? new ConfigSettings();
		}
		catch (Exception ex)
		{
			Console.ForegroundColor = ConsoleColor.Red;
			Console.WriteLine($"Malformed Config.json: {ex.Message}\nLoading defaults.");
			Console.ResetColor();
			return new ConfigSettings();
		}
	}

	public static void PrintSettings(ConfigSettings _config)
	{
		Console.WriteLine("Settings:");

		if (_config.Logging) Console.WriteLine("\tLogging is Enabled");

		if (_config.IP == "127.0.0.1") Console.WriteLine("\tIP: LocalHost");
		else Console.WriteLine($"\tIP: Not Localhost?");

		if (_config.UseOSCQuery) Console.WriteLine("\tUsing OSCQuery");
		else {
			Console.WriteLine($"\tListening Port: {_config.ListeningPort}");
		}
		Console.WriteLine($"\tSending Port: {_config.SendingPort}");

		Console.WriteLine();

		var AllLeashes = new List<string>();
		foreach (string leash in _config.PhysboneParameters)
		{
			if (!string.IsNullOrWhiteSpace(leash))
			{
				AllLeashes.Add(leash);
			}
		}

		Console.WriteLine($"\tLeash Name(s): {string.Join(", ", AllLeashes)}");

		Console.WriteLine($"\tActive Delay: {_config.ActiveDelayMs}ms");
		Console.WriteLine($"\tInactive Delay: {_config.InactiveDelayMs}ms");

		Console.WriteLine($"\tStrength Multiplier: {_config.StrengthMultiplier}");
		Console.WriteLine($"\tRunning Deadzone: {_config.RunDeadzone * 100}% stretch");
		Console.WriteLine($"\tWalking Deadzone: {_config.WalkDeadzone * 100}% stretch");
		Console.WriteLine($"\tUp/Down Compensation: {_config.UpDownCompensation}");
		Console.WriteLine($"\tUp/Down Deadzone: {_config.UpDownDeadzone * 100}% Max Angle");

		Console.WriteLine();
		if (_config.PickupEnabled)
		{
			Console.WriteLine($"\tPickup Movement is Enabled:");
			Console.WriteLine($"\t - Acceleration of {_config.PickupMultiplier}");
			Console.WriteLine($"\t - Deadzone of {_config.PickupDeadzone * 100}% Max Angle");
			Console.WriteLine($"\t - Smoothing of {_config.PickupSmoothing}");
			Console.WriteLine($"\t - Compensation of {_config.PickupCompensation}°");

			if (_config.GravityEnabled)
			{
				Console.WriteLine($"\t - Gravity is Enabled:");
				Console.WriteLine($"\t - Acceleration of {_config.GravityStrength}");
				Console.WriteLine($"\t - Terminal Velocity of {_config.TerminalVelocity}");
			}
			else
			{
				Console.WriteLine($"\t - Gravity is Disabled");
			}
		}
		else
		{
			Console.WriteLine($"\tVertical Movement is Disabled");
		}

		Console.WriteLine();
		if (_config.TurningEnabled)
		{
			Console.WriteLine();
			Console.WriteLine($"\tTurning is Enabled:");
			Console.WriteLine($"\t - Multiplier of {_config.TurningMultiplier}");
			Console.WriteLine($"\t - Deadzone of {_config.TurningDeadzone * 100}% Max Angle");
			Console.WriteLine($"\t - Goal of {_config.TurningGoal}°");
		}
		else
		{
			Console.WriteLine($"\tTurning is Disabled");
		}

		Console.WriteLine();
	}

	private static void Save(ConfigSettings settings)
	{
		string json = JsonSerializer.Serialize(settings, ConfigContext.Default.ConfigSettings);
		File.WriteAllText(ConfigPath, json);
	}
}