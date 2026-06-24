#include "NetworkWorker.h"
#include "handles.hpp"
#include "simdjson.h"
#include <fstream>
#include <WinSock2.h>
#include <format>
#include <ws2tcpip.h>
#include <WinUser.h>
#include <vector>
#include <bit>

using namespace std::literals;

void Config::load(const std::filesystem::path& confFile)
{
    if (!std::filesystem::exists(confFile))
    {
        return;
    }
    simdjson::ondemand::parser parser;
    simdjson::padded_string json = simdjson::padded_string::load(confFile.generic_string());
    simdjson::ondemand::document configDocument = parser.iterate(json);

    if (auto ip = configDocument["IP"sv].get_string(); ip.has_value())
    {
        IP = *ip;
    }
    if (auto lp = configDocument["ListeningPort"sv].get_uint32(); lp.has_value())
    {
        ListeningPort = *lp;
    }
    if (auto sp = configDocument["SendingPort"sv].get_uint32(); sp.has_value())
    {
        SendingPort = *sp;
    }
    if (auto rd = configDocument["RunDeadzone"sv].get_double(); rd.has_value())
    {
        RunDeadzone = *rd;
    }
    if (auto wd = configDocument["WalkDeadzone"sv].get_double(); wd.has_value())
    {
        WalkDeadzone = *wd;
    }
    if (auto sm = configDocument["StrengthMultiplier"sv].get_double(); sm.has_value())
    {
        StrengthMultiplier = *sm;
    }
    if (auto udc = configDocument["UpDownCompensation"sv].get_double(); udc.has_value())
    {
        UpDownCompensation = *udc;
    }
    if (auto udd = configDocument["UpDownDeadzone"sv].get_double(); udd.has_value())
    {
        UpDownDeadzone = *udd;
    }
    if (auto te = configDocument["TurningEnabled"sv].get_bool(); te.has_value())
    {
        TurningEnabled = *te;
    }
    if (auto tm = configDocument["TurningMultiplier"sv].get_double(); tm.has_value())
    {
        TurningMultiplier = *tm;
    }
    if (auto td = configDocument["TurningDeadzone"sv].get_double(); td.has_value())
    {
        TurningDeadzone = *td;
    }
    if (auto tg = configDocument["TurningGoal"sv].get_double(); tg.has_value())
    {
        TurningGoal = *tg;
    }
    if (auto ad = configDocument["ActiveDelay"sv].get_double(); ad.has_value())
    {
        ActiveDelay = *ad;
    }
    if (auto id = configDocument["InactiveDelay"sv].get_double(); id.has_value())
    {
        InactiveDelay = *id;
    }
    if (auto logging = configDocument["Logging"sv].get_bool(); logging.has_value())
    {
        Logging = *logging;
    }
    if (auto jm = configDocument["XboxJoystickMovement"sv].get_bool(); jm.has_value())
    {
        XboxJoystickMovement = *jm;
    }
    if (auto uq = configDocument["UseOSCQuery"sv].get_bool(); uq.has_value())
    {
        UseOSCQuery = *uq;
    }
}

void Config::save(const std::filesystem::path& confFile)
{
    simdjson::builder::string_builder builder;
    builder.start_object();
    builder.append_key_value<"IP">(IP);
    builder.append_comma();
    builder.append_key_value<"ListeningPort">(ListeningPort);
    builder.append_comma();
    builder.append_key_value<"SendingPort">(SendingPort);
    builder.append_comma();
    builder.append_key_value<"RunDeadzone">(RunDeadzone);
    builder.append_comma();
    builder.append_key_value<"WalkDeadzone">(WalkDeadzone);
    builder.append_comma();
    builder.append_key_value<"StrengthMultiplier">(StrengthMultiplier);
    builder.end_object();

    std::ofstream{ confFile, std::ios::out | std::ios::trunc } << static_cast<std::string_view>(simdjson::fractured_json_string(builder));
}

constexpr std::string app(const std::string& l, std::string_view r)
{
    return std::string(l.length() + r.length(), '\0').replace(0, l.size(), l).replace(l.length(), r.size(), r);
}

void formatDebugFloat(char output[], std::string_view parameter, float v)
{
    memcpy(output, parameter.data(), parameter.size());
    output += parameter.size();
    *output++ = ':';
    *output++ = ' ';
    *output++ = 'f';
    *output++ = '[';
    *output++ = '0' + (int(v) % 10);
    *output++ = '.';
    *output++ = '0' + (int(v * 10) % 10);
    *output++ = '0' + (int(v * 100) % 10);
    *output++ = ']';
    *output++ = '\0';
}

