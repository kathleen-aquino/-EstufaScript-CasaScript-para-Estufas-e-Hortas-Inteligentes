# -EstufaScript-CasaScript-para-Estufas-e-Hortas-Inteligentes

Victor Borges Quintella de Almeida - 2544963
Kathleen Aquino Lima - 2364196
João Victor Brandão - 2359197
Lucas Costa - 2361186

# 🌱 EstufaScript — CasaScript para Estufas e Hortas Inteligentes

**Prática 2 — Compiladores** · Notebook: `Pratica2_SmartEstufa.ipynb`

## 1. Cenário escolhido: Estufa / horta inteligente

**Mercado:** Agtech, agricultura de precisão e fazendas verticais.

Produtores de hortaliças em estufas e fazendas verticais ainda controlam boa parte da irrigação, da iluminação complementar e da ventilação de forma manual ou com temporizadores fixos. Isso desperdiça água e energia (irrigar quando está chovendo, deixar a lâmpada de cultivo ligada fora do fotoperíodo) e expõe a cultura a estresse térmico quando ninguém está presente para abrir a janela de teto. A startup quer que o próprio agrônomo escreva as regras da estufa numa linguagem simples, sem programar em Python ou C. A **EstufaScript** adapta a CasaScript para esse público: regras `QUANDO … ENTAO … SENAO … FIM` sobre sensores de solo, luz, clima, reservatório e relógio, compiladas para um bytecode executado por uma central embarcada que reage às mudanças de estado (bordas de subida e de descida).

## 2. Tabela de símbolos

### Sensores (7 sensores, 4 tipos)

| Sensor | Tipo | Faixa / valores | Descrição |
|---|---|---|---|
| `umidade_solo` | número | 0 … 100 % | Umidade volumétrica do solo |
| `luminosidade` | número | 0 … 100000 lux | Iluminância sobre o dossel |
| `temperatura` | número | -10 … 60 °C | Temperatura interna do ar |
| `nivel_reservatorio` | número | 0 … 100 % | Nível da caixa d'água de irrigação |
| `clima` | texto | `"ensolarado"`, `"nublado"`, `"chuvoso"` | Condição do tempo |
| `chovendo` | lógico | `VERDADEIRO` / `FALSO` | Pluviômetro |
| `relogio` | horário | `00:00` … `23:59` (0 … 1439 min) | Hora do dia |

### Dispositivos (5 dispositivos, 4 tipos)

| Dispositivo | Tipo | Descrição |
|---|---|---|
| `irrigador` | irrigador | Válvula de irrigação por gotejamento |
| `lampada` | lampada_cultivo | Lâmpada de cultivo LED full-spectrum |
| `ventilador` | ventilador | Ventilador de circulação |
| `exaustor` | ventilador | Exaustor de ar quente |
| `janela_teto` | janela | Janela zenital motorizada |

### Ações (6 ações, 4 novas)

| Ação | Parâmetros | Tipos de dispositivo aceitos | Faixa do número | Nova? |
|---|---|---|---|---|
| `ligar` | dispositivo | irrigador, lampada_cultivo, ventilador | — | não |
| `desligar` | dispositivo | irrigador, lampada_cultivo, ventilador | — | não |
| `irrigar` | dispositivo, número | irrigador | 1 … 60 min | **sim** |
| `ajustar_luz` | dispositivo, número | lampada_cultivo | 0 … 100 % | **sim** |
| `abrir` | dispositivo, número | janela | 0 … 100 % | **sim** |
| `fechar` | dispositivo | janela | — | **sim** |

## 3. Requisitos e fases do compilador

### RF1 — Literal de horário · **Fase léxica** (Célula 3)
* Novo padrão `HORARIO` (`\d+:\d+`) colocado **antes** de `NUMERO` na lista de tokens, para que `18:30` seja reconhecido como um único token.
* A função `horario_para_minutos` exige o formato `HH:MM`, valida hora `00..23` e minuto `00..59` e converte para minutos desde a meia-noite (`18:30 → 1110`). `25:00`, `18:75` e `7:30` geram `ErroLexico`.
* Novo sensor `relogio` do tipo `horario` na tabela de símbolos. A semântica só permite comparar horário com horário.
* A Célula 4 demonstra o token único e os erros.

### RF2 — Bloco `SENAO` · **Fase sintática** (Células 5, 6 e 7) + geração e runtime
* Gramática: `regra → QUANDO expr ENTAO acoes [SENAO acoes] FIM` e `acoes → acao+`.
* O nó `Regra` ganhou o campo `senao`. O método `bloco()` do parser lança `ErroSintatico` se o bloco estiver vazio (`SENAO FIM` → *"bloco SENAO vazio — esperada ao menos uma ação"*).
* O desenho da AST (SVG e texto) mostra o nó `SENAO` em laranja como terceiro filho da regra; o bytecode tem a coluna `SENAO`.
* As ações do `SENAO` são executadas na **borda de descida** (Célula 11, classe `Central`; demonstração na Célula 14).

### RF3 — Tabela de símbolos e novas verificações · **Fase semântica** (Células 2 e 8)
* Tabela da estufa com tipos, faixas dos sensores numéricos, valores permitidos do sensor de texto e faixas das ações com número.
* `verificar_bloco` é chamado para o `ENTAO` **e** para o `SENAO`, com as mesmas verificações: ação existente, dispositivo existente, tipo do dispositivo aceito, quantidade de argumentos e faixa do número.
* Condição: sensor declarado, tipos compatíveis, operador válido para o tipo (texto/lógico só com `==` e `!=`), literal dentro da faixa do sensor.
* **Aviso 1:** ação com os mesmos argumentos repetida dentro do mesmo bloco de uma regra.
* **Aviso 2:** duas regras com exatamente a mesma condição (comparação pela forma canônica gerada por `fmt`).
* Demonstrações na Célula 15.

