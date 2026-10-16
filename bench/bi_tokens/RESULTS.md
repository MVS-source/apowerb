# Banc tokens BI — résultats

Tokens d'entrée (tokenizer Gemini local, somme sur les appels du scénario), modèle scripté. Chaque levier ajoute sa ligne : `python bench/bi_tokens/replay.py --estimates --compare bench/bi_tokens/results/main.json`.

## Base : `main` (36ef99e, cœur v0.2.82)

| Scénario | Tours | Appels | Outils | 1er appel | Total | Mesuré DEV |
|---|---|---|---|---|---|---|
| creation | 1 | 5 | 36 | 17 070 | 104 285 | 98 144 |
| dashboard_chat | 2 | 5 | 36 | 17 113 | 151 177 | – |
| forecast | 1 | 4 | 36 | 17 060 | 108 775 | – |
| multi_turn | 3 | 10 | 36 | 17 070 | 286 522 | – |
| question | 1 | 3 | 36 | 17 113 | 75 227 | 71 617 |
| question_targeted *(estim.)* | 1 | 3 | 36 | 17 113 | 61 315 | 71 617 |

## D1 — outils de chat inutiles retirés des gabarits BI

Avant `main` (36ef99e) → après `d1` (695afa2)

| Scénario | Appels | Outils | 1er appel (tok) | Total avant | Total après | Δ | Qualité |
|---|---|---|---|---|---|---|---|
| creation | 5→5 | 36→26 | 17 070→13 916 | 104 285 | 88 515 | -15.1 % | ✅ |
| dashboard_chat | 5→5 | 36→26 | 17 113→13 959 | 151 177 | 135 407 | -10.4 % | ✅ |
| forecast | 4→4 | 36→26 | 17 060→13 906 | 108 775 | 96 159 | -11.6 % | ✅ |
| multi_turn | 10→10 | 36→26 | 17 070→13 916 | 286 522 | 254 982 | -11.0 % | ✅ |
| question | 3→3 | 36→26 | 17 113→13 959 | 75 227 | 65 765 | -12.6 % | ✅ |
| question_targeted *(estim.)* | 3→3 | 36→26 | 17 113→13 959 | 61 315 | 51 853 | -15.4 % | ✅ |
