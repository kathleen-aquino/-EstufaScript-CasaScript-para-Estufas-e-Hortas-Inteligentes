# %% [markdown]
# # 🌱 CasaScript → **EstufaScript**
# ### Prática 2 — Compilador para Estufa / Horta Inteligente
#
# Este notebook evolui a linguagem **CasaScript** para o mercado de **Agtech / agricultura de precisão / fazendas verticais**.
# Todas as fases do compilador foram alteradas:
#
# | Requisito | Fase | O que muda |
# |---|---|---|
# | **RF1** | Léxico | Token `HORARIO` (`HH:MM` → minutos desde 00:00) |
# | **RF2** | Sintático | Bloco opcional `SENAO` (borda de descida) |
# | **RF3** | Semântico | Tabela de símbolos da estufa + avisos de ação/condição repetida |
# | **RF4** | Otimização | Dupla negação e identidades aritméticas |
# | **RF5** | Geração de código / Runtime | 3 blocos de bytecode por regra, classe `Estufa`, `Central` com bordas |
# | **RF6** | Testes / Simulação | Bateria com 18 casos e simulação de um dia com 13 eventos |
#
# > ▶️ Para validar: **Ambiente de execução → Reiniciar e executar tudo**.

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 1 — Importações e tema visual (front-end do notebook)     ║
# ╚══════════════════════════════════════════════════════════════════╝
import re
import html
import copy
from dataclasses import dataclass
from typing import Any, List, Optional
from IPython.display import display, HTML

_FONTES = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
           '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800'
           '&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">')

_CSS = """<style>
.cs{font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:#e6edf3;background:#0d1117;
    border:1px solid #21303d;border-radius:16px;padding:18px 22px;margin:8px 0;line-height:1.45;font-size:14px}
.cs *{box-sizing:border-box}
.cs h1{font-size:28px;font-weight:800;margin:0 0 6px;letter-spacing:-.02em}
.cs h2{font-size:18px;font-weight:700;margin:0 0 2px}
.cs h3{font-size:12px;font-weight:700;margin:18px 0 8px;color:#86efac;text-transform:uppercase;letter-spacing:.08em}
.cs .sub{color:#8b9bab;font-size:13px;margin:2px 0 12px}
.cs .hero{background:linear-gradient(135deg,#14532d 0%,#0f3d2e 45%,#3b1a73 100%);border-radius:14px;padding:24px 26px}
.cs .hero p{color:#d1fae5;margin:4px 0 0;max-width:760px}
.cs .chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
.cs table{border-collapse:separate;border-spacing:0;width:100%;font-size:13px;border:1px solid #21303d;border-radius:12px;overflow:hidden}
.cs thead tr{background:linear-gradient(90deg,#4c1d95,#7c3aed)}
.cs th{background:transparent;color:#fff;text-align:left;padding:9px 11px;font-weight:600;white-space:nowrap}
.cs td{color:#d6dee6;padding:8px 11px;border-top:1px solid #1c2733;vertical-align:top}
.cs tr:nth-child(even) td{background:#111821}
.cs tr:hover td{background:#152230}
.cs code,.cs pre,.cs .mono{font-family:'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace}
.cs code{background:#1b2633;padding:1px 6px;border-radius:6px;font-size:12.5px;color:#c4b5fd}
.cs pre{background:#090d12;border:1px solid #1c2733;border-radius:10px;padding:12px 14px;overflow-x:auto;
        font-size:12.5px;line-height:1.6;margin:0;color:#d1d5db}
.cs .pill{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:700;margin:1px 2px;white-space:nowrap}
.cs .ok{background:#123d22;color:#86efac;border:1px solid #1f6b3a}
.cs .err{background:#3f0d1a;color:#fda4af;border:1px solid #7f1d35}
.cs .warn{background:#3a2606;color:#fcd34d;border:1px solid #78500f}
.cs .info{background:#132c52;color:#93c5fd;border:1px solid #1e4b8a}
.cs .roxo{background:#2e1765;color:#d8b4fe;border:1px solid #5b21b6}
.cs .laranja{background:#43200a;color:#fdba74;border:1px solid #9a3e0d}
.cs .cinza{background:#1f2933;color:#cbd5e1;border:1px solid #334155}
.cs .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.cs .card{background:#111821;border:1px solid #21303d;border-radius:12px;padding:12px 14px}
.cs .card .k{font-size:11px;color:#8b9bab;text-transform:uppercase;letter-spacing:.07em}
.cs .card .v{font-size:22px;font-weight:800;margin-top:2px}
.cs .status{border-radius:12px;padding:12px 16px;margin:4px 0 10px;font-weight:600}
.cs .status.okb{background:linear-gradient(90deg,#123d22,#0d1117);border-left:4px solid #22c55e}
.cs .status.errb{background:linear-gradient(90deg,#3f0d1a,#0d1117);border-left:4px solid #f43f5e}
.cs .status.warnb{background:linear-gradient(90deg,#3a2606,#0d1117);border-left:4px solid #f59e0b}
.cs .tok{display:inline-flex;flex-direction:column;align-items:center;border-radius:9px;padding:4px 8px;margin:3px;
         border:1px solid #2b3a48;background:#111821;min-width:46px}
.cs .tok b{font-family:'JetBrains Mono',monospace;font-size:13px}
.cs .tok i{font-style:normal;font-size:9.5px;letter-spacing:.06em;color:#8b9bab}
.cs .tok.kw{border-color:#6d28d9;background:#1d1240}.cs .tok.kw b{color:#c4b5fd}
.cs .tok.hr{border-color:#db2777;background:#3a0f27}.cs .tok.hr b{color:#f9a8d4}
.cs .tok.num b{color:#fcd34d}.cs .tok.txt b{color:#86efac}.cs .tok.id b{color:#7dd3fc}
.cs .bc{display:grid;grid-template-columns:repeat(3,minmax(200px,1fr));gap:10px}
.cs .bc .col{border-radius:10px;border:1px solid #21303d;overflow:hidden}
.cs .bc .col .hd{padding:6px 10px;font-weight:700;font-size:12px;letter-spacing:.06em}
.cs .bc .col pre{border:none;border-radius:0}
.cs .hd.c{background:#0c3a5c;color:#bae6fd}.cs .hd.e{background:#14532d;color:#bbf7d0}.cs .hd.s{background:#7c2d12;color:#fed7aa}
.cs .scroll{overflow-x:auto}
.cs details summary{cursor:pointer;color:#a5b4fc;font-weight:600;margin:6px 0}
.cs .muted{color:#6b7c8d}
</style>"""

def esc(x):
    return html.escape(str(x))

def show(corpo):
    """Renderiza um bloco HTML com o tema do notebook (cada saída do Colab é isolada, então o CSS vai junto)."""
    display(HTML(_FONTES + _CSS + f'<div class="cs">{corpo}</div>'))

def pill(texto, tipo='info'):
    return f'<span class="pill {tipo}">{esc(texto)}</span>'

def titulo(icone, texto, sub=''):
    s = f'<h2>{icone} {esc(texto)}</h2>'
    return s + (f'<div class="sub">{sub}</div>' if sub else '')

def tabela(cabecalho, linhas):
    """cabecalho: lista de strings; linhas: listas de células já em HTML."""
    th = ''.join(f'<th>{esc(c)}</th>' for c in cabecalho)
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in l) + '</tr>' for l in linhas)
    return f'<div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'

show('''<div class="hero">
  <h1>🌱 EstufaScript</h1>
  <p>Uma evolução da <b>CasaScript</b> para estufas e hortas inteligentes: regras <code>QUANDO … ENTAO … SENAO … FIM</code>
  que controlam irrigação, iluminação de cultivo, ventilação e a janela de teto a partir de sensores de solo, luz, clima e relógio.</p>
  <div class="chips">''' + ''.join(pill(t, c) for t, c in [
      ('RF1 · Léxico: HORARIO', 'roxo'), ('RF2 · Sintático: SENAO', 'laranja'),
      ('RF3 · Semântico: tabela da estufa', 'info'), ('RF4 · Otimização', 'warn'),
      ('RF5 · Bytecode + Runtime', 'ok'), ('RF6 · Testes + Simulação', 'cinza')]) + '''</div>
</div>''')

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 2 — Tabela de símbolos do cenário Estufa (RF3)            ║
# ╚══════════════════════════════════════════════════════════════════╝
SENSORES = {
    'umidade_solo':       {'tipo': 'numero',  'faixa': (0, 100),      'unidade': '%',   'icone': '💧', 'desc': 'Umidade volumétrica do solo'},
    'luminosidade':       {'tipo': 'numero',  'faixa': (0, 100000),   'unidade': 'lux', 'icone': '☀️', 'desc': 'Iluminância sobre o dossel'},
    'temperatura':        {'tipo': 'numero',  'faixa': (-10, 60),     'unidade': '°C',  'icone': '🌡️', 'desc': 'Temperatura interna do ar'},
    'nivel_reservatorio': {'tipo': 'numero',  'faixa': (0, 100),      'unidade': '%',   'icone': '🛢️', 'desc': 'Nível da caixa d\'água de irrigação'},
    'clima':              {'tipo': 'texto',   'valores': ['ensolarado', 'nublado', 'chuvoso'], 'icone': '⛅', 'desc': 'Condição do tempo (estação meteorológica)'},
    'chovendo':           {'tipo': 'logico',  'icone': '🌧️', 'desc': 'Pluviômetro detectou chuva'},
    'relogio':            {'tipo': 'horario', 'faixa': (0, 1439),     'unidade': 'min', 'icone': '🕒', 'desc': 'Hora do dia (minutos desde 00:00)'},
}