namespace RAII
{
    class Socket
    {
        SOCKET socket = INVALID_SOCKET;
    public:
        Socket() = default;
        Socket(SOCKET socket) : socket(socket)
        {}
        ~Socket()
        {
            if (socket != INVALID_SOCKET)
            {
                if (closesocket(socket) == SOCKET_ERROR)
                {
                    OutputDebugStringA(std::format("closesocket failed with error {}\n", WSAGetLastError()).c_str());
                }
            }
        }
        int bind(const std::string& ip, unsigned short port)
        {
            sockaddr_in addr;
            addr.sin_family = AF_INET;
            addr.sin_port = htons(port);
            int iResult = inet_pton(AF_INET, ip.c_str(), &addr.sin_addr.s_addr);
            if (iResult < 1)
            {
                OutputDebugStringA(std::format("Failed to convert IP address to s_addr with error {}\n", WSAGetLastError()).c_str());
                return 1;
            }
            
            iResult = ::bind(socket, (SOCKADDR*)&addr, sizeof(addr));
            if (iResult == SOCKET_ERROR) {
                OutputDebugStringA(std::format("Bind failed with error {}\n", WSAGetLastError()).c_str());
            }
            return iResult;
        }
        int connect(const std::string& ip, unsigned short port)
        {
            sockaddr_in addr;
            addr.sin_family = AF_INET;
            addr.sin_port = htons(port);
            int iResult = inet_pton(AF_INET, ip.c_str(), &addr.sin_addr.s_addr);
            if (iResult < 1)
            {
                OutputDebugStringA(std::format("Failed to convert IP address to s_addr with error {}\n", WSAGetLastError()).c_str());
                return 1;
            }
            iResult = ::connect(socket, (SOCKADDR*)&addr, sizeof(addr));
            if (iResult == SOCKET_ERROR) {
                OutputDebugStringA(std::format("Connect failed with error {}\n", WSAGetLastError()).c_str());
            }
            return iResult;
        }
        operator SOCKET() const noexcept
        {
            return socket;
        }
    };
}

AvatarParameter::argument& getParameterValue(std::string_view parameter, std::vector<AvatarParameter>& parameterSet)
{
    for (int i = 0; i < parameterSet.size(); ++i)
    {
        if (parameterSet[i].name == parameter)
        {
            return parameterSet[i].data;
        }
    }
    throw std::runtime_error("Parameter not found!");
}

template<class... Ts>
struct overloaded : Ts... { using Ts::operator()...; };

static std::string composeMessage(const AvatarParameter& param)
{
    static constexpr std::string_view prefix = "/input/"sv;
    auto messageLength = prefix.length() + param.name.length() + 4;
    if (!std::holds_alternative<bool>(param.data))
    {
        messageLength += 4;
    }
    std::string msg;
    msg.reserve(messageLength);
    msg += "/input/" + param.name + '\0';
    while (msg.length() & 3)
    {
        msg.push_back('\0');
    }
    msg += ',';
    std::visit(overloaded{ [&](bool b) {
            if (b)
            {
                msg += 'T';
            }
            else
            {
                msg += 'F';
            }
        },
        [&](float f) {
            msg += 'f';
        },
        [&](int i) {
            msg += 'i';
        }
        }, param.data);
    msg += '\0';
    while (msg.length() & 3)
    {
        msg.push_back('\0');
    }

    std::visit(overloaded{ [&](bool b) {},
    [&](float f) {
        int buf = std::byteswap(std::bit_cast<int>(f));
        msg.append(reinterpret_cast<const char*>(&buf), sizeof(buf));
    },
    [&](int i) {
        int buf = std::byteswap(i);
        msg.append(reinterpret_cast<const char*>(&buf), sizeof(buf));
    }
    }, param.data);

    return msg;
}
// NIH but we don't need to pull in the entire glm (ironic since I imported the whole of simdjson, I know)
struct vec2
{
    float x, y;
    vec2& operator*(float m) noexcept
    {
        x *= m;
        y *= m;
        return *this;
    }
    vec2& operator/(float d) noexcept
    {
        x /= d;
        y /= d;
        return *this;
    }
    vec2& operator=(float f) noexcept
    {
        x = f;
        y = f;
        return *this;
    }
    float length() const noexcept
    {
        return std::hypot(x, y);
    }
};

