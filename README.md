# doubleclickfix

Seu mouse dá **duplo clique sozinho** quando você clica uma vez? Arrasta um arquivo e ele solta no meio do caminho? Isso é o switch do botão gasto (a molinha de metal dentro dele perdeu a tensão e "quica"). Este programinha resolve por software: ele ignora o segundo clique quando ele chega rápido demais pra ter sido um humano.

- Sem instalar nada além do Python (que a maioria já tem). 90 linhas, dá pra ler tudo.
- Funciona no botão esquerdo e no direito.
- **Rodinha que "clica" sozinha ao rolar** (suja, ou desalinhada depois de um acidente): clique do meio que chega até 250 ms depois de um giro da rodinha é descartado. Clique do meio normal, com a rodinha parada, passa.
- Se o software do seu mouse tem ajuste de **debounce** (Glorious Core, Razer Synapse, Pulsar, Endgame Gear), use ele primeiro. Isso aqui é pra quem não tem, como Logitech G HUB ou mouse genérico. A opção "velocidade do clique duplo" do Windows não resolve: ela só muda como o Windows interpreta dois cliques, o clique fantasma continua chegando.
- Duplo clique de verdade continua funcionando (limite padrão de 60 ms; uma pessoa leva 100 ms ou mais entre dois cliques).
- Abre uma janelinha com o estado (**ATIVO** em verde, **DESLIGADO** em vermelho), botão de ligar/desligar, contador de cliques descartados, **caixinhas pra escolher o que filtrar** (só o esquerdo, só o direito, só a rodinha, ou qualquer combinação) e os dois limites em ms (duplo clique e rodinha). As escolhas ficam salvas e voltam quando o programa reabre. Desligado = o hook é removido de verdade, nada fica interceptando o mouse.
- Gasta nada e sobe sozinho com o Windows.
- Só Windows.

## Jogos e anticheat

Valorant e LoL leem o mouse por Raw Input, então o programa **não age dentro deles** de qualquer jeito. O Vanguard bloqueia automação de input; isso aqui não injeta clique nenhum, só descarta, mas a Riot não publica o que considera suspeito. Pra não arriscar, clique em **Desligar** antes de abrir jogo com anticheat (Vanguard, BattlEye, EAC) e em **Ligar** depois. Desligado, o hook não existe.

## Instalar (jeito fácil: .exe, sem Python)

1. Baixe o **`doubleclickfix.exe`** na página de [Releases](https://github.com/ericjf/doubleclickfix/releases/latest).
2. Coloque numa pasta que você não vá apagar nem mover (ex.: `C:\doubleclickfix`) e dê dois cliques.
3. Na janelinha, marque **"abrir junto com o Windows"** se quiser que ele suba sozinho no login.

O Windows pode mostrar o aviso azul do SmartScreen ("Windows protegeu o computador") porque o .exe não tem assinatura digital paga. Clique em **"Mais informações" > "Executar assim mesmo"**. O código é este aqui do repositório, empacotado com PyInstaller; se preferir não confiar num .exe, use o jeito com Python abaixo.

## Instalar (jeito com Python)

1. Tenha o Python 3 instalado: https://www.python.org/downloads/ (marque **"Add python.exe to PATH"** na instalação).
2. Baixe este repositório (botão verde **Code > Download ZIP**) e extraia numa pasta que você não vá apagar nem mover (ex.: `C:\doubleclickfix`). O atalho de inicialização aponta pra esse caminho; se mover a pasta, rode o `instalar.cmd` de novo.
3. Dê dois cliques em **`instalar.cmd`**.

Pronto. Ele já está rodando e vai abrir sozinho a cada login.

## Testar

Clique várias vezes com o botão que estava ruim. Se ainda escapar algum duplo clique, abra o `doubleclickfix.log` na pasta: cada linha "clique fantasma descartado" é um clique que ele segurou. Se quiser um limite maior (mais agressivo), mude o "duplo clique (ms)" na janelinha (90, por exemplo). Se um duplo clique legítimo parar de funcionar, diminua (40). Mouse que só tem problema na rodinha: desmarca esquerdo e direito e deixa só a rodinha marcada.

Pasta de inicialização: `Win + R`, digite `shell:startup`, Enter.

## Remover

Dois cliques em **`desinstalar.cmd`**. Ou apague o `doubleclickfix.cmd` da pasta de inicialização e encerre o `pythonw.exe` no Gerenciador de Tarefas.

## Como funciona

Um hook de mouse de baixo nível do Windows (`WH_MOUSE_LL`, via `ctypes`, sem bibliotecas externas). Quando um botão é pressionado menos de N milissegundos depois de ter sido solto, o programa devolve 1 para o Windows e o clique some antes de chegar em qualquer aplicativo. Cliques gerados por software (automação, acessibilidade) passam direto.

Não conserta o mouse: a solução definitiva é trocar o switch (peça de R$ 5 a 20, exige solda) ou dobrar a lâmina de cobre de dentro dele. Isso aqui é pra continuar usando enquanto isso.

## English

Ignores phantom double clicks from worn-out mouse switches on Windows. A low-level mouse hook drops any button press that arrives less than 60 ms (configurable) after the previous release. Pure Python, no dependencies. Run `instalar.cmd` to install to your user's Startup folder, `desinstalar.cmd` to remove.

MIT.
