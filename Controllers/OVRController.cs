using Valve.VR;
using OSCLeash.Models;

namespace OSCLeash.Controllers;

public class OVRController
{
	private bool _initialized;
	private float _currentVerticalOffset;
	private float _vrVelocity;

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

		_initialized = OpenVR.ChaperoneSetup != null;
		return _initialized;
	}

	public void ApplyOffset(LeashData leash, ConfigSettings config, float deltaTime)
	{
		if (!_initialized || !config.PickupEnabled) return;

		bool activelyPulling = false;
		float targetVelocity = 0f;

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

		if (activelyPulling)
		{
			_vrVelocity = _vrVelocity * config.PickupSmoothing + targetVelocity * (1f - config.PickupSmoothing);
		}
		else if (leash.Grabbed)
		{
			_vrVelocity = 0f;
		}

		if (!leash.Grabbed && config.GravityEnabled)
		{
			if (_currentVerticalOffset > 0f)
			{
				_vrVelocity -= config.GravityStrength * deltaTime;
				_vrVelocity = MathF.Max(_vrVelocity, -config.TerminalVelocity);
			}
		}

		if (activelyPulling || _currentVerticalOffset > 0f || _vrVelocity != 0f)
		{
			float deltaY = _vrVelocity * deltaTime;

			if (_currentVerticalOffset + deltaY <= 0f)
			{
				deltaY = -_currentVerticalOffset;
				_currentVerticalOffset = 0f;
				if (_vrVelocity < 0f) _vrVelocity = 0f;
			}
			else
			{
				_currentVerticalOffset += deltaY;
			}

			// Only if actual movement
			if (MathF.Abs(deltaY) > 0.0001f)
			{
				var setup = OpenVR.ChaperoneSetup;
				if (setup != null)
				{
					// LIVE matrix every frame so we don't overwrite OVRAS
					HmdMatrix34_t livePose = new HmdMatrix34_t();
					setup.GetWorkingStandingZeroPoseToRawTrackingPose(ref livePose);

					livePose.m7 -= deltaY;

					setup.SetWorkingStandingZeroPoseToRawTrackingPose(ref livePose);
					setup.CommitWorkingCopy(EChaperoneConfigFile.Live);
				}
			}
		}
	}

	public void Shutdown()
	{
		if (_initialized) OpenVR.Shutdown();
	}
}