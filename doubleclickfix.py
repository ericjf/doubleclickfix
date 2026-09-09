"""doubleclickfix: ignora o "duplo clique fantasma" de mouse com switch gasto.

Como funciona: instala um hook de mouse de baixo nível no Windows (WH_MOUSE_LL).
Se um botão for pressionado de novo em menos de N ms depois de ter sido solto,
esse clique é descartado. Um duplo clique humano leva 100 ms ou mais entre os cliques;
o "bounce" de um switch gasto fica abaixo de 40 ms.

Abre uma janelinha com o estado (ATIVO / DESLIGADO), botão de ligar/desligar,
contador de cliques descartados e o limite em ms. Desligado = hook removido, nada interceptando.

Também descarta clique do BOTÃO DO MEIO que chegue até WHEEL_GUARD_MS depois de um giro da
rodinha (rodinha suja ou desalinhada que "clica" sozinha ao rolar).

Uso:  pythonw doubleclickfix.py [limite_em_ms] [--desligado]
Log:  doubleclickfix.log ao lado do script (só a contagem de cliques descartados).
Sem dependências além do Python padrão. Só Windows.
"""
import ctypes, ctypes.wintypes as w, os, sys, time
import tkinter as tk

args = [a for a in sys.argv[1:] if not a.startswith('--')]
THRESHOLD_MS = float(args[0]) if args else 60.0
START_OFF = '--desligado' in sys.argv
BUTTONS = {0x0201: ('L', 'down'), 0x0202: ('L', 'up'), 0x0204: ('R', 'down'), 0x0205: ('R', 'up'), 0x0207: ('M', 'down'), 0x0208: ('M', 'up')}
WM_MOUSEWHEEL = 0x020A
WHEEL_GUARD_MS = 250.0  # clique do meio ate este tempo depois de rolar a rodinha e descartado
LLMHF_INJECTED = 0x01
WH_MOUSE_LL = 14
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doubleclickfix.log')

user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [('pt', w.POINT), ('mouseData', w.DWORD), ('flags', w.DWORD), ('time', w.DWORD),
                ('dwExtraInfo', ctypes.c_size_t)]  # ULONG_PTR


LowLevelMouseProc = ctypes.CFUNCTYPE(ctypes.c_long, ctypes.c_int, w.WPARAM, w.LPARAM)
user32.SetWindowsHookExW.restype = w.HHOOK
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, LowLevelMouseProc, w.HINSTANCE, w.DWORD]
user32.UnhookWindowsHookEx.argtypes = [w.HHOOK]
user32.CallNextHookEx.restype = ctypes.c_long
user32.CallNextHookEx.argtypes = [w.HHOOK, ctypes.c_int, w.WPARAM, w.LPARAM]
kernel32.GetModuleHandleW.restype = w.HMODULE
kernel32.GetModuleHandleW.argtypes = [w.LPCWSTR]

last_up = {'L': 0.0, 'R': 0.0, 'M': 0.0}
suppress_until_up = {'L': False, 'R': False, 'M': False}
dropped = {'L': 0, 'R': 0, 'M': 0}
last_wheel = 0.0
hook_handle = None


def log(msg):
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + msg + '\n')
    except OSError:
        pass


@LowLevelMouseProc
def hook(nCode, wParam, lParam):
    global last_wheel
    if nCode >= 0 and wParam == WM_MOUSEWHEEL:
        last_wheel = time.perf_counter() * 1000
    elif nCode >= 0 and wParam in BUTTONS:
        info = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        if not (info.flags & LLMHF_INJECTED):  # cliques gerados por software passam direto
            btn, kind = BUTTONS[wParam]
            now = time.perf_counter() * 1000
            if kind == 'down':
                if now - last_up[btn] < THRESHOLD_MS or (btn == 'M' and now - last_wheel < WHEEL_GUARD_MS):
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


def enable():
    global hook_handle
    if hook_handle:
        return True
    hook_handle = user32.SetWindowsHookExW(WH_MOUSE_LL, hook, kernel32.GetModuleHandleW(None), 0)
    if not hook_handle:
        log(f'falha ao instalar o hook: erro {ctypes.get_last_error()}')
        return False
    log(f'ativo, limite {THRESHOLD_MS:g} ms')
    return True


def disable():
    global hook_handle
    if hook_handle:
        user32.UnhookWindowsHookEx(hook_handle)
        hook_handle = None
        for k in suppress_until_up: suppress_until_up[k] = False
        log('desligado')


class Janela:
    ON, OFF = '#2e7d32', '#b71c1c'

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('doubleclickfix')
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.root.protocol('WM_DELETE_WINDOW', self.fechar)
        f = tk.Frame(self.root, padx=14, pady=10)
        f.pack()
        self.status = tk.Label(f, text='', font=('Segoe UI', 16, 'bold'), fg='white', width=12, pady=6)
        self.status.grid(row=0, column=0, columnspan=2, sticky='ew')
        self.botao = tk.Button(f, text='', width=14, font=('Segoe UI', 10), command=self.alternar)
        self.botao.grid(row=1, column=0, columnspan=2, pady=(8, 6))
        self.contador = tk.Label(f, text='', font=('Segoe UI', 9), fg='#555')
        self.contador.grid(row=2, column=0, columnspan=2)
        tk.Label(f, text='limite (ms):', font=('Segoe UI', 9)).grid(row=3, column=0, sticky='e', pady=(6, 0))
        self.limite = tk.Spinbox(f, from_=20, to=200, increment=10, width=5, command=self.mudar_limite)
        self.limite.delete(0, 'end'); self.limite.insert(0, f'{THRESHOLD_MS:g}')
        self.limite.bind('<Return>', lambda e: self.mudar_limite())
        self.limite.grid(row=3, column=1, sticky='w', pady=(6, 0))
        self.topo = tk.BooleanVar(value=True)
        tk.Checkbutton(f, text='sempre visível', variable=self.topo, font=('Segoe UI', 8),
                       command=lambda: self.root.attributes('-topmost', self.topo.get())).grid(row=4, column=0, columnspan=2, pady=(4, 0))
        self.atualizar()
        self.tick()

    def alternar(self):
        if hook_handle:
            disable()
        else:
            enable()
        self.atualizar()

    def mudar_limite(self):
        global THRESHOLD_MS
        try:
            THRESHOLD_MS = float(self.limite.get())
        except ValueError:
            pass

    def atualizar(self):
        on = bool(hook_handle)
        self.status.config(text='ATIVO' if on else 'DESLIGADO', bg=self.ON if on else self.OFF)
        self.botao.config(text='Desligar' if on else 'Ligar')

    def tick(self):
        self.contador.config(text=f"descartados: esq {dropped['L']} · dir {dropped['R']} · meio/rodinha {dropped['M']}")
        self.root.after(500, self.tick)

    def fechar(self):
        disable()
        self.root.destroy()


def main():
    kernel32.CreateMutexW(None, True, 'Local\\doubleclickfix')  # instância única
    if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        ctypes.windll.user32.MessageBoxW(None, 'O doubleclickfix já está aberto (procure a janelinha dele).', 'doubleclickfix', 0x40)
        sys.exit(0)
    if not START_OFF:
        enable()
    Janela().root.mainloop()  # o mainloop do tkinter bombeia as mensagens que o hook precisa


if __name__ == '__main__':
    main()
