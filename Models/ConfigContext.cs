using System.Text.Json.Serialization;

namespace OSCLeash.Models;

[JsonSourceGenerationOptions(WriteIndented = true, ReadCommentHandling = System.Text.Json.JsonCommentHandling.Skip)]
[JsonSerializable(typeof(ConfigSettings))]
[JsonSerializable(typeof(ConfigSettings.DirectionalParams))] // Explicitly map the nested class
public partial class ConfigContext : JsonSerializerContext
{
}