DISPOSITIVOS = {
    'irrigador':   {'tipo': 'irrigador',       'icone': '🚿', 'desc': 'Válvula de irrigação por gotejamento'},
    'lampada':     {'tipo': 'lampada_cultivo', 'icone': '💡', 'desc': 'Lâmpada de cultivo LED full-spectrum'},
    'ventilador':  {'tipo': 'ventilador',      'icone': '🌀', 'desc': 'Ventilador de circulação interna'},
    'exaustor':    {'tipo': 'ventilador',      'icone': '🌪️', 'desc': 'Exaustor de ar quente'},
    'janela_teto': {'tipo': 'janela',          'icone': '🪟', 'desc': 'Janela zenital motorizada'},
}

ACOES = {
    'ligar':       {'params': ['dispositivo'],           'tipos': ['irrigador', 'lampada_cultivo', 'ventilador'], 'nova': False, 'desc': 'Liga o dispositivo'},
    'desligar':    {'params': ['dispositivo'],           'tipos': ['irrigador', 'lampada_cultivo', 'ventilador'], 'nova': False, 'desc': 'Desliga o dispositivo'},
    'irrigar':     {'params': ['dispositivo', 'numero'], 'tipos': ['irrigador'],       'faixa': (1, 60),  'unidade': 'min', 'nova': True, 'desc': 'Irriga por N minutos'},
    'ajustar_luz': {'params': ['dispositivo', 'numero'], 'tipos': ['lampada_cultivo'], 'faixa': (0, 100), 'unidade': '%',   'nova': True, 'desc': 'Define a intensidade da lâmpada'},
    'abrir':       {'params': ['dispositivo', 'numero'], 'tipos': ['janela'],          'faixa': (0, 100), 'unidade': '%',   'nova': True, 'desc': 'Abre a janela N%'},
    'fechar':      {'params': ['dispositivo'],           'tipos': ['janela'],          'nova': True, 'desc': 'Fecha a janela'},
}

_COR_TIPO = {'numero': 'warn', 'texto': 'ok', 'logico': 'info', 'horario': 'roxo'}

def mostrar_tabela_simbolos():
    sens = [[f'{s["icone"]} <code>{n}</code>', pill(s['tipo'], _COR_TIPO[s['tipo']]),
             (f'{s["faixa"][0]} … {s["faixa"][1]} {s.get("unidade","")}' if s['tipo'] == 'numero'
              else '00:00 … 23:59' if s['tipo'] == 'horario'
              else ' | '.join(f'"{v}"' for v in s['valores']) if s['tipo'] == 'texto' else 'VERDADEIRO | FALSO'),
             esc(s['desc'])] for n, s in SENSORES.items()]
    disp = [[f'{d["icone"]} <code>{n}</code>', pill(d['tipo'], 'cinza'), esc(d['desc'])] for n, d in DISPOSITIVOS.items()]
    acs = [[f'<code>{n}({", ".join(a["params"])})</code>' + (' ' + pill('nova', 'laranja') if a['nova'] else ''),
            ' '.join(pill(t, 'cinza') for t in a['tipos']),
            f'{a["faixa"][0]} … {a["faixa"][1]} {a["unidade"]}' if 'faixa' in a else '<span class="muted">—</span>',
            esc(a['desc'])] for n, a in ACOES.items()]
    tipos_sens = {s['tipo'] for s in SENSORES.values()}
    tipos_disp = {d['tipo'] for d in DISPOSITIVOS.values()}
    resumo = ''.join(f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in [
        ('Sensores', f'{len(SENSORES)} <span class="muted" style="font-size:13px">({len(tipos_sens)} tipos)</span>'),
        ('Dispositivos', f'{len(DISPOSITIVOS)} <span class="muted" style="font-size:13px">({len(tipos_disp)} tipos)</span>'),
        ('Ações', f'{len(ACOES)} <span class="muted" style="font-size:13px">({sum(a["nova"] for a in ACOES.values())} novas)</span>')])
    show(titulo('📋', 'Tabela de símbolos — Estufa inteligente', 'Agtech · agricultura de precisão · fazendas verticais')
         + f'<div class="grid">{resumo}</div>'
         + '<h3>Sensores</h3>' + tabela(['Sensor', 'Tipo', 'Faixa / valores', 'Descrição'], sens)
         + '<h3>Dispositivos</h3>' + tabela(['Dispositivo', 'Tipo', 'Descrição'], disp)
         + '<h3>Ações</h3>' + tabela(['Assinatura', 'Tipos aceitos', 'Faixa do número', 'Descrição'], acs))

# Garantias do RF3 sobre a própria tabela
assert len(SENSORES) >= 5 and {'numero', 'texto', 'logico', 'horario'} <= {s['tipo'] for s in SENSORES.values()}
assert len(DISPOSITIVOS) >= 4 and len({d['tipo'] for d in DISPOSITIVOS.values()}) >= 3
assert sum(a['nova'] for a in ACOES.values()) >= 2 and any(a['nova'] and a['params'] == ['dispositivo', 'numero'] for a in ACOES.values())
mostrar_tabela_simbolos()

# %% [markdown]
# ## Etapa 1 — Cenário e tabela de símbolos (RF3)
# O cenário escolhido é a **Estufa / horta inteligente**. A tabela de símbolos define os sensores (com tipo e faixa), os dispositivos (com tipo) e as ações (com parâmetros, tipos de dispositivo aceitos e faixa do argumento numérico).

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 3 — Analisador léxico com o token HORARIO (RF1)           ║
# ╚══════════════════════════════════════════════════════════════════╝
class ErroLexico(Exception): pass
class ErroSintatico(Exception): pass

PALAVRAS_RESERVADAS = {'QUANDO', 'ENTAO', 'SENAO', 'FIM', 'E', 'OU', 'NAO', 'VERDADEIRO', 'FALSO'}

@dataclass
class Token:
    tipo: str
    valor: Any
    lexema: str
    linha: int
    coluna: int

# A ORDEM importa: HORARIO vem antes de NUMERO para que "18:30" seja um token só.
ESPEC_TOKENS = [
    ('NOVALINHA',  r'\n'),
    ('ESPACO',     r'[ \t\r]+'),
    ('COMENTARIO', r'\#[^\n]*'),
    ('HORARIO',    r'\d+:\d+'),
    ('NUMERO',     r'\d+(?:\.\d+)?'),
    ('TEXTO',      r'"[^"\n]*"'),
    ('IDENT',      r'[A-Za-z_][A-Za-z0-9_]*'),
    ('OP_REL',     r'>=|<=|==|!=|>|<'),
    ('OP_ARIT',    r'[+\-*/]'),
    ('ABRE_PAR',   r'\('),
    ('FECHA_PAR',  r'\)'),
    ('VIRGULA',    r','),
]
_MESTRE = re.compile('|'.join(f'(?P<{nome}>{padrao})' for nome, padrao in ESPEC_TOKENS))

def horario_para_minutos(lexema, linha=0, coluna=0):
    """'18:30' -> 1110. Lança ErroLexico se o formato ou os valores forem inválidos."""
    m = re.fullmatch(r'(\d{2}):(\d{2})', lexema)
    onde = f'Linha {linha}, col {coluna}: ' if linha else ''
    if not m:
        raise ErroLexico(f"{onde}horário inválido '{lexema}' — o formato deve ser HH:MM")
    h, mi = int(m.group(1)), int(m.group(2))
    if h > 23:
        raise ErroLexico(f"{onde}horário inválido '{lexema}' — hora {h:02d} fora de 00..23")
    if mi > 59:
        raise ErroLexico(f"{onde}horário inválido '{lexema}' — minuto {mi:02d} fora de 00..59")
    return h * 60 + mi

def minutos_para_horario(m):
    return f'{int(m) // 60:02d}:{int(m) % 60:02d}'

def analisar_lexico(fonte):
    tokens, linha, inicio_linha, pos = [], 1, 0, 0
    while pos < len(fonte):
        m = _MESTRE.match(fonte, pos)
        col = pos - inicio_linha + 1
        if not m:
            ch = fonte[pos]
            if ch == '"':
                raise ErroLexico(f'Linha {linha}, col {col}: texto não fechado (falta a aspa final)')
            raise ErroLexico(f"Linha {linha}, col {col}: caractere inesperado '{ch}'")
        tipo, lex = m.lastgroup, m.group()
        pos = m.end()
        if tipo == 'NOVALINHA':
            linha, inicio_linha = linha + 1, pos
            continue
        if tipo in ('ESPACO', 'COMENTARIO'):
            continue
        if tipo == 'HORARIO':
            valor = horario_para_minutos(lex, linha, col)
        elif tipo == 'NUMERO':
            valor = float(lex) if '.' in lex else int(lex)
        elif tipo == 'TEXTO':
            valor = lex[1:-1]
        elif tipo == 'IDENT' and lex in PALAVRAS_RESERVADAS:
            tipo = lex
            valor = {'VERDADEIRO': True, 'FALSO': False}.get(lex, lex)
        else:
            valor = lex
        tokens.append(Token(tipo, valor, lex, linha, col))
    tokens.append(Token('EOF', None, '', linha, pos - inicio_linha + 1))
    return tokens

def _classe_token(t):
    if t.tipo in PALAVRAS_RESERVADAS: return 'kw'
    return {'HORARIO': 'hr', 'NUMERO': 'num', 'TEXTO': 'txt', 'IDENT': 'id'}.get(t.tipo, '')

def html_tokens(tokens):
    partes = []
    for t in tokens:
        if t.tipo == 'EOF':
            continue
        extra = f' → {t.valor} min' if t.tipo == 'HORARIO' else ''
        partes.append(f'<span class="tok {_classe_token(t)}"><b>{esc(t.lexema)}</b><i>{esc(t.tipo)}{esc(extra)}</i></span>')
    return '<div>' + ''.join(partes) + '</div>'

print('✔ Léxico carregado:', len(ESPEC_TOKENS), 'padrões de token')

