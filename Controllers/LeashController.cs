using OSCLeash.Models;

namespace OSCLeash.Controllers;

public class LeashController
{
	private readonly ConfigSettings _config;
	private readonly OVRController _ovr;
	private readonly Action<float, float, float, bool> _oscOutput;

	// Expose the midair status to the main loop
	public bool IsMidair => _ovr != null && _ovr.IsMidair;

	public LeashController(ConfigSettings config, Action<float, float, float, bool> oscOutput)
	{
		_config = config;
		_oscOutput = oscOutput;

		if (_config.PickupEnabled)
		{
			_ovr = new OVRController();
			_config.PickupEnabled = _ovr.Initialize();
			Console.ResetColor();
		}
	}

	public void Process(LeashData leash, float deltaTime)
	{
		if (!leash.Active) return;

		if (leash.Grabbed && !leash.WasGrabbed)
		{
			Console.WriteLine($"{leash.Name} grabbed");
			leash.WasGrabbed = true;
			if (_config.PickupEnabled)
				_ovr.UpdateReferenceHeight();
		}
		else if (!leash.Grabbed && leash.WasGrabbed)
		{
			Console.WriteLine($"{leash.Name} dropped");
			leash.WasGrabbed = false;
			leash.ResetMovement();
			_oscOutput(0f, 0f, 0f, false);
		}

		if (_config.PickupEnabled)
		{
			_ovr.ApplyOffset(leash, _config, deltaTime);
		}

		if (!leash.Grabbed) return;

		float outputMultiplier = leash.Stretch * _config.StrengthMultiplier;
		float vertOut = Math.Clamp((leash.Z_Pos - leash.Z_Neg) * outputMultiplier, -1f, 1f);
		float horiOut = Math.Clamp((leash.X_Pos - leash.X_Neg) * outputMultiplier, -1f, 1f);
		float yCombined = leash.Y_Pos + leash.Y_Neg;

		if (yCombined >= _config.UpDownDeadzone)
		{
			vertOut = 0;
			horiOut = 0;
		}
		else if (_config.UpDownCompensation != 0)
		{
			float yModifier = Math.Clamp(1.0f - (yCombined * _config.UpDownCompensation), 0.1f, 1.0f);
			vertOut /= yModifier;
			horiOut /= yModifier;
		}

		float turnOut = 0f;
		if (_config.TurningEnabled && leash.Stretch > _config.TurningDeadzone)
		{
			turnOut = CalculateTurning(leash, vertOut, horiOut);
		}

		bool run = false;
		if (leash.Stretch > _config.RunDeadzone) run = true;
		else if (leash.Stretch <= _config.WalkDeadzone)
		{
			vertOut = 0; horiOut = 0; turnOut = 0;
		}

		_oscOutput(vertOut, horiOut, turnOut, run);
	}

	private float CalculateTurning(LeashData leash, float vertOut, float horiOut)
	{
		float speed = _config.TurningMultiplier;
		float goalAngle = _config.TurningGoal / 180f;

		switch (leash.Direction)
		{
			case "North":
				if (leash.Z_Pos < goalAngle) return (speed * horiOut) + (leash.X_Pos > leash.X_Neg ? leash.Z_Neg : -leash.Z_Neg);
				break;
			case "South":
				if (leash.Z_Neg < goalAngle) return (speed * -horiOut) + (leash.X_Pos > leash.X_Neg ? -leash.Z_Pos : leash.Z_Pos);
				break;
			case "East":
				if (leash.X_Pos < goalAngle) return (speed * vertOut) + (leash.Z_Pos > leash.Z_Neg ? leash.X_Neg : -leash.X_Neg);
				break;
			case "West":
				if (leash.X_Neg < goalAngle) return (speed * -vertOut) + (leash.Z_Pos > leash.Z_Neg ? -leash.X_Pos : leash.X_Pos);
				break;
		}
		return 0f;
	}

	public void Shutdown() => _ovr?.Shutdown();
}