#include "framework.h"
#include "oscleash.h"
#include "handles.hpp"
#include "NetworkWorker.h"
#include <WinSock2.h>

#define MAX_LOADSTRING 100

// Zmienne globalne:
HINSTANCE hInst;                                // bieżące wystąpienie
WCHAR szTitle[MAX_LOADSTRING];                  // Tekst paska tytułu
WCHAR szWindowClass[MAX_LOADSTRING];            // nazwa klasy okna głównego

// Przekaż dalej deklaracje funkcji dołączone w tym module kodu:
ATOM                MyRegisterClass(HINSTANCE hInstance);
BOOL                InitInstance(HINSTANCE, int, const Config&);
LRESULT CALLBACK    WndProc(HWND, UINT, WPARAM, LPARAM);
INT_PTR CALLBACK    About(HWND, UINT, WPARAM, LPARAM);

Config config;
NetworkWorker worker;
HWND hWnd;

int APIENTRY wWinMain(_In_ HINSTANCE hInstance,
                     _In_opt_ HINSTANCE hPrevInstance,
                     _In_ LPWSTR    lpCmdLine,
                     _In_ int       nCmdShow)
{
    UNREFERENCED_PARAMETER(hPrevInstance);
    UNREFERENCED_PARAMETER(lpCmdLine);
    config.load("config.json");

    LoadStringW(hInstance, IDS_APP_TITLE, szTitle, MAX_LOADSTRING);
    LoadStringW(hInstance, IDC_OSCLEASH, szWindowClass, MAX_LOADSTRING);
    MyRegisterClass(hInstance);

    if (!InitInstance (hInstance, nCmdShow, config))
    {
        return FALSE;
    }
    WSADATA wsaData;
    int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != NO_ERROR) {
        OutputDebugStringA(std::format("startup failed {}\n", iResult).c_str());
        return 1;
    }
    worker.windowHandle = hWnd;
    worker.run(config);

    HACCEL hAccelTable = LoadAccelerators(hInstance, MAKEINTRESOURCE(IDC_OSCLEASH));

    MSG msg;
    PeekMessageA(&msg, nullptr, WM_USER, WM_USER, PM_NOREMOVE);

    // Główna pętla komunikatów:
    while (GetMessage(&msg, nullptr, 0, 0))
    {
        if (!TranslateAccelerator(msg.hwnd, hAccelTable, &msg))
        {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }

    worker.stop();
    WSACleanup();
    config.save("config.json");

    return (int) msg.wParam;
}



//
//  FUNKCJA: MyRegisterClass()
//
//  PRZEZNACZENIE: Rejestruje klasę okna.
//
ATOM MyRegisterClass(HINSTANCE hInstance)
{
    WNDCLASSEXW wcex;

    wcex.cbSize = sizeof(WNDCLASSEX);

    wcex.style          = CS_HREDRAW | CS_VREDRAW;
    wcex.lpfnWndProc    = WndProc;
    wcex.cbClsExtra     = 0;
    wcex.cbWndExtra     = 0;
    wcex.hInstance      = hInstance;
    wcex.hIcon          = LoadIcon(hInstance, MAKEINTRESOURCE(IDI_OSCLEASH));
    wcex.hCursor        = LoadCursor(nullptr, IDC_ARROW);
    wcex.hbrBackground  = (HBRUSH)(COLOR_WINDOW+1);
    wcex.lpszMenuName   = MAKEINTRESOURCEW(IDC_OSCLEASH);
    wcex.lpszClassName  = szWindowClass;
    wcex.hIconSm        = LoadIcon(wcex.hInstance, MAKEINTRESOURCE(IDI_SMALL));

    return RegisterClassExW(&wcex);
}

//
//   FUNKCJA: InitInstance(HINSTANCE, int)
//
//   PRZEZNACZENIE: Zapisuje dojście wystąpienia i tworzy okno główne
//
//   KOMENTARZE:
//
//        W tej funkcji dojście wystąpienia jest zapisywane w zmiennej globalnej i
//        jest tworzone i wyświetlane okno główne programu.
//
#include <CommCtrl.h>
#include <WS2tcpip.h>

