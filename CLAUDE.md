# Vida de Garden — notas para o Claude Code

Jogo de gestão em navegador: o jogador escolhe ser **dono de garden** (loja de plantas) ou **produtor** (viveiro/estufa). Corre em tempo real (relógio verdadeiro), guarda a partida no `localStorage` e calcula o que aconteceu enquanto o jogador esteve fora.

O dono do projeto (Luiz) não programa: cria a arte no ChatGPT e pede as mudanças em português. Responde em português, de forma direta e visual, e diz com franqueza quando algo não vai ficar bem.

## Estrutura

```
jogo/
  index.html        o jogo inteiro (HTML + CSS + JS num só ficheiro, sem build)
  sprites/          imagens usadas pelo jogo (PNG/JPG), carregadas por caminho relativo
arte-original/      imagens originais do ChatGPT, antes de recortar (para voltar a recortar)
ferramentas/        scripts Python usados para recortar a arte (PIL + numpy + scipy)
```

Para testar: servir a pasta `jogo/` (ex.: `python3 -m http.server` dentro de `jogo/`) e abrir no navegador. Também funciona por `file://`.

Até agora estava publicado como artefacto do claude.ai (https://claude.ai/artifact/HDqGXWfS9qfCDyHB5wRpjF). O próximo passo previsto é pôr num repositório git e publicar no GitHub Pages ou no Netlify.

## Como o código está organizado (dentro de `index.html`)

O script é um único bloco `{ ... }`. Secções, por ordem:

1. **Dados**: `SP` (6 espécies: petunia, lavanda, suculenta, orquidea, monstera, oliveira, com dias de crescimento `g`, preço grossista `ws`, secagem `dry` e procura por estação `pk`), `SUP` (fornecedores), `STAFF` (cargos e salários), constantes (`GOAL=1500`, `KEY='vida-garden-5'` = chave do save).
2. **Sprites de lado (SVG)**: `spr()` desenha as plantas antigas em SVG. Só se usa nos cartões e painéis; no mapa usam-se as imagens novas.
3. **Mundo e pessoas**: geometria, rotas e "walkers" (bonecos).
   - `VS` é o estado visual, que não é guardado: bonecos, trabalhos em fila (`jobs`), "fantasmas" de plantas a ser levadas e partículas.
   - `S` é o estado do jogo, que é guardado: dinheiro, plantas, encomendas, equipa, banco, alertas, etc.
   - Cada boneco segue um `script` de passos `{go}`, `{wait}`, `{fn}` e `{queue}`.
4. **Desenho (canvas)**: vista de cima inclinada.
   - O mundo usa coordenadas `x,y` e o ecrã é `Y(y,z)=OY+y*K-z` (`K=.72`, `OY=64`, largura lógica `SW=400`).
   - `drawWorld(cv,D)` desenha o mapa: fundo em cache, depois objetos ordenados por `y` (profundidade).
5. **Simulação em tempo real**:
   - `realT()` = horas desde `S.base` (meia-noite local do dia em que o jogo começou).
   - `stepWorld()` faz avançar plantas, equipa, encomendas e clientes. `rollover()` corre à meia-noite: renda, salários e prestações do banco.
   - `catchUp()` simula o tempo em que o jogo esteve fechado (no máximo 14 dias) e gera o resumo "Enquanto estiveste fora".
   - `checkAlerts()` / `notify()` criam os avisos da equipa (o sino).
   - `restock()` (reposição automática no garden) e `autoDeliver()` (entregas automáticas no produtor) funcionam mesmo com o jogador ausente.
6. **Jogo e interface**: `newGame`, `act(a,arg)` (todas as ações dos botões passam por aqui, através de `data-act`/`data-arg`), painéis (`panel()`), folhas (`sheet()`), HUD, banco (`score()`, `limit()`, `payLoans()`).

## Níveis e cenários desenhados

- `S.rows` é o tamanho do edifício. Com `rows===2`, o jogo usa os **cenários desenhados** (`LV1ON=true`):
  - produtor: `LVS.prod`, imagem `sprites/p1n_bg.jpg` (viveiro rústico com 3 bancadas);
  - garden: `LVS.garden`, imagem `sprites/g2_bg.jpg` (loja de bairro com 3 mesas).
- Cada cenário define, em **píxeis da imagem original (1199×1312)**:
  - `B`: as 3 mesas/bancadas como quadriláteros `[trás-esq, trás-dir, frente-esq, frente-dir, y-trás, y-frente]`. Cada uma leva 8 vasos (2×4), calculados em `lv1Pot(i)`.
  - `C`: os corredores verticais por onde os bonecos andam. `FY` é a faixa horizontal à frente das mesas, que liga os corredores.
  - `G`: o x da porta/portão. No garden, `SY` é o passeio (rota `'S'`).
  - `sign`: a posição do texto ABERTO/FECHADO. `own`, `pay`, `reg`: dono/caixa, fila e registo.
- `geo(rows)` monta os pontos de interesse (`PT`, `HOMES`) e `route(w,g)` calcula o caminho: corredor → faixa da frente → outro corredor.
- Com `rows>2` (depois de "Ampliar"), o jogo volta ao desenho antigo feito em código, até haver arte para os níveis 2 e 3.

**Para acrescentar um cenário novo:** pôr a imagem vazia em `sprites/`, registá-la em `ASSET`, medir `B`, `C`, `FY` e `G` sobre a imagem (uma grelha de 50 px ajuda) e criar uma entrada em `LVS`.

## Arte

- **Plantas**: `sprites/pl_<especie>_<fase>.png` (fases 0 = muda, 1 = a crescer, 2 = pronta), mais `_s` (versão doente, dessaturada) e `pl_vazio.png`. `PLM` tem `[largura, altura, âncoraX, âncoraY]`; a âncora é o fundo do vaso. Recortadas com `ferramentas/recortar_plantas.py`.
- **Jardineiro**: marioneta de recortes (`front_*`, `back_*`, `side_*` em `sprites/`), animada em `drawRig()`: pernas e braços rodam, de lado usa membros escurecidos (`_dk`), para a esquerda espelha a vista de lado. É usado nos jardineiros (garden) e nos trabalhadores (produtor).
- **Os outros bonecos** (dono, caixa, vendedores, clientes, estafeta) ainda são desenhados em código, em `person()`, no estilo antigo. **Destoam dos cenários novos: é a melhoria visual mais urgente.**
- Os `p1_*.png` são de uma tentativa anterior do nível 1 e já não se usam (ainda estão em `ASSET`). Podem ser removidos.

### Como a arte é feita
Cria-se no ChatGPT, sempre na mesma conversa, para o estilo ficar igual: ilustração desenhada à mão, luz de cima à esquerda, câmara de frente e de cima a cerca de 45°, **sem ponto de fuga** e sem telhado. Para cenários, pede-se primeiro a cena cheia (para aprovar) e depois "a mesma imagem com as mesas vazias". Para objetos e bonecos, pede-se uma folha de peças separadas em fundo branco liso.

## O que falta (por ordem de prioridade combinada)

1. Bonecos no estilo novo: jardineiro, dono, caixa, vendedor e 3 a 5 clientes (marioneta, como o jardineiro).
2. Loja nível 1 (banca de rua), para a loja atual passar a ser o nível 2.
3. Estufa nível 2 (estufa de túnel) e nível 3 (estufa grande com corredores, armazém e vila à volta).
4. Carrinha do produtor como imagem separada, para voltar a arrancar nas entregas.
5. Publicar num site próprio (GitHub Pages ou Netlify) e transformar em PWA (ícone para instalar no telemóvel).
6. Backend (ex.: Supabase): contas, gravação na nuvem, jogadores garden ↔ produtor a negociar entre si, ranking.

## Cuidados

- O save tem versão (`KEY`). Ao mudar a estrutura de `S`, mudar a chave ou migrar, senão as partidas antigas partem.
- Tudo é em tempo real. Para testar rápido, `lamAt` já tem um gancho `if(window.FAST)return 900;`, que só atua se uma cópia de teste definir `window.FAST=1` antes do script. Na versão publicada não está definido.
- Testar sempre num ecrã de telemóvel (390×844): o jogo é pensado primeiro para telemóvel.