# %% [markdown]
# ## Etapa 2 — Analisador léxico (RF1)
# Novo token **`HORARIO`** no formato `HH:MM`. A expressão regular de horário é testada **antes** da de número, então `18:30` vira um único token (e não `18`, `:`, `30`). O lexema é validado (`00..23` e `00..59`) e convertido para **minutos desde a meia-noite** (`18:30 → 1110`). `25:00` e `18:75` geram **erro léxico**.

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 4 — Demonstração do RF1                                   ║
# ╚══════════════════════════════════════════════════════════════════╝
exemplo = 'QUANDO relogio >= 18:30 ENTAO ligar(lampada) FIM'
toks = analisar_lexico(exemplo)
tok_h = [t for t in toks if t.tipo == 'HORARIO']
assert len(tok_h) == 1 and tok_h[0].lexema == '18:30' and tok_h[0].valor == 1110

linhas = []
for src in ['18:30', '00:00', '23:59', '07:05', '25:00', '18:75', '7:30']:
    try:
        t = analisar_lexico(src)[0]
        linhas.append([f'<code>{src}</code>', pill('OK', 'ok'), f'<code>{t.tipo}</code>', f'<b>{t.valor}</b> min'])
    except ErroLexico as e:
        linhas.append([f'<code>{src}</code>', pill('ERRO LÉXICO', 'err'), '—', f'<span class="muted">{esc(e)}</span>'])

show(titulo('🔤', 'RF1 — Literal de horário', f'Fonte: <code>{esc(exemplo)}</code>')
     + '<h3>Fluxo de tokens</h3>' + html_tokens(toks)
     + f'<div class="status okb">✅ <code>18:30</code> reconhecido como <b>um único token HORARIO</b> com valor <b>{tok_h[0].valor}</b> minutos.</div>'
     + '<h3>Validação de horários</h3>' + tabela(['Entrada', 'Resultado', 'Token', 'Valor / mensagem'], linhas))

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 5 — Nós da AST                                            ║
# ╚══════════════════════════════════════════════════════════════════╝
@dataclass
class Literal:
    valor: Any
    tipo: str            # 'numero' | 'texto' | 'logico' | 'horario'

@dataclass
class Sensor:
    nome: str
    linha: int = 0

@dataclass
class Nao:
    expr: Any

@dataclass
class BinOp:
    op: str              # relacional, aritmético, 'E' ou 'OU'
    esq: Any
    dir: Any

@dataclass
class Acao:
    nome: str
    dispositivo: str
    argumento: Optional[Any]
    linha: int = 0

@dataclass
class Regra:
    condicao: Any
    entao: List[Acao]
    senao: List[Acao]    # NOVO (RF2): lista vazia quando não há SENAO
    linha: int = 0

@dataclass
class Programa:
    regras: List[Regra]

def fmt(n, topo=True):
    """Converte uma expressão da AST de volta em código-fonte canônico."""
    if isinstance(n, Literal):
        if n.tipo == 'horario': return minutos_para_horario(n.valor)
        if n.tipo == 'texto':   return f'"{n.valor}"'
        if n.tipo == 'logico':  return 'VERDADEIRO' if n.valor else 'FALSO'
        v = n.valor
        return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)
    if isinstance(n, Sensor): return n.nome
    if isinstance(n, Nao):    return 'NAO ' + fmt(n.expr, False)
    if isinstance(n, BinOp):
        s = f'{fmt(n.esq, False)} {n.op} {fmt(n.dir, False)}'
        return s if topo else f'({s})'
    return str(n)

def fmt_acao(a):
    if a.argumento is None:
        return f'{a.nome}({a.dispositivo})'
    v = a.argumento
    v = int(v) if isinstance(v, float) and v.is_integer() else v
    return f'{a.nome}({a.dispositivo}, {v})'

print('✔ Nós da AST definidos: Programa, Regra(condicao, entao, senao), Acao, BinOp, Nao, Sensor, Literal')

# %% [markdown]
# ## Etapa 3 — Árvore sintática abstrata e analisador sintático (RF2)
# A gramática ganhou o bloco opcional `SENAO`:
#
# ```
# programa  → regra+ EOF
# regra     → QUANDO expr ENTAO acoes [ SENAO acoes ] FIM
# acoes     → acao+                       (bloco vazio = erro sintático)
# acao      → IDENT '(' IDENT [ ',' ['-'] NUMERO ] ')'
# expr      → ou
# ou        → e ( OU e )*
# e         → nao ( E nao )*
# nao       → NAO nao | rel
# rel       → soma [ OP_REL soma ]
# soma      → termo ( ('+'|'-') termo )*
# termo     → fator ( ('*'|'/') fator )*
# fator     → NUMERO | HORARIO | TEXTO | VERDADEIRO | FALSO | IDENT | '(' expr ')' | '-' fator
# ```

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 6 — Analisador sintático (descida recursiva) com SENAO    ║
# ╚══════════════════════════════════════════════════════════════════╝
_NOMES = {'ABRE_PAR': "'('", 'FECHA_PAR': "')'", 'VIRGULA': "','", 'IDENT': 'identificador',
          'NUMERO': 'número', 'HORARIO': 'horário', 'TEXTO': 'texto', 'EOF': 'fim do arquivo'}

class Parser:
    def __init__(self, tokens):
        self.t, self.i = tokens, 0

    @property
    def atual(self):
        return self.t[self.i]

    def avancar(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def ver(self, *tipos):
        return self.atual.tipo in tipos

    def erro(self, msg):
        tok = self.atual
        achado = 'fim do arquivo' if tok.tipo == 'EOF' else f"'{tok.lexema}'"
        raise ErroSintatico(f'Linha {tok.linha}, col {tok.coluna}: {msg}; encontrado {achado}')

    def esperar(self, tipo, ctx=''):
        if not self.ver(tipo):
            self.erro(f'esperado {_NOMES.get(tipo, tipo)}{ctx}')
        return self.avancar()

    # ---------- estrutura ----------
    def programa(self):
        regras = []
        while not self.ver('EOF'):
            regras.append(self.regra())
        if not regras:
            raise ErroSintatico('Programa vazio: esperada ao menos uma regra QUANDO … FIM')
        return Programa(regras)

    def regra(self):
        inicio = self.esperar('QUANDO', ' no início da regra')
        cond = self.expressao()
        self.esperar('ENTAO', ' após a condição')
        entao = self.bloco('ENTAO')
        senao = []
        if self.ver('SENAO'):                     # RF2: bloco opcional
            self.avancar()
            senao = self.bloco('SENAO')
        self.esperar('FIM', ' para fechar a regra')
        return Regra(cond, entao, senao, inicio.linha)

    def bloco(self, nome):
        acoes = []
        while self.ver('IDENT'):
            acoes.append(self.acao())
        if not acoes:                              # RF2: SENAO (ou ENTAO) sem ações
            self.erro(f'bloco {nome} vazio — esperada ao menos uma ação')
        return acoes

    def acao(self):
        nome = self.avancar()
        self.esperar('ABRE_PAR', f" após '{nome.lexema}'")
        disp = self.esperar('IDENT', ' (dispositivo)')
        arg = None
        if self.ver('VIRGULA'):
            self.avancar()
            negativo = self.ver('OP_ARIT') and self.atual.lexema == '-'
            if negativo:
                self.avancar()
            num = self.esperar('NUMERO', ' como argumento numérico')
            arg = -num.valor if negativo else num.valor
        self.esperar('FECHA_PAR', f" para fechar '{nome.lexema}('")
        return Acao(nome.lexema, disp.lexema, arg, nome.linha)

    # ---------- expressões ----------
    def expressao(self):
        return self.ou()

    def ou(self):
        n = self.e()
        while self.ver('OU'):
            self.avancar()
            n = BinOp('OU', n, self.e())
        return n

    def e(self):
        n = self.nao()
        while self.ver('E'):
            self.avancar()
            n = BinOp('E', n, self.nao())
        return n

    def nao(self):
        if self.ver('NAO'):
            self.avancar()
            return Nao(self.nao())
        return self.relacional()

    def relacional(self):
        n = self.soma()
        if self.ver('OP_REL'):
            op = self.avancar().lexema
            n = BinOp(op, n, self.soma())
        return n

    def soma(self):
        n = self.termo()
        while self.ver('OP_ARIT') and self.atual.lexema in ('+', '-'):
            op = self.avancar().lexema
            n = BinOp(op, n, self.termo())
        return n

    def termo(self):
        n = self.fator()
        while self.ver('OP_ARIT') and self.atual.lexema in ('*', '/'):
            op = self.avancar().lexema
            n = BinOp(op, n, self.fator())
        return n

    def fator(self):
        tok = self.atual
        if tok.tipo == 'NUMERO':     self.avancar(); return Literal(tok.valor, 'numero')
        if tok.tipo == 'HORARIO':    self.avancar(); return Literal(tok.valor, 'horario')
        if tok.tipo == 'TEXTO':      self.avancar(); return Literal(tok.valor, 'texto')
        if tok.tipo in ('VERDADEIRO', 'FALSO'):
            self.avancar(); return Literal(tok.valor, 'logico')
        if tok.tipo == 'IDENT':      self.avancar(); return Sensor(tok.lexema, tok.linha)
        if tok.tipo == 'ABRE_PAR':
            self.avancar()
            n = self.expressao()
            self.esperar('FECHA_PAR', ' para fechar a expressão')
            return n
        if tok.tipo == 'OP_ARIT' and tok.lexema == '-':
            self.avancar()
            f = self.fator()
            if isinstance(f, Literal) and f.tipo == 'numero':
                return Literal(-f.valor, 'numero')
            return BinOp('-', Literal(0, 'numero'), f)
        self.erro('esperada uma expressão (sensor, número, horário, texto ou "(")')

def analisar_sintatico(tokens):
    return Parser(tokens).programa()

print('✔ Parser carregado (QUANDO … ENTAO … [SENAO …] FIM)')

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 7 — Desenho da AST (SVG colorido + árvore em texto)       ║
# ╚══════════════════════════════════════════════════════════════════╝
_CORES_NO = {
    'prog':   ('#4c1d95', '#ede9fe'), 'regra': ('#6d28d9', '#f5f3ff'),
    'cond':   ('#0c4a6e', '#e0f2fe'), 'entao': ('#15803d', '#dcfce7'), 'senao': ('#c2410c', '#ffedd5'),
    'acao':   ('#1f6b3a', '#d1fae5'), 'op':    ('#334155', '#f1f5f9'), 'sensor': ('#0e7490', '#cffafe'),
    'lit':    ('#92400e', '#fef3c7'), 'disp':  ('#1e293b', '#cbd5e1'),
}

def ast_para_arvore(n, idx=None):
    """Converte a AST em tuplas (rótulo, tipo_visual, filhos)."""
    if isinstance(n, Programa):
        return ('PROGRAMA', 'prog', [ast_para_arvore(r, i) for i, r in enumerate(n.regras, 1)])
    if isinstance(n, Regra):
        filhos = [('CONDIÇÃO', 'cond', [ast_para_arvore(n.condicao)]),
                  ('ENTAO', 'entao', [ast_para_arvore(a) for a in n.entao])]
        if n.senao:
            filhos.append(('SENAO', 'senao', [ast_para_arvore(a) for a in n.senao]))
        return (f'REGRA #{idx}', 'regra', filhos)
    if isinstance(n, Acao):
        filhos = [(n.dispositivo, 'disp', [])]
        if n.argumento is not None:
            filhos.append((fmt(Literal(n.argumento, 'numero')), 'lit', []))
        return (f'{n.nome}()', 'acao', filhos)
    if isinstance(n, BinOp):  return (n.op, 'op', [ast_para_arvore(n.esq), ast_para_arvore(n.dir)])
    if isinstance(n, Nao):    return ('NAO', 'op', [ast_para_arvore(n.expr)])
    if isinstance(n, Sensor): return (n.nome, 'sensor', [])
    if isinstance(n, Literal):
        rot = fmt(n) + (f' ({n.valor} min)' if n.tipo == 'horario' else '')
        return (rot, 'lit', [])
    return (str(n), 'op', [])

def arvore_texto(t, prefixo='', ultimo=True, raiz=True):
    rotulo, _, filhos = t
    linhas = [rotulo if raiz else prefixo + ('└── ' if ultimo else '├── ') + rotulo]
    novo = '' if raiz else prefixo + ('    ' if ultimo else '│   ')
    for i, f in enumerate(filhos):
        linhas += arvore_texto(f, novo, i == len(filhos) - 1, False)
    return linhas

def ast_svg(t):
    nos, arestas = [], []
    def folhas(x):
        return 1 if not x[2] else sum(folhas(f) for f in x[2])
    def posicionar(x, esquerda, prof):
        rot, tipo, filhos = x
        if not filhos:
            cx = esquerda + 0.5
        else:
            cursor, xs = esquerda, []
            for f in filhos:
                xs.append(posicionar(f, cursor, prof + 1))
                cursor += folhas(f)
            cx = (xs[0] + xs[-1]) / 2
            for xf in xs:
                arestas.append((cx, prof, xf, prof + 1))
        nos.append((cx, prof, rot, tipo))
        return cx
    posicionar(t, 0, 0)
    maior = max(len(n[2]) for n in nos)
    W, H = max(96, maior * 7.4 + 26), 74
    largura, altura = folhas(t) * W, (max(n[1] for n in nos) + 1) * H
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura:.0f}" height="{altura:.0f}" '
              f'viewBox="0 0 {largura:.0f} {altura:.0f}" style="font-family:JetBrains Mono,monospace">']
    for x1, p1, x2, p2 in arestas:
        X1, Y1, X2, Y2 = x1 * W, p1 * H + 46, x2 * W, p2 * H + 18
        meio = (Y1 + Y2) / 2
        partes.append(f'<path d="M{X1:.1f},{Y1:.1f} C{X1:.1f},{meio:.1f} {X2:.1f},{meio:.1f} {X2:.1f},{Y2:.1f}" '
                      f'stroke="#3b4b5c" stroke-width="1.6" fill="none"/>')
    for cx, prof, rot, tipo in nos:
        fundo, texto = _CORES_NO[tipo]
        bw = len(rot) * 7.4 + 18
        X, Y = cx * W - bw / 2, prof * H + 18
        partes.append(f'<rect x="{X:.1f}" y="{Y:.1f}" width="{bw:.1f}" height="28" rx="8" fill="{fundo}" '
                      f'stroke="{texto}" stroke-opacity=".25"/>')
        peso = '700' if tipo in ('prog', 'regra', 'cond', 'entao', 'senao') else '400'
        partes.append(f'<text x="{cx * W:.1f}" y="{Y + 18.5:.1f}" fill="{texto}" font-size="12" font-weight="{peso}" '
                      f'text-anchor="middle">{esc(rot)}</text>')
    partes.append('</svg>')
    return ''.join(partes)

