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