void NetworkWorker::senderFunc(Config config)
{
    RAII::Socket ConnectSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (ConnectSocket == INVALID_SOCKET) {
        OutputDebugStringA(std::format("Failed to create socket with error: {}\n", WSAGetLastError()).c_str());
        return;
    }

    if (ConnectSocket.connect(config.IP, config.SendingPort))
    {
        return;
    }
    OutputDebugStringA("Successfully created a Client Socket\n");

    auto workingCopy = parameterSet;
    float& leashStretch = std::get<float>(getParameterValue(config.physboneParameters[0] + "_Stretch", workingCopy)); // TODO: wtf do you do if there's more than one physbone configured?
    float& Z_Positive = std::get<float>(getParameterValue(config.Z_Positive_Param, workingCopy));
    float& Z_Negative = std::get<float>(getParameterValue(config.Z_Negative_Param, workingCopy));
    float& X_Positive = std::get<float>(getParameterValue(config.X_Positive_Param, workingCopy));
    float& X_Negative = std::get<float>(getParameterValue(config.X_Negative_Param, workingCopy));
    float& Y_Positive = std::get<float>(getParameterValue(config.Y_Positive_Param, workingCopy));
    float& Y_Negative = std::get<float>(getParameterValue(config.Y_Negative_Param, workingCopy));
    std::vector<std::reference_wrapper<bool>> isGrabbed;
    isGrabbed.reserve(config.physboneParameters.size());
    for (auto&& bone : config.physboneParameters)
    {
        isGrabbed.emplace_back(std::ref(std::get<bool>(getParameterValue(bone + "_IsGrabbed", workingCopy))));
    }

    //bool& isGrabbed = std::get<bool>(getParameterValue())

    while (!stopToken.load(std::memory_order_acquire))
    {
        std::unique_lock lk(receiverActiveMtx);
        std::chrono::duration<float> inactiveDelay(config.InactiveDelay);
        activeCV.wait_for(lk, inactiveDelay);
        for (size_t i = 0; i < parameterSet.size(); ++i)
        {
            workingCopy[i].data = parameterSet[i].data;
        }
        lk.unlock();
        
        float outputMultiplier = leashStretch * config.StrengthMultiplier;
        vec2 movementVector = { (Z_Positive - Z_Negative), (X_Positive - X_Negative) };
        movementVector = movementVector / movementVector.length();
        std::string debugMessage = composeMessage(AvatarParameter{ "debug/leash/Horizontal", movementVector.x });
        send(ConnectSocket, debugMessage.data(), debugMessage.size(), 0);
        debugMessage = composeMessage(AvatarParameter{ "debug/leash/Vertical", movementVector.y });
        send(ConnectSocket, debugMessage.data(), debugMessage.size(), 0);
        movementVector = movementVector * outputMultiplier;
        float Y_Combined = Y_Positive + Y_Negative;
        debugMessage = composeMessage(AvatarParameter{ "debug/leash/Lift", Y_Combined});
        send(ConnectSocket, debugMessage.data(), debugMessage.size(), 0);
        debugMessage = composeMessage(AvatarParameter{ "debug/leash/Stretch", leashStretch });
        send(ConnectSocket, debugMessage.data(), debugMessage.size(), 0);
        bool anyGrabbed = false;
        for (auto&& grabbed : isGrabbed)
        {
            anyGrabbed |= grabbed;
        }
        if (Y_Combined >= config.UpDownDeadzone
            || (!anyGrabbed && false))
        {
            movementVector = 0;
        }
        std::string message = composeMessage(AvatarParameter{ "Horizontal", movementVector.x });
        send(ConnectSocket, message.data(), message.size(), 0);
        message = composeMessage(AvatarParameter{ "Vertical", movementVector.y });
        send(ConnectSocket, message.data(), message.size(), 0);
        message = composeMessage(AvatarParameter{ "Run", leashStretch > config.RunDeadzone && !anyGrabbed });
        send(ConnectSocket, message.data(), message.size(), 0);
        //TODO
    }
}