def html_ast(ast):
    t = ast_para_arvore(ast)
    legenda = ' '.join(f'<span class="pill" style="background:{c[0]};color:{c[1]}">{n}</span>' for n, c in [
        ('regra', _CORES_NO['regra']), ('condição', _CORES_NO['cond']), ('ENTAO', _CORES_NO['entao']),
        ('SENAO', _CORES_NO['senao']), ('ação', _CORES_NO['acao']), ('operador', _CORES_NO['op']),
        ('sensor', _CORES_NO['sensor']), ('literal', _CORES_NO['lit']), ('dispositivo', _CORES_NO['disp'])])
    caixa = '<div class="scroll" style="background:#090d12;border:1px solid #1c2733;border-radius:12px;padding:6px;margin-bottom:8px">{}</div>'
    # Programas com várias regras: um desenho por regra (fica legível); a árvore em texto mostra o PROGRAMA inteiro.
    desenhos = ''.join(caixa.format(ast_svg(sub)) for sub in t[2]) if len(t[2]) > 1 else caixa.format(ast_svg(t))
    return (f'<div style="margin-bottom:8px">{legenda}</div>{desenhos}'
            f'<details><summary>Ver AST completa em texto</summary><pre>{esc(chr(10).join(arvore_texto(t)))}</pre></details>')

# Demonstração do RF2 na AST
_src_rf2 = '''QUANDO umidade_solo < 30 ENTAO
    irrigar(irrigador, 10)
SENAO
    desligar(irrigador)
FIM'''
_ast_rf2 = analisar_sintatico(analisar_lexico(_src_rf2))
assert _ast_rf2.regras[0].senao and _ast_rf2.regras[0].senao[0].nome == 'desligar'
show(titulo('🌳', 'RF2 — AST com o bloco SENAO', 'O nó <b style="color:#fdba74">SENAO</b> aparece como terceiro filho da regra.')
     + f'<pre>{esc(_src_rf2)}</pre><h3>Desenho da AST</h3>' + html_ast(_ast_rf2))

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 8 — Analisador semântico (RF3)                            ║
# ╚══════════════════════════════════════════════════════════════════╝
OPS_REL  = {'<', '>', '<=', '>=', '==', '!='}
OPS_ARIT = {'+', '-', '*', '/'}

class AnalisadorSemantico:
    def __init__(self):
        self.erros, self.avisos = [], []

    def analisar(self, prog):
        condicoes_vistas = {}
        for i, r in enumerate(prog.regras, 1):
            ctx = f'Regra #{i} (linha {r.linha}), condição'
            t = self.tipo(r.condicao, ctx)
            if t is not None and t != 'logico':
                self.erros.append(f"{ctx}: a condição deve ser lógica, mas '{fmt(r.condicao)}' é do tipo {t}")
            self.verificar_bloco(r.entao, 'ENTAO', i)
            self.verificar_bloco(r.senao, 'SENAO', i)      # SENAO passa pelas MESMAS verificações
            chave = fmt(r.condicao)                          # Aviso 2: condição repetida
            if chave in condicoes_vistas:
                self.avisos.append(f"Regras #{condicoes_vistas[chave]} e #{i} têm exatamente a mesma condição: '{chave}'")
            else:
                condicoes_vistas[chave] = i
        return self.erros, self.avisos

    # ---------- tipos das expressões ----------
    def tipo(self, n, ctx):
        if isinstance(n, Literal):
            return n.tipo
        if isinstance(n, Sensor):
            if n.nome in SENSORES:
                return SENSORES[n.nome]['tipo']
            if n.nome in DISPOSITIVOS:
                self.erros.append(f"{ctx}: '{n.nome}' é um dispositivo, não um sensor")
            else:
                self.erros.append(f"{ctx}: sensor '{n.nome}' não declarado na tabela de símbolos")
            return None
        if isinstance(n, Nao):
            t = self.tipo(n.expr, ctx)
            if t is not None and t != 'logico':
                self.erros.append(f"{ctx}: NAO exige operando lógico, recebeu {t} em '{fmt(n)}'")
            return 'logico'
        if isinstance(n, BinOp):
            if n.op in ('E', 'OU'):
                for lado in (n.esq, n.dir):
                    t = self.tipo(lado, ctx)
                    if t is not None and t != 'logico':
                        self.erros.append(f"{ctx}: {n.op} exige operandos lógicos, mas '{fmt(lado)}' é {t}")
                return 'logico'
            if n.op in OPS_ARIT:
                tl, tr = self.tipo(n.esq, ctx), self.tipo(n.dir, ctx)
                if None in (tl, tr):
                    return None
                if tl != 'numero' or tr != 'numero':
                    self.erros.append(f"{ctx}: operador '{n.op}' só se aplica a números ('{fmt(n)}' usa {tl} e {tr})")
                    return None
                return 'numero'
            if n.op in OPS_REL:
                tl, tr = self.tipo(n.esq, ctx), self.tipo(n.dir, ctx)
                if None in (tl, tr):
                    return 'logico'
                if tl != tr:
                    self.erros.append(f"{ctx}: não é possível comparar {tl} com {tr} em '{fmt(n)}'")
                elif tl in ('texto', 'logico') and n.op not in ('==', '!='):
                    self.erros.append(f"{ctx}: operador '{n.op}' não se aplica a {tl} (use == ou !=)")
                else:
                    self.verificar_faixa(n, ctx)
                return 'logico'
        return None

    def verificar_faixa(self, n, ctx):
        for s, lit in ((n.esq, n.dir), (n.dir, n.esq)):
            if isinstance(s, Sensor) and isinstance(lit, Literal) and s.nome in SENSORES:
                info = SENSORES[s.nome]
                if info['tipo'] == 'numero':
                    lo, hi = info['faixa']
                    if not lo <= lit.valor <= hi:
                        self.erros.append(f"{ctx}: valor {fmt(lit)} fora da faixa de '{s.nome}' "
                                          f"[{lo}, {hi}] {info['unidade']}")
                elif info['tipo'] == 'texto' and lit.valor not in info['valores']:
                    self.erros.append(f"{ctx}: '{s.nome}' só aceita {info['valores']}, recebeu \"{lit.valor}\"")

    # ---------- ações (ENTAO e SENAO) ----------
    def verificar_bloco(self, acoes, bloco, i):
        vistas = set()
        for a in acoes:
            ctx = f'Regra #{i}, bloco {bloco} (linha {a.linha})'
            if a.nome not in ACOES:
                self.erros.append(f"{ctx}: ação '{a.nome}' não existe")
                continue
            spec = ACOES[a.nome]
            if a.dispositivo not in DISPOSITIVOS:
                tipo = 'é um sensor, não um dispositivo' if a.dispositivo in SENSORES else 'não declarado'
                self.erros.append(f"{ctx}: dispositivo '{a.dispositivo}' {tipo}")
            elif DISPOSITIVOS[a.dispositivo]['tipo'] not in spec['tipos']:
                self.erros.append(f"{ctx}: '{a.nome}' não se aplica a '{a.dispositivo}' "
                                  f"(tipo {DISPOSITIVOS[a.dispositivo]['tipo']}; aceita {', '.join(spec['tipos'])})")
            recebidos = 1 + (a.argumento is not None)
            if recebidos != len(spec['params']):
                self.erros.append(f"{ctx}: '{a.nome}' espera {len(spec['params'])} argumento(s) "
                                  f"({', '.join(spec['params'])}), recebeu {recebidos}")
            elif a.argumento is not None and 'faixa' in spec:
                lo, hi = spec['faixa']
                if not lo <= a.argumento <= hi:
                    self.erros.append(f"{ctx}: argumento {a.argumento} de '{a.nome}' fora da faixa "
                                      f"[{lo}, {hi}] {spec['unidade']}")
            chave = (a.nome, a.dispositivo, a.argumento)   # Aviso 1: ação repetida
            if chave in vistas:
                self.avisos.append(f"Regra #{i}, bloco {bloco}: ação '{fmt_acao(a)}' repetida (linha {a.linha})")
            vistas.add(chave)

