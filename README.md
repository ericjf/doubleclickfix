# doubleclickfix

Seu mouse dá **duplo clique sozinho** quando você clica uma vez? Arrasta um arquivo e ele solta no meio do caminho? Isso é o switch do botão gasto (a molinha de metal dentro dele perdeu a tensão e "quica"). Este programinha resolve por software: ele ignora o segundo clique quando ele chega rápido demais pra ter sido um humano.

- Sem instalar nada além do Python (que a maioria já tem). 90 linhas, dá pra ler tudo.
- Funciona no botão esquerdo e no direito.
- Duplo clique de verdade continua funcionando (limite padrão de 60 ms; uma pessoa leva 100 ms ou mais entre dois cliques).
- Roda escondido, gasta nada, e sobe sozinho com o Windows.
- Só Windows.

## Instalar

1. Tenha o Python 3 instalado: https://www.python.org/downloads/ (marque **"Add python.exe to PATH"** na instalação).
2. Baixe este repositório (botão verde **Code > Download ZIP**) e extraia numa pasta que você não vá apagar (ex.: `C:\doubleclickfix`).
3. Dê dois cliques em **`instalar.cmd`**.

Pronto. Ele já está rodando e vai abrir sozinho a cada login.

## Testar

Clique várias vezes com o botão que estava ruim. Se ainda escapar algum duplo clique, abra o `doubleclickfix.log` na pasta: cada linha "clique fantasma descartado" é um clique que ele segurou. Se quiser um limite maior (mais agressivo), edite o `doubleclickfix.cmd` que ficou na pasta de inicialização e acrescente o número no fim, por exemplo `... doubleclickfix.py" 90` para 90 ms. Se um duplo clique legítimo parar de funcionar, diminua (40).

Pasta de inicialização: `Win + R`, digite `shell:startup`, Enter.

## Remover

Dois cliques em **`desinstalar.cmd`**. Ou apague o `doubleclickfix.cmd` da pasta de inicialização e encerre o `pythonw.exe` no Gerenciador de Tarefas.

## Como funciona

Um hook de mouse de baixo nível do Windows (`WH_MOUSE_LL`, via `ctypes`, sem bibliotecas externas). Quando um botão é pressionado menos de N milissegundos depois de ter sido solto, o programa devolve 1 para o Windows e o clique some antes de chegar em qualquer aplicativo. Cliques gerados por software (automação, acessibilidade) passam direto.

Não conserta o mouse: a solução definitiva é trocar o switch (peça de R$ 5 a 20, exige solda) ou dobrar a lâmina de cobre de dentro dele. Isso aqui é pra continuar usando enquanto isso.

## English

Ignores phantom double clicks from worn-out mouse switches on Windows. A low-level mouse hook drops any button press that arrives less than 60 ms (configurable) after the previous release. Pure Python, no dependencies. Run `instalar.cmd` to install to your user's Startup folder, `desinstalar.cmd` to remove.

MIT.
