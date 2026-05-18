using System.Diagnostics;
using System.Net;
using VRC.OSCQuery;
using OSCLeash.Controllers;
using OSCLeash.Models;
using FastOSC;

namespace OSCLeash;

class Program
{
	private static ConfigSettings _config = null!;
	private static List<LeashData> _leashes = new();
	private static OSCSender _oscSender = null!;
	private static OSCReceiver _oscReceiver = null!;
	private static OSCQueryService? _oscQuery;
	private static string _applicationVersion = "OSCLeash " + "VERSION_PLACEHOLDER";

	static async Task Main(string[] args)
	{
		if (_applicationVersion.Contains("VERSION_PLACEHOLDER"))
		{
			_applicationVersion = "OSCLeash (Local Build)";
		}

		Console.Title = "OSCLeash";
		Console.ForegroundColor = ConsoleColor.Green;
		Console.WriteLine(_applicationVersion);
		Console.ResetColor();

		_config = ConfigManager.Load();
		ConfigManager.PrintSettings(_config);

		foreach (var name in _config.PhysboneParameters)
			_leashes.Add(new LeashData(name));

		if (_leashes.Count == 0) throw new Exception("No leashes found in config.");

		var _listeningport = _config.ListeningPort;
		if (_config.UseOSCQuery)
		{
			int udpPort = Extensions.GetAvailableUdpPort();
			int tcpPort = Extensions.GetAvailableTcpPort();

			_oscQuery = new OSCQueryServiceBuilder()
				.WithServiceName(_applicationVersion)
				.WithUdpPort(udpPort)
				.WithTcpPort(tcpPort)
				.WithDefaults()
				.Build();

			AdvertiseEndpoints();

			_listeningport = udpPort;
		}

		_oscReceiver = new OSCReceiver();
		_oscReceiver.OnPacketReceived += OnPacketReceived;
		_oscReceiver.Connect(new IPEndPoint(IPAddress.Parse(_config.IP), _listeningport));

		await InitializeSender(_config.SendingPort);

		var leashController = new LeashController(_config, SendOscOutput);

		Console.WriteLine("\nStarted, awaiting input.\n");

		Stopwatch sw = Stopwatch.StartNew();
		while (true)
		{
			float dt = (float)sw.Elapsed.TotalSeconds;
			sw.Restart();

			foreach (var leash in _leashes)
			{
				leashController.Process(leash, dt);
				while (leash.Grabbed || leashController.IsMidair)
				{
					await Task.Delay(_config.ActiveDelayMs);
					dt = (float)sw.Elapsed.TotalSeconds;
					sw.Restart();
					leashController.Process(leash, dt);
				}
				await Task.Delay(_config.ActiveDelayMs);
				SendOscOutput(0f, 0f, 0f, false);
			}
			await Task.Delay(_config.InactiveDelayMs);
		}
	}

	private static async Task InitializeSender(int port)
	{
		_oscSender = new OSCSender();
		await _oscSender.ConnectAsync(new IPEndPoint(IPAddress.Parse(_config.IP), port));
	}

	private static Task OnPacketReceived(IOSCPacket packet)
	{
		if (packet is OSCMessage msg)
		{
			object? value = msg.Arguments.FirstOrDefault();
			HandleMessage(msg.Address, value);
		}

		return Task.CompletedTask;
	}

	private static void HandleMessage(string address, object? value)
	{
		if (value is not float fVal && value is not bool bVal) return;
		float val = value is bool b ? (b ? 1f : 0f) : (float)value!;

		foreach (var leash in _leashes)
		{
			if (address.EndsWith($"{leash.Name}_Stretch")) leash.Stretch = val;
			else if (address.EndsWith($"{leash.Name}_IsGrabbed"))
			{
				leash.Grabbed = val > 0;
				if (leash.Grabbed) leash.Active = true;
			}
			else if (address.EndsWith(_config.DirectionalParameters.Z_Positive)) leash.Z_Pos = val;
			else if (address.EndsWith(_config.DirectionalParameters.Z_Negative)) leash.Z_Neg = val;
			else if (address.EndsWith(_config.DirectionalParameters.X_Positive)) leash.X_Pos = val;
			else if (address.EndsWith(_config.DirectionalParameters.X_Negative)) leash.X_Neg = val;
			else if (address.EndsWith(_config.DirectionalParameters.Y_Positive)) leash.Y_Pos = val;
			else if (address.EndsWith(_config.DirectionalParameters.Y_Negative)) leash.Y_Neg = val;
		}
	}

	public static void SendOscOutput(float vert, float hori, float turn, bool run)
	{
		_oscSender.Send(new OSCMessage("/input/Vertical", vert));
		_oscSender.Send(new OSCMessage("/input/Horizontal", hori));
		_oscSender.Send(new OSCMessage("/input/Run", run));
		if (_config.TurningEnabled) _oscSender.Send(new OSCMessage("/input/LookHorizontal", turn));

		if (_config.Logging)
		{
			Console.WriteLine($"\tVert: {vert:F2} | Hori: {hori:F2} | Run: {run} | Turn: {turn:F2}");
		}
	}

	private static void AdvertiseEndpoints()
	{
		if (_oscQuery == null) return;

		_oscQuery.AddEndpoint("/input/Vertical", "f", Attributes.AccessValues.WriteOnly);
		_oscQuery.AddEndpoint("/input/Horizontal", "f", Attributes.AccessValues.WriteOnly);
		_oscQuery.AddEndpoint("/input/Run", "b", Attributes.AccessValues.WriteOnly);
		if (_config.TurningEnabled) _oscQuery.AddEndpoint("/input/LookHorizontal", "f", Attributes.AccessValues.WriteOnly);

		foreach (var leash in _leashes)
		{
			_oscQuery.AddEndpoint($"/avatar/parameters/{leash.Name}_Stretch", "f", Attributes.AccessValues.ReadOnly);
			_oscQuery.AddEndpoint($"/avatar/parameters/{leash.Name}_IsGrabbed", "b", Attributes.AccessValues.ReadOnly);
		}

		_oscQuery.AddEndpoint($"/avatar/parameters/{_config.DirectionalParameters.Z_Positive}", "f", Attributes.AccessValues.ReadOnly);
		_oscQuery.AddEndpoint($"/avatar/parameters/{_config.DirectionalParameters.Z_Negative}", "f", Attributes.AccessValues.ReadOnly);
		_oscQuery.AddEndpoint($"/avatar/parameters/{_config.DirectionalParameters.X_Positive}", "f", Attributes.AccessValues.ReadOnly);
		_oscQuery.AddEndpoint($"/avatar/parameters/{_config.DirectionalParameters.X_Negative}", "f", Attributes.AccessValues.ReadOnly);
		_oscQuery.AddEndpoint($"/avatar/parameters/{_config.DirectionalParameters.Y_Positive}", "f", Attributes.AccessValues.ReadOnly);
		_oscQuery.AddEndpoint($"/avatar/parameters/{_config.DirectionalParameters.Y_Negative}", "f", Attributes.AccessValues.ReadOnly);
	}
}