print('✔ Semântico carregado')

# %% [markdown]
# ## Etapa 4 — Analisador semântico (RF3)
# Verifica a condição (sensores existentes, tipos compatíveis, faixas e valores permitidos) e **as ações dos blocos `ENTAO` e `SENAO` com as mesmas regras** (ação existe, dispositivo existe e é do tipo aceito, número de argumentos e faixa do número).  
# Duas verificações novas emitem **avisos** (não impedem a compilação):
# 1. a mesma ação, com os mesmos argumentos, repetida no mesmo bloco de uma regra;
# 2. duas regras diferentes com exatamente a mesma condição.

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 9 — Otimizador (RF4)                                      ║
# ╚══════════════════════════════════════════════════════════════════╝
_ARIT = {'+': lambda a, b: a + b, '-': lambda a, b: a - b, '*': lambda a, b: a * b, '/': lambda a, b: a / b}
_REL  = {'<': lambda a, b: a < b, '>': lambda a, b: a > b, '<=': lambda a, b: a <= b,
         '>=': lambda a, b: a >= b, '==': lambda a, b: a == b, '!=': lambda a, b: a != b}

def _eh_num(n, v):
    return isinstance(n, Literal) and n.tipo == 'numero' and n.valor == v

def _normaliza(v):
    return int(v) if isinstance(v, float) and v.is_integer() else v

class Otimizador:
    DUPLA_NEG = 'Eliminação de dupla negação'
    IDENT     = 'Identidade aritmética'
    CONST     = 'Dobramento de constantes'

    def __init__(self):
        self.relatorio = []
        self.regra = 0

    def otimizar(self, prog):
        for i, r in enumerate(prog.regras, 1):
            self.regra = i
            r.condicao = self.opt(r.condicao)
        return prog

    def _reg(self, tecnica, antes, depois):
        self.relatorio.append({'regra': self.regra, 'tecnica': tecnica, 'antes': fmt(antes), 'depois': fmt(depois)})
        return depois

    def opt(self, n):
        if isinstance(n, Nao):
            interno = self.opt(n.expr)
            if isinstance(interno, Nao):                                    # NAO NAO x -> x
                return self._reg(self.DUPLA_NEG, Nao(interno), interno.expr)
            if isinstance(interno, Literal) and interno.tipo == 'logico':
                return self._reg(self.CONST, Nao(interno), Literal(not interno.valor, 'logico'))
            return Nao(interno)

        if isinstance(n, BinOp):
            l, r = self.opt(n.esq), self.opt(n.dir)
            atual = BinOp(n.op, l, r)
            ll, rl = isinstance(l, Literal), isinstance(r, Literal)
            # identidades aritméticas
            if n.op in ('+', '-') and _eh_num(r, 0):  return self._reg(self.IDENT, atual, l)   # x + 0, x - 0
            if n.op == '+' and _eh_num(l, 0):          return self._reg(self.IDENT, atual, r)   # 0 + x
            if n.op in ('*', '/') and _eh_num(r, 1):  return self._reg(self.IDENT, atual, l)   # x * 1, x / 1
            if n.op == '*' and _eh_num(l, 1):          return self._reg(self.IDENT, atual, r)   # 1 * x
            if n.op == '*' and (_eh_num(r, 0) or _eh_num(l, 0)):
                return self._reg(self.IDENT, atual, Literal(0, 'numero'))                     # x * 0
            # dobramento de constantes (depois das identidades)
            if n.op in _ARIT and ll and rl and l.tipo == r.tipo == 'numero' and not (n.op == '/' and r.valor == 0):
                return self._reg(self.CONST, atual, Literal(_normaliza(_ARIT[n.op](l.valor, r.valor)), 'numero'))
            if n.op in _REL and ll and rl and l.tipo == r.tipo:
                return self._reg(self.CONST, atual, Literal(_REL[n.op](l.valor, r.valor), 'logico'))
            return atual
        return n

_COR_TEC = {Otimizador.DUPLA_NEG: 'roxo', Otimizador.IDENT: 'warn', Otimizador.CONST: 'info'}

def html_relatorio_otimizacao(rel):
    if not rel:
        return '<div class="muted">Nenhuma otimização aplicável.</div>'
    return tabela(['Regra', 'Técnica', 'Antes', 'Depois'],
                  [[f'#{x["regra"]}', pill(x['tecnica'], _COR_TEC.get(x['tecnica'], 'cinza')),
                    f'<code>{esc(x["antes"])}</code>', f'<code style="color:#86efac">{esc(x["depois"])}</code>']
                   for x in rel])

print('✔ Otimizador carregado:', Otimizador.DUPLA_NEG, '|', Otimizador.IDENT, '|', Otimizador.CONST)

# %% [markdown]
# ## Etapa 5 — Otimizador (RF4)
# Percorre a condição de cada regra de baixo para cima (pós-ordem), então uma simplificação pode habilitar a seguinte (ex.: `x * 0 + y → 0 + y → y`). Além do **dobramento de constantes**, há duas técnicas novas:
# * **Eliminação de dupla negação:** `NAO NAO x → x`
# * **Identidades aritméticas:** `x + 0`, `x - 0`, `x * 1`, `x / 1 → x` e `x * 0 → 0`
#
# Cada transformação entra no relatório com **técnica, antes e depois**.

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 10 — Gerador de bytecode (RF5)                            ║
# ╚══════════════════════════════════════════════════════════════════╝
_OPCODE = {'<': 'CMP_LT', '>': 'CMP_GT', '<=': 'CMP_LE', '>=': 'CMP_GE', '==': 'CMP_EQ', '!=': 'CMP_NE',
           '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', 'E': 'AND', 'OU': 'OR'}

@dataclass
class Instr:
    op: str
    args: tuple = ()
    nota: str = ''

    def texto(self):
        a = ' '.join(f'"{x}"' if isinstance(x, str) and self.op == 'PUSH_CONST' else str(x) for x in self.args)
        s = f'{self.op:<12}{a}'.rstrip()
        return f'{s:<26}; {self.nota}' if self.nota else s

class GeradorCodigo:
    def gerar(self, prog):
        return [{'id': i, 'fonte': fmt(r.condicao),
                 'condicao': self.expr(r.condicao),
                 'entao': self.acoes(r.entao),
                 'senao': self.acoes(r.senao)}          # RF5: terceiro bloco
                for i, r in enumerate(prog.regras, 1)]

    def expr(self, n):
        if isinstance(n, Literal):
            if n.tipo == 'horario':
                return [Instr('PUSH_CONST', (n.valor,), f'horário {minutos_para_horario(n.valor)}')]
            if n.tipo == 'logico':
                return [Instr('PUSH_CONST', (n.valor,), 'lógico')]
            return [Instr('PUSH_CONST', (n.valor,))]
        if isinstance(n, Sensor):
            return [Instr('LOAD_SENSOR', (n.nome,))]
        if isinstance(n, Nao):
            return self.expr(n.expr) + [Instr('NOT')]
        if isinstance(n, BinOp):
            return self.expr(n.esq) + self.expr(n.dir) + [Instr(_OPCODE[n.op])]
        raise ValueError(f'nó desconhecido: {n}')

    def acoes(self, acoes):
        codigo = []
        for a in acoes:
            if a.argumento is not None:
                codigo.append(Instr('PUSH_CONST', (_normaliza(a.argumento),), 'argumento'))
                codigo.append(Instr('CALL', (a.nome, a.dispositivo, 2)))
            else:
                codigo.append(Instr('CALL', (a.nome, a.dispositivo, 1)))
        return codigo

