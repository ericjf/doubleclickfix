"""doubleclickfix: ignora o "duplo clique fantasma" de mouse com switch gasto.

Como funciona: instala um hook de mouse de baixo nível no Windows (WH_MOUSE_LL).
Se um botão for pressionado de novo em menos de THRESHOLD_MS depois de ter sido solto,
esse clique é descartado. Um duplo clique humano leva 100 ms ou mais entre os cliques;
o "bounce" de um switch gasto fica abaixo de 40 ms.

Uso:  pythonw doubleclickfix.py [limite_em_ms]   (padrão 60)
Log:  doubleclickfix.log ao lado do script (só a contagem de cliques descartados).
Sem dependências além do Python padrão. Só Windows.
"""
import ctypes, ctypes.wintypes as w, os, sys, time

THRESHOLD_MS = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
BUTTONS = {0x0201: ('L', 'down'), 0x0202: ('L', 'up'), 0x0204: ('R', 'down'), 0x0205: ('R', 'up')}
LLMHF_INJECTED = 0x01
WH_MOUSE_LL = 14
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doubleclickfix.log')

user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [('pt', w.POINT), ('mouseData', w.DWORD), ('flags', w.DWORD), ('time', w.DWORD),
                ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong))]


LowLevelMouseProc = ctypes.CFUNCTYPE(ctypes.c_long, ctypes.c_int, w.WPARAM, w.LPARAM)
user32.SetWindowsHookExW.restype = w.HHOOK
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, LowLevelMouseProc, w.HINSTANCE, w.DWORD]
user32.CallNextHookEx.restype = ctypes.c_long
user32.CallNextHookEx.argtypes = [w.HHOOK, ctypes.c_int, w.WPARAM, w.LPARAM]
kernel32.GetModuleHandleW.restype = w.HMODULE
kernel32.GetModuleHandleW.argtypes = [w.LPCWSTR]

last_up = {'L': 0.0, 'R': 0.0}
suppress_until_up = {'L': False, 'R': False}
dropped = {'L': 0, 'R': 0}


def log(msg):
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + msg + '\n')
    except OSError:
        pass


@LowLevelMouseProc
def hook(nCode, wParam, lParam):
    if nCode >= 0 and wParam in BUTTONS:
        info = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        if not (info.flags & LLMHF_INJECTED):  # cliques gerados por software passam direto
            btn, kind = BUTTONS[wParam]
            now = time.perf_counter() * 1000
            if kind == 'down':
                if now - last_up[btn] < THRESHOLD_MS:
                    suppress_until_up[btn] = True
                    dropped[btn] += 1
                    if dropped[btn] % 10 == 1:
                        log(f'clique fantasma descartado no botao {btn} (total {btn}={dropped[btn]})')
                    return 1  # engole o DOWN
            else:
                if suppress_until_up[btn]:
                    suppress_until_up[btn] = False
                    return 1  # engole o UP correspondente
                last_up[btn] = now
    return user32.CallNextHookEx(None, nCode, wParam, lParam)


def main():
    kernel32.CreateMutexW(None, True, 'Local\\doubleclickfix')  # instancia unica
    if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        sys.exit(0)
    h = user32.SetWindowsHookExW(WH_MOUSE_LL, hook, kernel32.GetModuleHandleW(None), 0)
    if not h:
        log(f'falha ao instalar o hook: erro {ctypes.get_last_error()}')
        sys.exit(1)
    log(f'iniciado, limite {THRESHOLD_MS:g} ms')
    msg = w.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
    user32.UnhookWindowsHookEx(h)


if __name__ == '__main__':
    main()
