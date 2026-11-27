# Vida de Garden — notas para o Claude Code

Jogo de navegador, pensado para telemóvel **deitado**. O jogador controla um jardineiro numa rua vista de cima:
- no viveiro, do outro lado da estrada, semeia, rega, trata pragas e colhe;
- na loja, põe as plantas nas mesas e cobra na caixa.

A gestão (equipa, preços, fornecedor, banco, horário, expansão e avisos) abre no botão **Gestão**. O jogo corre com o relógio real, guarda no `localStorage` e mostra "Enquanto estiveste fora" quando o jogador volta.

O dono do projeto (Luiz) não programa: cria a arte no ChatGPT e pede as mudanças em português. Responde em português, de forma curta e visual, e diz com franqueza quando algo não vai ficar bem.

## Pastas

```
jogo/           O JOGO ATUAL. index.html (HTML+CSS+JS num ficheiro, sem build) + sprites/
jogo-antigo/    versão anterior (gestão vista de cima, sem andar). Só serve de referência para regras
arte-original/  imagens do ChatGPT antes de recortar
ferramentas/    scripts Python (PIL, numpy, scipy) que recortam a arte
```

Para testar, corre `python3 -m http.server` dentro de `jogo/` e abre o endereço no navegador. Também funciona por `file://`.

Mais tarde pôr em git e publicar no GitHub Pages ou no Netlify, para outras pessoas jogarem.

## Ecrã deitado (importante)

A app do Claude e muitos telemóveis têm a rotação bloqueada. Por isso o jogo roda-se a si mesmo:
- `resize()`: se o ecrã estiver em pé num aparelho de toque, o `#game` leva `rotate(90deg)` e `W`/`H` ficam trocados. Lá dentro o jogo é sempre largo.
- `gp(e)` converte o toque do ecrã para coordenadas do jogo. Qualquer novo controlo por toque no canvas tem de usar `gp()`.
- Tudo o que é interface fica dentro de `#game`, para rodar junto. Não usar `vw`/`vh` nos elementos dentro do `#game`; usar `--gw`/`--gh`.
- A classe `body.land` aplica o layout de ecrã largo e baixo.

## Organização do script (um bloco `{ ... }`)

1. **plants**: `PLM` (tamanho e âncora de cada sprite), `pAt(sp,fase,x,yBase,rim)`.
2. **jardineiro**: marioneta de recortes (`RIG_META`, `drawRig`), usada só no jogador. Os outros bonecos (clientes, peões, equipa) são desenhados em código em `person()`. A equipa leva avental verde e nome por cima.
3. **data**:
   - `SP` com as 6 espécies: `t` = segundos a crescer, `price` = preço de referência, `seed` = custo da semente.
   - Estado `G`, guardado em `localStorage['vdg-proto-1']`. Saves antigos são migrados com `Object.assign`.
4. **scenes**:
   - Rua: `OUT`, 48×34 tiles de 32. A loja tem a porta em `POUT` e o viveiro fica em x13–33, y25–33.
   - Interior da loja: `SHOP`, 24×14 tiles.
5. **static objects**:
   - Edifícios, árvores, candeeiros, bancadas do viveiro (`BENCHES`, `POTS`) e a placa ABERTO/FECHADO na porta.
   - O interior da loja é todo desenhado em código: `shopFloor`, `shopTable2`, `counter2` e `shopFront`.
   - Objetos ainda bloqueados (`G.tables`, `G.benches`) aparecem a tracejado com `lockedArea()`.
6. **actors**:
   - `walker()` cria um boneco e `moveAlong()` fá-lo seguir `path`.
   - Clientes da loja (`custs`) passam por estes estados: `go` → `look` → `toq` → `q` → `wait` → `leave`.
   - Ao olhar para a planta, o cliente compra ou não conforme `buyChance()`, que depende do preço.
   - Na fila, quem espera mais de 32 s desiste.
7. **interaction**:
   - `findNear()` decide o que o botão rosa faz conforme o sítio: semear, regar, tratar, colher, pôr à venda ou cobrar.
   - `doAct()` executa a ação.
8. **gestão** (`/* gestão ... */`):
   - Relógio: `nowH()`, `isOpen()` (de `G.open` a `G.close`) e `darkness()` (noite).
   - `newDay()` corre à meia-noite real: salários (`wages()`) e prestações (`payLoans()`).
   - `catchUp()` simula o tempo fora, até 8 h. O que pode acontecer está limitado (vendas e ciclos de cultivo) para a economia não disparar.
   - Equipa: `STAFF` + `crew` (bonecos) + `staffStep()`. Só trabalham com a loja aberta.
     - Ana, a caixa, cobra sozinha.
     - Rui, o repositor, leva o stock para as mesas vazias.
     - Marta, a jardineira, trata, rega, colhe e semeia, nesta ordem de prioridade.
   - Avisos: `notify(quem,chave,texto)` guarda em `G.alerts`, com pausa de 4 min por chave. `warnings()` gera os avisos automáticos.
   - Banco: `score()`, `rating()`, `limit()` e `loanTerms()`.
   - Janela de gestão: `gestHTML()` e `gestAct()`, com 6 separadores (`TABS`).
9. **loop**: em cada frame, `step()` faz andar o jogador, as plantas, a rua, a equipa, os avisos, os clientes e o `newDay`.

## Para testar sem esperar

- `window.DBG()` devolve `G`, `crew`, `custs`, `spawnCust`, `catchUp`, `newDay`, etc.
- `G.hOff` = horas a somar ao relógio real. Por exemplo, `DBG().G.hOff = 23 - new Date().getHours()` põe o jogo às 23 h.
- Para testar o "Enquanto estiveste fora": `G.lastT = Date.now() - 2*3600e3`, depois `DBG().catchUp()`.
- Para testar a meia-noite: `G.lastDay -= 1`, depois `DBG().newDay()`.

## Arte

- **Plantas**: `sprites/pl_<especie>_<0|1|2>.png`, recortadas com `ferramentas/recortar_plantas.py`. A âncora fica no fundo do vaso.
- **Jardineiro**: `sprites/front_*`, `back_*` e `side_*`, recortados com `ferramentas/recortar_boneco.py`.
- **Cenários**: a rua e a loja são desenhadas em código, de propósito. O Luiz preferiu assim à imagem do ChatGPT, porque as imagens geradas saem tortas e com perspetiva errada. Para trocar por arte, o melhor é pedir objetos soltos sobre fundo liso (mesa, balcão, prateleira) e recortá-los. Evitar cenários inteiros numa só imagem.

## Ideias que ficaram por fazer

- Modo **produtor** (receber encomendas de gardens), que existia no `jogo-antigo/`.
- Entrar no café e na padaria.
- Níveis de loja maiores, como no plano original: nível 2 moderno, nível 3 com estufa e corredores.
- Som. Multijogador ou ranking quando estiver online.
