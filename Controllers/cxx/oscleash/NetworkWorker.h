#pragma once

#include <vector>
#include <string>
#include <filesystem>

struct Config
{
    std::string IP = "127.0.0.1";
    unsigned short ListeningPort = 9001;
    unsigned short SendingPort = 9000;
    float RunDeadzone = 0.70;
    float WalkDeadzone = 0.15;
    float StrengthMultiplier = 1.2;
    float UpDownCompensation = 1.0;
    float UpDownDeadzone = 0.5;
    bool TurningEnabled = false;
    float TurningMultiplier = 0.8;
    float TurningDeadzone = 0.15;
    float TurningGoal = 90;
    float ActiveDelay = 0.02;
    float InactiveDelay = 0.5;
    bool Logging = false;
    bool XboxJoystickMovement = false;
    bool UseOSCQuery = false;
    std::vector<std::string> physboneParameters = { "Leash" };
    std::string Z_Positive_Param = "Leash_Z+";
    std::string Z_Negative_Param = "Leash_Z-";
    std::string X_Positive_Param = "Leash_X+";
    std::string X_Negative_Param = "Leash_X-";
    std::string Y_Positive_Param = "Leash_Y+";
    std::string Y_Negative_Param = "Leash_Y-";

    void load(const std::filesystem::path& confFile);
    void save(const std::filesystem::path& confFile);
};

#include <thread>
#include <condition_variable>
#include <variant>
#include "framework.h"

struct AvatarParameter
{
    std::string name;
    using argument = std::variant<bool, float, int>;
    argument data;
};

class NetworkWorker
{
    std::vector<AvatarParameter> parameterSet;
    std::atomic<bool> stopToken{false};
    std::atomic<bool> debug{false};
    std::condition_variable activeCV;
    std::mutex receiverActiveMtx;
    std::thread receiverWorker;
    void receiverFunc(Config conf);
    std::thread senderWorker;
    void senderFunc(Config conf);
public:
    HWND windowHandle;
    ~NetworkWorker()
    {
        stop();
    }
    void run(Config config);
    void stop();
    void setDebug(bool b)
    {
        debug.store(b, std::memory_order_release);
    }
};

