Victor Borges Quintella de Almeida - 2544963<br>
Kathleen Aquino Lima - 2364196<br>
João Victor Brandão - 2359197<br>
Lucas Costa - 2361186<br>

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
Evidências 

<img width="845" height="371" alt="image" src="https://github.com/user-attachments/assets/b0f1e750-3b3a-44cb-8f87-051c6295f2b7" />
<img width="804" height="235" alt="image" src="https://github.com/user-attachments/assets/0549cfc8-c887-4112-ab17-e6eb844c3536" />
<img width="856" height="369" alt="image" src="https://github.com/user-attachments/assets/ed3df3d4-723f-4549-afe2-4330d3c71eb5" />
<img width="851" height="324" alt="image" src="https://github.com/user-attachments/assets/342c6b2b-ef4b-41f0-91c1-57d6463edcea" />
<img width="842" height="278" alt="image" src="https://github.com/user-attachments/assets/564c9d9b-8f8d-4058-8997-2d46dadf9f3b" />
<img width="859" height="391" alt="image" src="https://github.com/user-attachments/assets/a3603841-9613-4157-837d-133bbf52faab" />
<img width="634" height="269" alt="image" src="https://github.com/user-attachments/assets/8a8c6cdc-af9b-4165-9f2c-eae40501fe28" />
<img width="521" height="395" alt="image" src="https://github.com/user-attachments/assets/4800eed7-2755-4a3c-9be2-14f1aa9d4fed" />
<img width="782" height="270" alt="image" src="https://github.com/user-attachments/assets/9c5f0a76-4209-463f-af6a-967b59578daa" />
<img width="446" height="374" alt="image" src="https://github.com/user-attachments/assets/6f244ae9-ec85-4874-8061-881af234a48f" />
<img width="640" height="400" alt="image" src="https://github.com/user-attachments/assets/d931c020-711d-4519-a1af-ae9910a1aa30" />
<img width="574" height="398" alt="image" src="https://github.com/user-attachments/assets/c5ec1472-e55d-4a06-b496-b6258956fb56" />
<img width="541" height="301" alt="image" src="https://github.com/user-attachments/assets/6c54a3c4-40b9-4c57-9096-6ba2e9263e27" />
<img width="862" height="365" alt="image" src="https://github.com/user-attachments/assets/e30104a9-9e0f-41f7-bf3d-f33395eb3e6b" />
<img width="864" height="394" alt="image" src="https://github.com/user-attachments/assets/836d076a-f7e3-496f-8ced-3e908a6101a5" />
<img width="853" height="345" alt="image" src="https://github.com/user-attachments/assets/9d0e73d6-127c-4816-accd-329db1323ac8" />
<img width="631" height="385" alt="image" src="https://github.com/user-attachments/assets/95ee5cf4-80c7-4804-aaa6-bffab03c54a8" />
<img width="599" height="386" alt="image" src="https://github.com/user-attachments/assets/4451f8b0-e65d-44c9-8bd3-305b9ea380cc" />
<img width="404" height="215" alt="image" src="https://github.com/user-attachments/assets/cdd33c61-afd5-4a69-96e6-319bf428d542" />
<img width="845" height="242" alt="image" src="https://github.com/user-attachments/assets/1c3b2e7d-b1ad-4e9b-afa4-ce990a372fb6" />
<img width="848" height="137" alt="image" src="https://github.com/user-attachments/assets/abae33c0-304f-43e1-a61a-aad4d13e7936" />
<img width="836" height="290" alt="image" src="https://github.com/user-attachments/assets/e81aad56-6bdd-45b8-b020-6537fc35ddf5" />
<img width="647" height="219" alt="image" src="https://github.com/user-attachments/assets/315cb10d-943c-4bd6-a1dc-22e34011d948" />
<img width="548" height="179" alt="image" src="https://github.com/user-attachments/assets/4531929f-958f-4c56-8346-2ecbb22bfb7d" />
<img width="842" height="335" alt="image" src="https://github.com/user-attachments/assets/5207003c-e7c4-4855-aef6-300eb9c912df" />
<img width="851" height="378" alt="image" src="https://github.com/user-attachments/assets/137009d8-f828-4fbe-bc99-17a0d8870f17" />
<img width="843" height="386" alt="image" src="https://github.com/user-attachments/assets/3a7569b0-37db-4062-b793-094729d99ab1" />
<img width="838" height="382" alt="image" src="https://github.com/user-attachments/assets/57832cbf-8502-4d20-b24d-4333dade7441" />
<img width="839" height="384" alt="image" src="https://github.com/user-attachments/assets/f877c773-0145-4381-9ea3-521edb221fdb" />
<img width="836" height="389" alt="image" src="https://github.com/user-attachments/assets/89127368-d980-431a-bd00-070fcf8fa863" />
<img width="840" height="392" alt="image" src="https://github.com/user-attachments/assets/2f2e9502-cb3d-413b-87ab-cce28a29cdcb" />
<img width="871" height="164" alt="image" src="https://github.com/user-attachments/assets/1c78f077-bac0-413d-9f1e-ca8a5d599ca0" />
<img width="845" height="297" alt="image" src="https://github.com/user-attachments/assets/0c8fb49a-1b92-4bdb-b6d8-ae1d367c8dda" />
<img width="830" height="386" alt="image" src="https://github.com/user-attachments/assets/f2a957e1-68e7-41dd-b849-6f5c99715d37" />
<img width="841" height="380" alt="image" src="https://github.com/user-attachments/assets/c4eff883-3169-42b7-868b-43d2d9847fd9" />
<img width="881" height="194" alt="image" src="https://github.com/user-attachments/assets/b4499e85-96bf-4461-b8ee-57dca17b5f21" />




