BOOL InitInstance(HINSTANCE hInstance, int nCmdShow, const Config& conf)
{
    INITCOMMONCONTROLSEX commonControls;
    commonControls.dwICC |= ICC_INTERNET_CLASSES;
    hInst = hInstance; // Przechowuj dojście wystąpienia w naszej zmiennej globalnej

    hWnd = CreateWindowW(szWindowClass, szTitle, WS_SYSMENU | WS_MINIMIZEBOX,
        CW_USEDEFAULT, 0, 640, 480, nullptr, nullptr, hInstance, nullptr);

    if (!hWnd)
    {
        return FALSE;
    }

    unsigned long addr;
    inet_pton(AF_INET, config.IP.c_str(), &addr);

    startButton = CreateWindowW(L"BUTTON", L"RESTART", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON, 0, 0, 100, 25, hWnd, nullptr, hInst, nullptr);
    HWND tip = CreateWindowA(TOOLTIPS_CLASSA, nullptr, WS_POPUP | TTS_ALWAYSTIP | TTS_NOPREFIX, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, hWnd, nullptr, hInst, nullptr);
    TOOLINFO toolInfo{};
    toolInfo.cbSize = sizeof(toolInfo);
    toolInfo.hwnd = startButton;
    toolInfo.uFlags = TTF_IDISHWND | TTF_SUBCLASS;
    toolInfo.uId = (UINT_PTR)startButton;
    char str[] = "Fuck\0";
    toolInfo.lpszText = reinterpret_cast<LPWSTR>(str);
    SendMessageA(tip, TTM_ADDTOOLA, 0, (UINT_PTR) & toolInfo);

    int y = 50;
    auto addEdit = [&y](const std::string& label, const std::string& text, long editStyle = 0) {
        HWND hLabel = CreateWindowA("STATIC", label.c_str(), WS_VISIBLE | WS_CHILD, 0, y, 190, 25, hWnd, nullptr, hInst, nullptr);
        HWND hEdit = CreateWindowA("EDIT", text.c_str(), ES_LEFT | WS_BORDER | WS_VISIBLE | WS_CHILD | WS_TABSTOP | editStyle, 190, y, 200, 25, hWnd, nullptr, hInst, nullptr);
        y += 25;
        return hEdit;
    };

    auto addButton = [&y](const std::string& label, long extraButtonStyle = 0) {
        HWND hButton = CreateWindowA("BUTTON", label.c_str(), WS_VISIBLE | WS_CHILD | BS_AUTOCHECKBOX | BS_LEFTTEXT | extraButtonStyle, 0, y, 390, 25, hWnd, nullptr, hInst, nullptr);
        y += 25;
        return hButton;
    };

    serverRunningIndicator = CreateWindowA("BUTTON", "Server running:", WS_VISIBLE | WS_CHILD | WS_DISABLED | BS_CHECKBOX | BS_LEFTTEXT, 100, 0, 150, 25, hWnd, nullptr, hInst, nullptr);
    HWND ipEditLabel = CreateWindowA("STATIC", "IP:", ES_LEFT | WS_VISIBLE | WS_CHILD, 0, 25, 190, 25, hWnd, nullptr, hInst, nullptr);
    ipEdit = CreateWindowA(WC_IPADDRESSA, nullptr, ES_LEFT | WS_BORDER | WS_VISIBLE | WS_CHILD | WS_TABSTOP, 190, 25, 200, 25, hWnd, nullptr, hInst, nullptr);
    SendMessageA(ipEdit, IPM_SETADDRESS, 0, htonl(addr));
    listenPortEdit = addEdit("Listen port:", std::to_string(conf.ListeningPort), ES_NUMBER);
    sendPortEdit = addEdit("Send port:", std::to_string(conf.SendingPort), ES_NUMBER);
    runDeadzoneEdit = addEdit("Run deadzone:", std::to_string(conf.RunDeadzone));
    walkDeadzoneEdit = addEdit("Walk deadzone:", std::to_string(conf.WalkDeadzone));
    strengthMultiplierEdit = addEdit("Strength multiplier:", std::to_string(conf.StrengthMultiplier));
    upDownCompensationEdit = addEdit("Up/down compensation:", std::to_string(conf.UpDownCompensation));
    upDownDeadzoneEdit = addEdit("Up/down deadzone:", std::to_string(conf.UpDownDeadzone));
    turningEnabledCheckbox = addButton("Turning:", BS_CHECKBOX);
    SendMessageA(turningEnabledCheckbox, BM_SETCHECK, config.TurningEnabled, 0);
    turningMultiplierEdit = addEdit("Turning multiplier:", std::to_string(conf.TurningMultiplier));
    EnableWindow(turningMultiplierEdit, config.TurningEnabled);
    turningDeadzoneEdit = addEdit("Turning deadzone:", std::to_string(conf.TurningDeadzone));
    EnableWindow(turningDeadzoneEdit, config.TurningEnabled);
    turningGoalEdit = addEdit("Turning goal:", std::to_string(conf.TurningGoal));
    EnableWindow(turningGoalEdit, config.TurningEnabled);
    activeDelayEdit = addEdit("Active delay:", std::to_string(conf.ActiveDelay));
    inactiveDelayEdit = addEdit("Inactive delay:", std::to_string(conf.InactiveDelay));
    std::string physboneParametersCSV;
    for (auto&& param : conf.physboneParameters)
    {
        physboneParametersCSV.append(param).push_back(',');
    }
    physboneParameterEdit = addEdit("Physbone parameters:", physboneParametersCSV, ES_AUTOHSCROLL);


    debugCheckbox = CreateWindowA("BUTTON", "Debug:", WS_VISIBLE | WS_CHILD | BS_AUTOCHECKBOX | BS_LEFTTEXT, 300, 0, 90, 18, hWnd, nullptr, hInst, nullptr);
    for (int i = 0; i < 9; ++i)
    {
        debugOutput[i] = CreateWindowA("STATIC", "", WS_VISIBLE | WS_CHILD, 390, (i * 18), 250, 18, hWnd, nullptr, hInst, nullptr);
    }

    ShowWindow(hWnd, nCmdShow);
    UpdateWindow(hWnd);

    return TRUE;
}

