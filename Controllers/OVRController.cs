using Valve.VR;
using OSCLeash.Models;

namespace OSCLeash.Controllers;

public class OVRController
{
	private bool _initialized;
	private float _referenceHeight;
	private float _currentVerticalOffset;
	private float _vrVelocity;
	private HmdMatrix34_t _standingZeroPose;

	public bool IsMidair => _currentVerticalOffset > 0.001f;

	public bool Initialize()
	{
		var error = EVRInitError.None;
		OpenVR.Init(ref error, EVRApplicationType.VRApplication_Background);

		if (error != EVRInitError.None)
		{
			Console.ForegroundColor = ConsoleColor.Red;
			Console.WriteLine($"OpenVR failed to initialize, vertical movement disabled");
			switch (error)
			{
				case EVRInitError.Init_NoServerForBackgroundApp:
					Console.WriteLine($"SteamVR is not running. ({error})");
					break;
				default:
					Console.WriteLine($"OpenVR Init Failed: {error}");
					break;
			}
			Console.ResetColor();

			return false;
		}

		try
		{
			var setup = OpenVR.ChaperoneSetup;
			if (setup != null)
			{
				setup.GetWorkingStandingZeroPoseToRawTrackingPose(ref _standingZeroPose);
				_referenceHeight = _standingZeroPose.m7;
				_initialized = true;
				return true;
			}
		}
		catch (Exception ex)
		{
			Console.WriteLine($"Chaperone Error: {ex.Message}");
		}

		return false;
	}

	public void UpdateReferenceHeight()
	{
		if (!_initialized) return;
		var setup = OpenVR.ChaperoneSetup;
		setup?.GetWorkingStandingZeroPoseToRawTrackingPose(ref _standingZeroPose);
		_referenceHeight = _standingZeroPose.m7;
		_currentVerticalOffset = 0;
		_vrVelocity = 0;
	}

	public void ApplyOffset(LeashData leash, ConfigSettings config, float deltaTime)
	{
		if (!_initialized || !config.PickupEnabled) return;

		bool activelyPulling = false;
		float targetVelocity = 0f;

		// 1. Calculate the intended velocity from the leash pull
		if (leash.Grabbed)
		{
			float horizontalMag = MathF.Sqrt((leash.NetX * leash.NetX) + (leash.NetZ * leash.NetZ));
			float pullAngle = MathF.Atan2(MathF.Abs(leash.NetY), horizontalMag) * (180f / MathF.PI);

			if (pullAngle >= config.PickupCompensation && MathF.Abs(leash.NetY) >= config.PickupDeadzone)
			{
				targetVelocity = leash.NetY * config.PickupMultiplier;
				activelyPulling = true;
			}
		}

		// 2. Apply smoothing to the artificial leash movement
		if (activelyPulling)
		{
			_vrVelocity = _vrVelocity * config.PickupSmoothing + targetVelocity * (1f - config.PickupSmoothing);
		}
		else if (leash.Grabbed)
		{
			// If holding the leash but not actively pulling, slowly bleed off artificial upward momentum
			// so gravity can take over smoothly, preventing abrupt snapping.
			_vrVelocity *= config.PickupSmoothing;
		}

		// 3. Apply Gravity
		if (config.GravityEnabled)
		{
			bool pullingUp = activelyPulling && targetVelocity > 0f;

			// Apply gravity if we are in the air and NOT actively pulling ourselves upwards
			if (!pullingUp && _currentVerticalOffset > 0f)
			{
				_vrVelocity -= config.GravityStrength * deltaTime;
			}

			// Enforce maximum falling speed
			_vrVelocity = MathF.Max(_vrVelocity, -config.TerminalVelocity);
		}

		// 4. Update offset and commit to SteamVR
		// Only run the matrix update if we are moving or currently floating
		if (activelyPulling || _currentVerticalOffset > 0f || _vrVelocity != 0f)
		{
			_currentVerticalOffset += _vrVelocity * deltaTime;

			// Floor Clamp: Prevent pushing the user below their real-world floor
			if (_currentVerticalOffset <= 0f)
			{
				_currentVerticalOffset = 0f;
				if (_vrVelocity < 0f) _vrVelocity = 0f;
			}

			// Subtracting the offset pulls the chaperone floor down, raising the player
			_standingZeroPose.m7 = _referenceHeight - _currentVerticalOffset;

			var setup = OpenVR.ChaperoneSetup;
			setup?.SetWorkingStandingZeroPoseToRawTrackingPose(ref _standingZeroPose);
			setup?.CommitWorkingCopy(EChaperoneConfigFile.Live);
		}
	}

	public void Shutdown()
	{
		if (_initialized) OpenVR.Shutdown();
	}
}