void NetworkWorker::receiverFunc(Config config)
{
    RAII::Socket ListenSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (ListenSocket == INVALID_SOCKET)
    {
        OutputDebugStringA(std::format("Failed to create socket with error: {}\n", WSAGetLastError()).c_str());
        return;
    }

    DWORD timeout = config.InactiveDelay * 100;
    setsockopt(ListenSocket, SOL_SOCKET, SO_RCVTIMEO, (const char*) & timeout, sizeof(DWORD));
    if (ListenSocket.bind(config.IP, config.ListeningPort))
    {
        return;
    }

    OutputDebugStringA("Successfully created a Listen Socket\n");

    if (!PostMessageA(windowHandle, WM_USER, 1, 0))
    {
        OutputDebugStringA("Failed to send message to GUI thread\n");
    }

    auto tryParse = [this](char argType, AvatarParameter& param, char* msg, int parameterIndex) -> std::optional<AvatarParameter::argument> {
        switch (argType)
        {
        case 'T':
        {
            if (!std::holds_alternative<bool>(param.data))
            {
                OutputDebugStringA(std::format("Parameter {} type mismatch (True value), dropping message\n", param.name).c_str());
                return std::nullopt;
            }
            if (debug.load(std::memory_order_acquire))
            {
                SendMessageTimeoutA(debugOutput[parameterIndex], WM_SETTEXT, NULL, reinterpret_cast<long long>(std::format("{}: b[{}]\n", param.name, true).c_str()), SMTO_ABORTIFHUNG, 20, nullptr);
            }
            return static_cast<AvatarParameter::argument>(true);
        }
        case 'F':
        {
            if (!std::holds_alternative<bool>(param.data))
            {

                OutputDebugStringA(std::format("Parameter {} type mismatch (False value), dropping message\n", param.name).c_str());
                return std::nullopt;
            }
            if (debug.load(std::memory_order_acquire))
            {
                SendMessageTimeoutA(debugOutput[parameterIndex], WM_SETTEXT, NULL, reinterpret_cast<long long>(std::format("{}: b[{}]\n", param.name, false).c_str()), SMTO_ABORTIFHUNG, 20, nullptr);
            }
            return static_cast<AvatarParameter::argument>(false);
        }
        case 'f':
        {
            if (!std::holds_alternative<float>(param.data))
            {
                OutputDebugStringA(std::format("Parameter {} type mismatch (float), dropping message\n", param.name).c_str());
                return std::nullopt;
            }
            int buf;
            memcpy(&buf, msg, sizeof(int));
            buf = std::byteswap(buf);
            if (debug.load(std::memory_order_acquire))
            {
                char text[128];
                formatDebugFloat(text, param.name, std::bit_cast<float>(buf));
                SendMessageTimeoutA(debugOutput[parameterIndex], WM_SETTEXT, NULL, reinterpret_cast<long long>(text), SMTO_ABORTIFHUNG, 20, nullptr);
            }
            return static_cast<AvatarParameter::argument>(std::bit_cast<float>(buf));
        }
        case 'i':
        {
            if (!std::holds_alternative<int>(param.data))
            {
                OutputDebugStringA(std::format("Parameter {} type mismatch (int), dropping message\n", param.name).c_str());
                return std::nullopt;
            }
            int buf;
            memcpy(&buf, msg, sizeof(int));
            buf = std::byteswap(buf);
            if (debug.load(std::memory_order_acquire))
            {
                SendMessageTimeoutA(debugOutput[parameterIndex], WM_SETTEXT, NULL, reinterpret_cast<long long>(std::format("{}: i[{}]\n", param.name, buf).c_str()), SMTO_ABORTIFHUNG, 20, nullptr);
            }
            return static_cast<AvatarParameter::argument>(buf);
        }
        }
        return std::nullopt;
    };

    while (!stopToken.load(std::memory_order_acquire))
    {
        alignas(4) char msgBuff[1024];
        sockaddr_in SenderAddr;
        int SenderAddrSize = sizeof(SenderAddr);
        int msgLen = recvfrom(ListenSocket, msgBuff, 1024, 0, (SOCKADDR*) & SenderAddr, &SenderAddrSize);
        if (msgLen<=0)
        {
            continue;
        }
        std::string_view path = msgBuff;
        auto offset = (path.size() + 4) & ~3ull;

        std::string_view parameterName = path;
        auto parametersPrefix = std::string_view("/avatar/parameters/");
        if (!parameterName.starts_with(parametersPrefix))
        {
            continue;
        }
        parameterName.remove_prefix(parametersPrefix.size());
        int parameterIndex = 0;
        for (; parameterIndex < parameterSet.size(); ++parameterIndex)
        {
            if (parameterSet[parameterIndex].name == parameterName)
            {
                break;
            }
        }
        if (parameterIndex >= parameterSet.size())
        {
            continue;
        }
        auto& parameter = parameterSet[parameterIndex];
        std::string_view argList = msgBuff + offset;
        offset += (argList.size() + 4) & ~3ull;
        if (argList.size() < 2 || argList[0] != ',')
        {
            OutputDebugStringA(std::format("arglist malformed ({}), dropping message\n", argList).c_str());
            continue;
        }
        if (auto value = tryParse(argList[1], parameter, msgBuff + offset, parameterIndex))
        {
            std::unique_lock<std::mutex> lk(receiverActiveMtx);
            parameter.data = *value;
            auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(static_cast<long long>(config.ActiveDelay * 1000));
            while (true)
            {
                auto now = std::chrono::steady_clock::now();
                if (now > deadline)
                {
                    break;
                }

                WSAPOLLFD pollfd{};
                pollfd.fd = ListenSocket;
                pollfd.events |= POLLRDNORM;
                int pollResult = WSAPoll(&pollfd, 1, std::chrono::duration_cast<std::chrono::milliseconds>(deadline - now).count());
                if (pollResult < 1)
                {
                    continue;
                }
                if (!(pollfd.revents & POLLRDNORM))
                {
                    continue;
                }
                now = std::chrono::steady_clock::now();
                int msgLen = recvfrom(ListenSocket, msgBuff, 1024, 0, (SOCKADDR*)&SenderAddr, &SenderAddrSize);
                if (msgLen <= 0)
                {
                    continue;
                }
                std::string_view path = msgBuff;
                auto offset = (path.size() + 4) & ~3ull;

                std::string_view parameterName = path;
                auto parametersPrefix = std::string_view("/avatar/parameters/");
                if (!parameterName.starts_with(parametersPrefix))
                {
                    continue;
                }
                parameterName.remove_prefix(parametersPrefix.size());
                int parameterIndex = 0;
                for (; parameterIndex < parameterSet.size(); ++parameterIndex)
                {
                    if (parameterSet[parameterIndex].name == parameterName)
                    {
                        break;
                    }
                }
                if (parameterIndex >= parameterSet.size())
                {
                    continue;
                }
                auto& parameter = parameterSet[parameterIndex];
                std::string_view argList = msgBuff + offset;
                offset += (argList.size() + 4) & ~3ull;
                if (argList.size() < 2 || argList[0] != ',')
                {
                    OutputDebugStringA(std::format("arglist malformed ({}), dropping message\n", argList).c_str());
                    continue;
                }
                if (auto value = tryParse(argList[1], parameter, msgBuff + offset, parameterIndex))
                {
                    parameter.data = *value;
                }
            }
            lk.unlock();
            activeCV.notify_one();
        }
    }

    PostMessageA(windowHandle, WM_USER, 0, 0);
}