def bytecode_texto(bytecode):
    linhas = []
    for r in bytecode:
        linhas.append(f'── REGRA #{r["id"]}: QUANDO {r["fonte"]}')
        for bloco in ('condicao', 'entao', 'senao'):
            linhas.append(f'  [{bloco.upper()}]')
            if not r[bloco]:
                linhas.append('    (vazio)')
            for k, ins in enumerate(r[bloco]):
                linhas.append(f'    {k:03d}  {ins.texto()}')
    return '\n'.join(linhas)

def html_bytecode(bytecode):
    partes = []
    for r in bytecode:
        cols = ''
        for bloco, cls, nome in (('condicao', 'c', 'CONDIÇÃO'), ('entao', 'e', 'ENTAO'), ('senao', 's', 'SENAO')):
            corpo = '\n'.join(f'<span class="muted">{k:03d}</span>  {esc(i.texto())}' for k, i in enumerate(r[bloco])) \
                    or '<span class="muted">— vazio (regra sem SENAO)</span>'
            cols += f'<div class="col"><div class="hd {cls}">{nome} · {len(r[bloco])} instr.</div><pre>{corpo}</pre></div>'
        partes.append(f'<div style="margin:10px 0 4px"><b>Regra #{r["id"]}</b> <code>{esc(r["fonte"])}</code></div>'
                      f'<div class="scroll"><div class="bc">{cols}</div></div>')
    return ''.join(partes)

print('✔ Gerador de código carregado')

# %% [markdown]
# ## Etapa 6 — Geração de código (RF5)
# Máquina de pilha. Cada regra compilada tem **três blocos**: `condicao`, `entao` e `senao`. Horários viram `PUSH_CONST` com o valor em **minutos**. Ações com número empilham o argumento e chamam `CALL acao dispositivo nargs`.

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 11 — Ambiente Estufa, VM de pilha e Central (RF5)         ║
# ╚══════════════════════════════════════════════════════════════════╝
class Estufa:
    """Ambiente físico: guarda o estado dos dispositivos e executa as ações."""
    VAZAO_L_POR_MIN = 2.0

    def __init__(self):
        self.estado = {
            'irrigador':   {'ligado': False, 'minutos': 0},
            'lampada':     {'ligado': False, 'intensidade': 0},
            'ventilador':  {'ligado': False},
            'exaustor':    {'ligado': False},
            'janela_teto': {'abertura': 0},
        }
        self.agua_litros = 0.0

    def executar(self, acao, disp, arg=None):
        e, ic = self.estado[disp], DISPOSITIVOS[disp]['icone']
        if acao == 'ligar':
            e['ligado'] = True
            if disp == 'lampada' and e['intensidade'] == 0:
                e['intensidade'] = 100
            return f'{ic} {disp} ligado'
        if acao == 'desligar':
            e['ligado'] = False
            if 'intensidade' in e: e['intensidade'] = 0
            if 'minutos' in e:     e['minutos'] = 0
            return f'{ic} {disp} desligado'
        if acao == 'irrigar':                                   # NOVA
            e['ligado'], e['minutos'] = True, arg
            self.agua_litros += arg * self.VAZAO_L_POR_MIN
            return f'{ic} irrigando por {arg} min (~{arg * self.VAZAO_L_POR_MIN:.0f} L)'
        if acao == 'ajustar_luz':                               # NOVA
            e['intensidade'], e['ligado'] = arg, arg > 0
            return f'{ic} intensidade em {arg}%'
        if acao == 'abrir':                                     # NOVA
            e['abertura'] = arg
            return f'{ic} janela aberta {arg}%'
        if acao == 'fechar':                                    # NOVA
            e['abertura'] = 0
            return f'{ic} janela fechada'
        raise ValueError(f'ação sem implementação: {acao}')

    def resumo_html(self):
        s = self.estado
        def chip(ic, on, txt):
            return f'<span class="pill {"ok" if on else "cinza"}">{ic} {txt}</span>'
        return ''.join([
            chip('🚿', s['irrigador']['ligado'], 'ON' if s['irrigador']['ligado'] else 'OFF'),
            chip('💡', s['lampada']['ligado'], f'{s["lampada"]["intensidade"]}%' if s['lampada']['ligado'] else 'OFF'),
            chip('🌀', s['ventilador']['ligado'], 'ON' if s['ventilador']['ligado'] else 'OFF'),
            chip('🌪️', s['exaustor']['ligado'], 'ON' if s['exaustor']['ligado'] else 'OFF'),
            chip('🪟', s['janela_teto']['abertura'] > 0, f'{s["janela_teto"]["abertura"]}%')])

    def ativo(self, disp):
        e = self.estado[disp]
        return e.get('ligado', False) or e.get('abertura', 0) > 0

class MaquinaVirtual:
    _BIN = {'CMP_LT': _REL['<'], 'CMP_GT': _REL['>'], 'CMP_LE': _REL['<='], 'CMP_GE': _REL['>='],
            'CMP_EQ': _REL['=='], 'CMP_NE': _REL['!='], 'ADD': _ARIT['+'], 'SUB': _ARIT['-'], 'MUL': _ARIT['*'],
            'DIV': lambda a, b: a / b if b else 0, 'AND': lambda a, b: a and b, 'OR': lambda a, b: a or b}

    def avaliar(self, codigo, sensores):
        pilha = []
        for ins in codigo:
            if ins.op == 'PUSH_CONST':
                pilha.append(ins.args[0])
            elif ins.op == 'LOAD_SENSOR':
                pilha.append(sensores[ins.args[0]])
            elif ins.op == 'NOT':
                pilha.append(not pilha.pop())
            else:
                b, a = pilha.pop(), pilha.pop()
                pilha.append(self._BIN[ins.op](a, b))
        return bool(pilha.pop())

    def executar_acoes(self, codigo, ambiente):
        pilha, log = [], []
        for ins in codigo:
            if ins.op == 'PUSH_CONST':
                pilha.append(ins.args[0])
            elif ins.op == 'CALL':
                nome, disp, nargs = ins.args
                arg = pilha.pop() if nargs == 2 else None
                log.append(ambiente.executar(nome, disp, arg))
        return log

class Central:
    """Executa as regras com detecção de borda: subida → ENTAO, descida → SENAO."""
    def __init__(self, bytecode, ambiente, sensores_iniciais):
        self.regras, self.amb, self.vm = bytecode, ambiente, MaquinaVirtual()
        self.sensores = {k: self._converter(k, v) for k, v in sensores_iniciais.items()}
        self.anterior = {r['id']: False for r in bytecode}
        self.historico = []

    @staticmethod
    def _converter(nome, valor):
        if nome not in SENSORES:
            raise KeyError(f'sensor desconhecido: {nome}')
        if SENSORES[nome]['tipo'] == 'horario' and isinstance(valor, str):
            return horario_para_minutos(valor)
        return valor

    def evento(self, descricao, **leituras):
        for k, v in leituras.items():
            self.sensores[k] = self._converter(k, v)
        disparos = []
        for r in self.regras:
            agora, antes = self.vm.avaliar(r['condicao'], self.sensores), self.anterior[r['id']]
            if agora and not antes:                                  # borda de subida
                disparos.append(('ENTAO', r['id'], self.vm.executar_acoes(r['entao'], self.amb)))
            elif antes and not agora and r['senao']:                 # borda de descida
                disparos.append(('SENAO', r['id'], self.vm.executar_acoes(r['senao'], self.amb)))
            self.anterior[r['id']] = agora
        self.historico.append({'hora': self.sensores.get('relogio', 0), 'evento': descricao, 'leituras': leituras,
                               'disparos': disparos, 'estado': copy.deepcopy(self.amb.estado),
                               'resumo': self.amb.resumo_html()})
        return disparos

print('✔ Runtime carregado: Estufa, MaquinaVirtual, Central')

# %% [markdown]
# ## Etapa 7 — Runtime: classe `Estufa`, máquina virtual e central (RF5)
# A `Central` guarda o último valor de cada condição. A cada evento:
# * **borda de subida** (FALSO → VERDADEIRO) → executa o bloco `ENTAO`;
# * **borda de descida** (VERDADEIRO → FALSO) → executa o bloco `SENAO`.

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 12 — Pipeline do compilador + relatório visual            ║
# ╚══════════════════════════════════════════════════════════════════╝
def compilar(fonte):
    res = {'fonte': fonte, 'fase_erro': None, 'erros': [], 'avisos': [], 'tokens': None,
           'ast': None, 'ast_otimizada': None, 'otimizacoes': [], 'bytecode': None}
    try:
        res['tokens'] = analisar_lexico(fonte)
    except ErroLexico as e:
        res.update(fase_erro='léxico', erros=[str(e)])
        return res
    try:
        res['ast'] = analisar_sintatico(res['tokens'])
    except ErroSintatico as e:
        res.update(fase_erro='sintático', erros=[str(e)])
        return res
    erros, avisos = AnalisadorSemantico().analisar(res['ast'])
    res['avisos'] = avisos
    if erros:
        res.update(fase_erro='semântico', erros=erros)
        return res
    res['ast_otimizada'] = copy.deepcopy(res['ast'])
    otm = Otimizador()
    otm.otimizar(res['ast_otimizada'])
    res['otimizacoes'] = otm.relatorio
    res['bytecode'] = GeradorCodigo().gerar(res['ast_otimizada'])
    return res