### RF4 — Duas técnicas novas · **Fase de otimização** (Célula 9)
* **Eliminação de dupla negação:** `NAO NAO x → x`.
* **Identidades aritméticas:** `x + 0`, `0 + x`, `x - 0`, `x * 1`, `1 * x`, `x / 1 → x` e `x * 0 → 0`.
* O otimizador percorre a árvore em pós-ordem; cada transformação é registrada no relatório com regra, técnica, antes e depois (Células 13 e 15).

### RF5 — Bytecode e runtime · **Geração de código** (Célula 10) e **execução** (Célula 11)
* Cada regra compilada é um dicionário com três blocos: `condicao`, `entao` e `senao`.
* Literais de horário viram `PUSH_CONST <minutos>` (com comentário `; horário HH:MM`).
* Ações: `CALL <acao> <dispositivo> <nargs>`; com número, o argumento é empilhado antes com `PUSH_CONST`.
* Classe `Estufa` com o estado de todos os dispositivos e a execução das ações novas (`irrigar`, `ajustar_luz`, `abrir`, `fechar`), incluindo o consumo de água.
* `MaquinaVirtual` (pilha) avalia a condição e executa os blocos; `Central` guarda o último valor de cada condição e executa `ENTAO` na subida e `SENAO` na descida.

### RF6 — Testes e simulação · **Validação** (Células 16 e 17)
* Bateria com **18 casos**, todos ✅: 5 corretos, 4 erros léxicos (incluindo `25:00` e `18:75`), 4 erros sintáticos (incluindo `SENAO` vazio) e 5 erros semânticos (incluindo erro dentro do `SENAO`). Cada caso confere a fase do erro e um trecho da mensagem.
* Simulação de um dia com **13 eventos**, 5 disparos de `ENTAO` e 4 de `SENAO`, exibida em tabela e numa linha do tempo dos dispositivos.

## 4. Exemplo de programa e bytecode gerado

```
# EstufaScript — controle de uma estufa de hortaliças
# R1: irrigação por umidade do solo, inibida quando chove
QUANDO umidade_solo < 30 E NAO chovendo ENTAO
    irrigar(irrigador, 10)
SENAO
    desligar(irrigador)
FIM

# R2: fotoperíodo complementar das 18:30 às 22:00
QUANDO relogio >= 18:30 E relogio < 22:00 ENTAO
    ligar(lampada)
    ajustar_luz(lampada, 80)
SENAO
    desligar(lampada)
FIM

# R3: controle térmico (calor ou sol forte)
QUANDO temperatura > 32 OU NAO NAO (clima == "ensolarado" E luminosidade > 60000) ENTAO
    abrir(janela_teto, 70)
    ligar(ventilador)
    ligar(exaustor)
SENAO
    fechar(janela_teto)
    desligar(ventilador)
    desligar(exaustor)
FIM

# R4: proteção da bomba com reservatório baixo (regra sem SENAO)
QUANDO nivel_reservatorio * 1 < 15 + 0 ENTAO
    desligar(irrigador)
FIM
```

Otimizações aplicadas: `NAO NAO (...)` → `(...)` na regra 3; `nivel_reservatorio * 1` → `nivel_reservatorio` e `15 + 0` → `15` na regra 4.

```
── REGRA #1: QUANDO (umidade_solo < 30) E NAO chovendo
  [CONDICAO]
    000  LOAD_SENSOR umidade_solo
    001  PUSH_CONST  30
    002  CMP_LT
    003  LOAD_SENSOR chovendo
    004  NOT
    005  AND
  [ENTAO]
    000  PUSH_CONST  10            ; argumento
    001  CALL        irrigar irrigador 2
  [SENAO]
    000  CALL        desligar irrigador 1
── REGRA #2: QUANDO (relogio >= 18:30) E (relogio < 22:00)
  [CONDICAO]
    000  LOAD_SENSOR relogio
    001  PUSH_CONST  1110          ; horário 18:30
    002  CMP_GE
    003  LOAD_SENSOR relogio
    004  PUSH_CONST  1320          ; horário 22:00
    005  CMP_LT
    006  AND
  [ENTAO]
    000  CALL        ligar lampada 1
    001  PUSH_CONST  80            ; argumento
    002  CALL        ajustar_luz lampada 2
  [SENAO]
    000  CALL        desligar lampada 1
── REGRA #3: QUANDO (temperatura > 32) OU ((clima == "ensolarado") E (luminosidade > 60000))
  [CONDICAO]
    000  LOAD_SENSOR temperatura
    001  PUSH_CONST  32
    002  CMP_GT
    003  LOAD_SENSOR clima
    004  PUSH_CONST  "ensolarado"
    005  CMP_EQ
    006  LOAD_SENSOR luminosidade
    007  PUSH_CONST  60000
    008  CMP_GT
    009  AND
    010  OR
  [ENTAO]
    000  PUSH_CONST  70            ; argumento
    001  CALL        abrir janela_teto 2
    002  CALL        ligar ventilador 1
    003  CALL        ligar exaustor 1
  [SENAO]
    000  CALL        fechar janela_teto 1
    001  CALL        desligar ventilador 1
    002  CALL        desligar exaustor 1
── REGRA #4: QUANDO nivel_reservatorio < 15
  [CONDICAO]
    000  LOAD_SENSOR nivel_reservatorio
    001  PUSH_CONST  15
    002  CMP_LT
  [ENTAO]
    000  CALL        desligar irrigador 1
  [SENAO]
    (vazio)
```