void NetworkWorker::run(Config config)
{
    stop();
    stopToken.store(false, std::memory_order_release);
    parameterSet =
    {
        {config.X_Negative_Param, float{}},
        {config.X_Positive_Param, float{}},
        {config.Y_Negative_Param, float{}},
        {config.Y_Positive_Param, float{}},
        {config.Z_Negative_Param, float{}},
        {config.Z_Positive_Param, float{}},
    };
    std::string_view stretchSuffix = "_Stretch", grabbedSuffix = "_IsGrabbed", angleSuffix = "_Angle";
    for (const std::string& leash : config.physboneParameters)
    {
        parameterSet.emplace_back(app(leash, stretchSuffix), float{});
        parameterSet.emplace_back(app(leash, grabbedSuffix), bool{});
        parameterSet.emplace_back(app(leash, angleSuffix), float{});
    }
    receiverWorker = std::thread(&NetworkWorker::receiverFunc, this, config);
    senderWorker = std::thread(&NetworkWorker::senderFunc, this, config);
}

void NetworkWorker::stop()
{
    stopToken.store(true, std::memory_order_release);
    activeCV.notify_all();
    if (receiverWorker.joinable())
    {
        receiverWorker.join();
    }
    if (senderWorker.joinable())
    {
        senderWorker.join();
    }
}