def html_status(res):
    if res['fase_erro']:
        msgs = ''.join(f'<div style="font-weight:400;margin-top:4px">• {esc(m)}</div>' for m in res['erros'])
        return f'<div class="status errb">❌ Erro {res["fase_erro"]}{msgs}</div>'
    r = res['bytecode']
    n_instr = sum(len(x['condicao']) + len(x['entao']) + len(x['senao']) for x in r)
    return (f'<div class="status okb">✅ Compilado com sucesso — {len(r)} regra(s), {len(res["tokens"]) - 1} tokens, '
            f'{n_instr} instruções, {len(res["otimizacoes"])} otimização(ões)</div>')

def html_avisos(avisos):
    return ''.join(f'<div class="status warnb">⚠️ {esc(a)}</div>' for a in avisos)

def relatorio_compilacao(res, titulo_txt='Compilação', mostrar=('fonte', 'tokens', 'ast', 'otim', 'bytecode')):
    h = titulo('⚙️', titulo_txt) + html_status(res) + html_avisos(res['avisos'])
    if 'fonte' in mostrar:
        h += f'<details open><summary>Código-fonte</summary><pre>{esc(res["fonte"])}</pre></details>'
    if res['tokens'] and 'tokens' in mostrar:
        h += f'<details><summary>Tokens ({len(res["tokens"]) - 1})</summary>{html_tokens(res["tokens"])}</details>'
    if res['ast'] and 'ast' in mostrar and not res['fase_erro']:
        h += '<h3>AST</h3>' + html_ast(res['ast'])
    if res['bytecode'] is not None:
        if 'otim' in mostrar:
            h += '<h3>Relatório do otimizador</h3>' + html_relatorio_otimizacao(res['otimizacoes'])
        if 'bytecode' in mostrar:
            h += '<h3>Bytecode</h3>' + html_bytecode(res['bytecode'])
            h += f'<details><summary>Bytecode em texto</summary><pre>{esc(bytecode_texto(res["bytecode"]))}</pre></details>'
    show(h)

print('✔ Pipeline pronto: compilar(fonte) → relatorio_compilacao(res)')

# %% [markdown]
# ## Etapa 8 — Pipeline completo do compilador
# `compilar(fonte)` executa **léxico → sintático → semântico → otimização → geração de código** e devolve tudo o que foi produzido em cada fase. `relatorio_compilacao(...)` desenha o resultado.

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 13 — Programa da estufa inteligente                       ║
# ╚══════════════════════════════════════════════════════════════════╝
PROGRAMA_ESTUFA = '''# EstufaScript — controle de uma estufa de hortaliças
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
'''
res_estufa = compilar(PROGRAMA_ESTUFA)
assert res_estufa['fase_erro'] is None, res_estufa['erros']
relatorio_compilacao(res_estufa, 'Programa da estufa — todas as fases')

# %% [markdown]
# ## Etapa 9 — Programa completo da estufa
# Programa usado no README e na simulação do dia. Usa horário, texto, lógico, `SENAO`, as ações novas e expressões que o otimizador simplifica.

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 14 — RF2: SENAO dispara na borda de descida               ║
# ╚══════════════════════════════════════════════════════════════════╝
_res = compilar(_src_rf2)
_central = Central(_res['bytecode'], Estufa(), {'umidade_solo': 50})
_linhas = []
for desc, umid in [('Solo úmido', 50), ('Solo seca', 25), ('Continua seco', 22), ('Após irrigação', 55), ('Continua úmido', 60)]:
    d = _central.evento(desc, umidade_solo=umid)
    cond = umid < 30
    disparo = ' '.join(pill(f'{b} → ' + '; '.join(a), 'ok' if b == 'ENTAO' else 'laranja') for b, _, a in d) \
              or '<span class="muted">—</span>'
    _linhas.append([esc(desc), f'<b>{umid}%</b>', pill('VERDADEIRO', 'ok') if cond else pill('FALSO', 'cinza'),
                    disparo, _central.amb.resumo_html()])
_blocos = [d[0] for h in _central.historico for d in h['disparos']]
assert _blocos == ['ENTAO', 'SENAO'], _blocos
show(titulo('🔁', 'RF2 — Execução do SENAO na borda de descida', f'<code>QUANDO umidade_solo &lt; 30 ENTAO irrigar(irrigador, 10) SENAO desligar(irrigador) FIM</code>')
     + tabela(['Evento', 'umidade_solo', 'Condição', 'Disparo', 'Estufa'], _linhas)
     + '<h3>Bytecode com os três blocos</h3>' + html_bytecode(_res['bytecode']))

# %% [markdown]
# ## Etapa 10 — Demonstrações dos requisitos RF2, RF3 e RF4

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 15 — RF3 (avisos e erro no SENAO) e RF4 (otimizações)     ║
# ╚══════════════════════════════════════════════════════════════════╝
SRC_AVISOS = '''QUANDO temperatura > 30 ENTAO
    ligar(ventilador)
    ligar(ventilador)
FIM
QUANDO temperatura > 30 ENTAO
    abrir(janela_teto, 50)
FIM'''
r_av = compilar(SRC_AVISOS)
assert r_av['fase_erro'] is None and len(r_av['avisos']) == 2
relatorio_compilacao(r_av, 'RF3 — Avisos: ação repetida e condição repetida', mostrar=('fonte',))

SRC_ERRO_SENAO = '''QUANDO relogio >= 06:00 ENTAO
    abrir(janela_teto, 40)
SENAO
    abrir(irrigador, 50)
    irrigar(irrigador, 90)
FIM'''
r_es = compilar(SRC_ERRO_SENAO)
assert r_es['fase_erro'] == 'semântico' and all('SENAO' in e for e in r_es['erros'])
relatorio_compilacao(r_es, 'RF3 — Ações erradas dentro do SENAO são detectadas', mostrar=('fonte',))

SRC_OTIM = '''QUANDO NAO NAO chovendo ENTAO fechar(janela_teto) FIM
QUANDO umidade_solo * 1 < 30 + 0 ENTAO irrigar(irrigador, 5) FIM
QUANDO temperatura - 0 > 25 E luminosidade / 1 > 500 ENTAO ligar(exaustor) FIM
QUANDO temperatura * 0 + umidade_solo > 80 ENTAO desligar(irrigador) FIM
QUANDO NAO NAO NAO (temperatura >= 5 * 1) ENTAO desligar(lampada) FIM'''
r_ot = compilar(SRC_OTIM)
_tecs = {x['tecnica'] for x in r_ot['otimizacoes']}
assert Otimizador.DUPLA_NEG in _tecs and Otimizador.IDENT in _tecs
relatorio_compilacao(r_ot, 'RF4 — Dupla negação e identidades aritméticas', mostrar=('fonte', 'otim', 'bytecode'))

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 16 — Bateria de testes (RF6)                              ║
# ╚══════════════════════════════════════════════════════════════════╝
CASOS = [
    # (nome, fonte, fase esperada, trecho esperado na mensagem)
    ('Horário 18:30 como token único', 'QUANDO relogio >= 18:30 ENTAO ligar(lampada) FIM', None, ''),
    ('Irrigação com SENAO', 'QUANDO umidade_solo < 30 ENTAO irrigar(irrigador, 10) SENAO desligar(irrigador) FIM', None, ''),
    ('Texto + lógico + janela', 'QUANDO clima == "chuvoso" OU chovendo ENTAO fechar(janela_teto) SENAO abrir(janela_teto, 40) FIM', None, ''),
    ('Dupla negação + identidade', 'QUANDO NAO NAO (temperatura * 1 > 35) ENTAO ligar(exaustor) ligar(ventilador) FIM', None, ''),
    ('Várias regras + ajustar_luz', '''QUANDO relogio >= 05:30 E luminosidade < 2000 ENTAO ajustar_luz(lampada, 40) FIM
QUANDO nivel_reservatorio < 10 ENTAO desligar(irrigador) SENAO ligar(irrigador) FIM''', None, ''),

    ('Horário inválido 25:00', 'QUANDO relogio >= 25:00 ENTAO ligar(lampada) FIM', 'léxico', '25:00'),
    ('Minuto inválido 18:75', 'QUANDO relogio < 18:75 ENTAO ligar(lampada) FIM', 'léxico', '18:75'),
    ('Caractere inesperado @', 'QUANDO temperatura > 30 @ ENTAO ligar(ventilador) FIM', 'léxico', '@'),
    ('Texto não fechado', 'QUANDO clima == "nublado ENTAO ligar(lampada) FIM', 'léxico', 'não fechado'),

    ('SENAO vazio', 'QUANDO umidade_solo < 30 ENTAO irrigar(irrigador, 10) SENAO FIM', 'sintático', 'SENAO vazio'),
    ('Falta ENTAO', 'QUANDO temperatura > 30 ligar(ventilador) FIM', 'sintático', 'ENTAO'),
    ('Falta FIM', 'QUANDO temperatura > 30 ENTAO ligar(ventilador)', 'sintático', 'FIM'),
    ('Parêntese não fechado', 'QUANDO umidade_solo < 30 ENTAO irrigar(irrigador, 10 FIM', 'sintático', "')'"),

    ('Erro dentro do SENAO', 'QUANDO umidade_solo < 30 ENTAO irrigar(irrigador, 10) SENAO abrir(irrigador, 50) FIM', 'semântico', 'bloco SENAO'),
    ('Sensor inexistente', 'QUANDO ph_solo < 6 ENTAO ligar(irrigador) FIM', 'semântico', 'ph_solo'),
    ('Valor fora da faixa do sensor', 'QUANDO umidade_solo < 150 ENTAO irrigar(irrigador, 10) FIM', 'semântico', 'fora da faixa'),
    ('Argumento fora da faixa', 'QUANDO umidade_solo < 20 ENTAO irrigar(irrigador, 90) FIM', 'semântico', 'irrigar'),
    ('Horário comparado com número', 'QUANDO relogio > 30 ENTAO ligar(lampada) FIM', 'semântico', 'horario com numero'),
]

resultados = []
for nome, fonte, fase_esp, trecho in CASOS:
    r = compilar(fonte)
    msg = ' | '.join(r['erros'])
    passou = r['fase_erro'] == fase_esp and (trecho in msg)
    resultados.append((nome, fonte, fase_esp, r, msg, passou))