//
//  FUNKCJA: WndProc(HWND, UINT, WPARAM, LPARAM)
//
//  PRZEZNACZENIE: Przetwarza komunikaty dla okna głównego.
//
//  WM_COMMAND  - przetwarzaj menu aplikacji
//  WM_PAINT    - Maluj okno główne
//  WM_DESTROY  - opublikuj komunikat o wyjściu i wróć
//
//
#include <windowsx.h>

template<typename T>
static void tieScalar(T& configParameter, HWND handle) {
    std::string text;
    text.resize(GetWindowTextLengthA(handle));
    GetWindowTextA(handle, text.data(), text.size() + 1);
    std::from_chars(text.data(), text.data() + text.size(), configParameter);
}

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    struct editTie
    {
        HWND handle;
        void (*callback)(HWND handle, Config& config) = nullptr;
    };

    editTie ties[] = {
        {ipEdit, [](HWND hIp, Config& config) {
            config.IP.resize(GetWindowTextLengthA(ipEdit));
            GetWindowTextA(ipEdit, config.IP.data(), config.IP.size() + 1);
        }},
        {listenPortEdit, [](HWND hlp, Config& config) {
            tieScalar(config.ListeningPort, hlp);
        }},
        {sendPortEdit, [](HWND hsp, Config& config) {
            tieScalar(config.SendingPort, hsp);
        }},
        {runDeadzoneEdit, [](HWND hrd, Config& config) {
            tieScalar(config.RunDeadzone, hrd);
        }},
        {walkDeadzoneEdit, [](HWND hwd, Config& config) {
            tieScalar(config.WalkDeadzone, hwd);
        }},
        {strengthMultiplierEdit, [](HWND hsm, Config& config) {
            tieScalar(config.StrengthMultiplier, hsm);
        }},
        {upDownCompensationEdit, [](HWND hudc, Config& config) {
            tieScalar(config.UpDownCompensation, hudc);
        }},
        {upDownDeadzoneEdit, [](HWND hudd, Config& config) {
            tieScalar(config.UpDownDeadzone, hudd);
        }},
        {turningMultiplierEdit, [](HWND htm, Config& config) {
            tieScalar(config.TurningMultiplier, htm);
        }},
        {turningDeadzoneEdit, [](HWND htd, Config& config) {
            tieScalar(config.TurningDeadzone, htd);
        }},
        {turningGoalEdit, [](HWND htg, Config& config) {
            tieScalar(config.TurningGoal, htg);
        }},
        {activeDelayEdit, [](HWND had, Config& config) {
            tieScalar(config.ActiveDelay, had);
        }},
        {inactiveDelayEdit, [](HWND hid, Config& config) {
            tieScalar(config.InactiveDelay, hid);
        }},
        {physboneParameterEdit, [](HWND hpp, Config& config) {
            config.physboneParameters.clear();
            std::string text;
            text.resize(GetWindowTextLengthA(hpp));
            GetWindowTextA(hpp, text.data(), text.size());
            std::string_view view = text;
            while (!view.empty())
            {
                while (view[0] == ',')
                {
                    view.remove_prefix(1);
                }
                auto sub = view.substr(0, view.find(','));
                view.remove_prefix(sub.size());
                config.physboneParameters.push_back(std::string(sub));
            }
        }}
    };

    switch (message)
    {
    case WM_COMMAND:
    {
        int wmId = HIWORD(wParam);
        // Analizuj zaznaczenia menu:
        switch (wmId)
        {
        case BN_CLICKED:
            if ((HWND)(lParam) == startButton)
            {
                worker.run(config);
            }
            if ((HWND)(lParam) == debugCheckbox)
            {
                worker.setDebug(Button_GetCheck(debugCheckbox));
            }
            if ((HWND)(lParam) == turningEnabledCheckbox)
            {
                bool enabled = Button_GetCheck(turningEnabledCheckbox);
                config.TurningEnabled = enabled;
                EnableWindow(turningMultiplierEdit, enabled);
                EnableWindow(turningDeadzoneEdit, enabled);
                EnableWindow(turningGoalEdit, enabled);
            }
            break;
        case EN_CHANGE:
        {
            bool handled = false;
            for (auto&& [handle, callback] : ties)
            {
                if (handle == (HWND)(lParam))
                {
                    callback(handle, config);
                    handled = true;
                    break;
                }
            }
            if (handled)
            {
                break;
            }
            OutputDebugStringA("Unhandled input event\n");
        }
        break;
        }
    }
        break;
    case WM_PAINT:
        {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hWnd, &ps);
            // TODO: Tutaj dodaj kod rysujący używający elementu hdc...
            EndPaint(hWnd, &ps);
        }
        break;
    case WM_USER:
        {
            SendMessageA(serverRunningIndicator, BM_SETCHECK, wParam, 0);
            return 0;
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    }
    return DefWindowProc(hWnd, message, wParam, lParam);
}

// Procedura obsługi komunikatów dla okna informacji o programie.
INT_PTR CALLBACK About(HWND hDlg, UINT message, WPARAM wParam, LPARAM lParam)
{
    UNREFERENCED_PARAMETER(lParam);
    switch (message)
    {
    case WM_INITDIALOG:
        return (INT_PTR)TRUE;

    case WM_COMMAND:
        if (LOWORD(wParam) == IDOK || LOWORD(wParam) == IDCANCEL)
        {
            EndDialog(hDlg, LOWORD(wParam));
            return (INT_PTR)TRUE;
        }
        break;
    }
    return (INT_PTR)FALSE;
}