_cor_fase = {None: 'ok', 'léxico': 'roxo', 'sintático': 'laranja', 'semântico': 'info'}
linhas = []
for k, (nome, fonte, fase_esp, r, msg, passou) in enumerate(resultados, 1):
    obtido = r['fase_erro']
    linhas.append([f'<b>{k:02d}</b>', esc(nome), f'<code style="white-space:pre-wrap">{esc(fonte)}</code>',
                   pill(fase_esp or 'correto', _cor_fase[fase_esp]), pill(obtido or 'correto', _cor_fase[obtido]),
                   f'<span class="muted" style="font-size:12px">{esc(msg) if msg else "compilou"}</span>',
                   '✅' if passou else '❌'])

def _conta(f): return sum(1 for c in CASOS if c[2] == f)
total_ok = sum(1 for x in resultados if x[5])
cards = ''.join(f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in [
    ('Resultado', f'{total_ok}/{len(CASOS)} ✅'), ('Corretos', _conta(None)), ('Erro léxico', _conta('léxico')),
    ('Erro sintático', _conta('sintático')), ('Erro semântico', _conta('semântico'))])
show(titulo('🧪', 'Bateria de testes — Célula 16', 'Fase esperada × fase obtida para cada programa')
     + f'<div class="grid">{cards}</div><h3>Casos</h3>'
     + tabela(['#', 'Caso', 'Programa', 'Esperado', 'Obtido', 'Mensagem', 'OK'], linhas))

assert len(CASOS) >= 12 and _conta(None) >= 4 and _conta('léxico') >= 2 and _conta('sintático') >= 3 and _conta('semântico') >= 3
assert total_ok == len(CASOS), 'Há casos falhando!'
print(f'✅ Todos os {len(CASOS)} casos passaram.')

# %% [markdown]
# ## Etapa 11 — Bateria de testes (RF6)
# 18 casos: 5 corretos, 4 com erro léxico, 4 com erro sintático e 5 com erro semântico. Cada caso declara a fase esperada e um trecho que deve aparecer na mensagem.

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 17 — Simulação de um dia (RF6)                            ║
# ╚══════════════════════════════════════════════════════════════════╝
estufa = Estufa()
central = Central(res_estufa['bytecode'], estufa, {
    'umidade_solo': 45, 'luminosidade': 0, 'temperatura': 18, 'nivel_reservatorio': 80,
    'clima': 'nublado', 'chovendo': False, 'relogio': '00:00'})

EVENTOS = [
    ('Amanhecer',                  dict(relogio='05:30', luminosidade=800, temperatura=17)),
    ('Sol nasce',                  dict(relogio='07:00', clima='ensolarado', luminosidade=20000, temperatura=21)),
    ('Solo secando',               dict(relogio='09:30', umidade_solo=28)),
    ('Irrigação concluída',        dict(relogio='09:45', umidade_solo=52)),
    ('Pico de sol',                dict(relogio='12:00', luminosidade=75000, temperatura=30)),
    ('Calor intenso',              dict(relogio='13:30', temperatura=34)),
    ('Nuvens chegam',              dict(relogio='15:00', clima='nublado', luminosidade=30000, temperatura=29)),
    ('Começa a chover',            dict(relogio='16:00', chovendo=True, clima='chuvoso', umidade_solo=25)),
    ('Chuva para, solo ainda seco',dict(relogio='17:00', chovendo=False, clima='nublado', umidade_solo=27)),
    ('Reservatório baixo',         dict(relogio='17:20', nivel_reservatorio=12, umidade_solo=40)),
    ('Anoitecer',                  dict(relogio='18:30', luminosidade=200, temperatura=22)),
    ('Fim do fotoperíodo',         dict(relogio='22:00', luminosidade=0, temperatura=19)),
    ('Reservatório reabastecido',  dict(relogio='23:00', nivel_reservatorio=90)),
]
for desc, leituras in EVENTOS:
    central.evento(desc, **leituras)

def _fmt_leitura(k, v):
    if k == 'relogio': return None
    if isinstance(v, bool): v = 'VERDADEIRO' if v else 'FALSO'
    return f'{SENSORES[k]["icone"]} {k}={v}{SENSORES[k].get("unidade", "") if isinstance(v, (int, float)) else ""}'

linhas = []
for k, h in enumerate(central.historico, 1):
    leit = ' '.join(f'<span class="pill cinza">{esc(x)}</span>' for x in
                    (_fmt_leitura(a, b) for a, b in h['leituras'].items()) if x)
    disp = '<br>'.join(f'{pill(f"R{rid} · {bloco}", "ok" if bloco == "ENTAO" else "laranja")} '
                       f'<span style="font-size:12px">{esc("; ".join(acs))}</span>' for bloco, rid, acs in h['disparos']) \
           or '<span class="muted">—</span>'
    linhas.append([f'<b>{k:02d}</b>', f'<span class="mono">{minutos_para_horario(h["hora"])}</span>',
                   f'<b>{esc(h["evento"])}</b>', leit, disp, h['resumo']])

# Linha do tempo (Gantt) dos dispositivos ao longo do dia
def gantt_svg(hist):
    devs = list(DISPOSITIVOS)
    L, W, RH = 130, 720, 30
    alt = len(devs) * RH + 40
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{L + W + 20}" height="{alt}" style="font-family:Inter,sans-serif">']
    for hh in range(0, 25, 3):
        x = L + hh * 60 * W / 1440
        p.append(f'<line x1="{x}" y1="10" x2="{x}" y2="{alt - 22}" stroke="#1f2a36"/>'
                 f'<text x="{x}" y="{alt - 6}" fill="#8b9bab" font-size="11" text-anchor="middle">{hh:02d}h</text>')
    for i, d in enumerate(devs):
        y = 12 + i * RH
        p.append(f'<text x="{L - 10}" y="{y + 17}" fill="#cbd5e1" font-size="12" text-anchor="end">'
                 f'{DISPOSITIVOS[d]["icone"]} {d}</text>'
                 f'<rect x="{L}" y="{y + 4}" width="{W}" height="20" rx="5" fill="#111821"/>')
        faixas = []                                   # junta intervalos contíguos em que o dispositivo ficou ativo
        for j, h in enumerate(hist):
            ini, fim = h['hora'], hist[j + 1]['hora'] if j + 1 < len(hist) else 1440
            e = h['estado'][d]
            if e.get('ligado') or e.get('abertura', 0) > 0:
                if faixas and faixas[-1][1] == ini:
                    faixas[-1][1] = fim
                else:
                    faixas.append([ini, fim])
        cor = '#f97316' if d == 'janela_teto' else '#22c55e'
        for ini, fim in faixas:
            p.append(f'<rect x="{L + ini * W / 1440:.1f}" y="{y + 4}" width="{max((fim - ini) * W / 1440, 3):.1f}" '
                     f'height="20" rx="5" fill="{cor}" opacity=".9"><title>{d}: {minutos_para_horario(ini)}–'
                     f'{minutos_para_horario(min(fim, 1439))}</title></rect>')
    p.append('</svg>')
    return ''.join(p)

n_entao = sum(1 for h in central.historico for d in h['disparos'] if d[0] == 'ENTAO')
n_senao = sum(1 for h in central.historico for d in h['disparos'] if d[0] == 'SENAO')
cards = ''.join(f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in [
    ('Eventos', len(central.historico)), ('Disparos ENTAO', n_entao), ('Disparos SENAO', n_senao),
    ('Água usada', f'{estufa.agua_litros:.0f} L')])
show(titulo('🌞', 'Simulação de um dia na estufa', 'ENTAO na borda de subida · SENAO na borda de descida')
     + f'<div class="grid">{cards}</div>'
     + '<h3>Linha do tempo dos dispositivos</h3>'
     + f'<div class="scroll" style="background:#090d12;border:1px solid #1c2733;border-radius:12px;padding:8px">{gantt_svg(central.historico)}</div>'
     + '<h3>Eventos</h3>'
     + tabela(['#', 'Hora', 'Evento', 'Leituras', 'Disparos', 'Estado da estufa'], linhas))

assert len(central.historico) >= 10 and n_entao >= 1 and n_senao >= 1
print(f'✅ Simulação: {len(central.historico)} eventos, {n_entao} ENTAO, {n_senao} SENAO')

# %% [markdown]
# ## Etapa 12 — Simulação de um dia na estufa (RF6)
# O programa da Etapa 9 é carregado na `Central` e recebe 13 eventos de sensores ao longo de um dia. A tabela mostra quais regras dispararam (`ENTAO` na subida, `SENAO` na descida) e o estado dos dispositivos depois de cada evento.

# %%
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Célula 18 — Playground interativo (ipywidgets)                   ║
# ╚══════════════════════════════════════════════════════════════════╝
try:
    import ipywidgets as widgets
    _editor = widgets.Textarea(value=_src_rf2, layout=widgets.Layout(width='100%', height='200px'))
    _exemplos = widgets.Dropdown(options=[('SENAO simples', _src_rf2), ('Programa da estufa', PROGRAMA_ESTUFA),
                                          ('Otimizações', SRC_OTIM), ('Avisos', SRC_AVISOS), ('Erro no SENAO', SRC_ERRO_SENAO)],
                                 description='Exemplo:')
    _botao = widgets.Button(description='▶ Compilar', button_style='success', icon='play')
    _saida = widgets.Output()

    def _compilar(_=None):
        _saida.clear_output()
        with _saida:
            relatorio_compilacao(compilar(_editor.value), 'Playground')

    def _trocar(mudanca):
        _editor.value = mudanca['new']
        _compilar()

    _exemplos.observe(_trocar, names='value')
    _botao.on_click(_compilar)
    display(widgets.VBox([widgets.HBox([_exemplos, _botao]), _editor, _saida]))
    _compilar()
except ImportError:
    show('<div class="status warnb">ipywidgets não está disponível — use <code>relatorio_compilacao(compilar(seu_codigo))</code>.</div>')
