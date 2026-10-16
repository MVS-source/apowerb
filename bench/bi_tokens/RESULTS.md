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
| main_chat_spec *(échec connu)* | 1 | 3 | 44 | 20 641 | 63 733 | – |

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


## D4 — gros CSV lu en en-tête + 20 lignes + nombre de lignes (agents BI)

Avant `d1` (695afa2) → après `d4` (dd43c4d)

| Scénario | Appels | Outils | 1er appel (tok) | Total avant | Total après | Δ | Qualité |
|---|---|---|---|---|---|---|---|
| creation | 5→5 | 26→26 | 13 916→13 916 | 88 515 | 88 515 | +0.0 % | ✅ |
| dashboard_chat | 5→5 | 26→26 | 13 959→13 959 | 135 407 | 135 407 | +0.0 % | ✅ |
| forecast | 4→4 | 26→26 | 13 906→13 906 | 96 159 | 61 164 | -36.4 % | ✅ |
| multi_turn | 10→10 | 26→26 | 13 916→13 916 | 254 982 | 254 982 | +0.0 % | ✅ |
| question | 3→3 | 26→26 | 13 959→13 959 | 65 765 | 65 765 | +0.0 % | ✅ |
| question_targeted *(estim.)* | 3→3 | 26→26 | 13 959→13 959 | 51 853 | 51 853 | +0.0 % | ✅ |

## D5 — `group_by` dans tool_bi_query_dashboard

Avant `d4` (dd43c4d) → après `d5` (4e4fe32)

| Scénario | Appels | Outils | 1er appel (tok) | Total avant | Total après | Δ | Qualité |
|---|---|---|---|---|---|---|---|
| creation | 5→5 | 26→26 | 13 916→13 988 | 88 515 | 88 875 | +0.4 % | ✅ |
| dashboard_chat | 5→5 | 26→26 | 13 959→14 031 | 135 407 | 135 767 | +0.3 % | ✅ |
| forecast | 4→4 | 26→26 | 13 906→13 978 | 61 164 | 61 452 | +0.5 % | ✅ |
| multi_turn | 10→10 | 26→26 | 13 916→13 988 | 254 982 | 255 702 | +0.3 % | ✅ |
| question | 3→3 | 26→26 | 13 959→14 031 | 65 765 | 65 981 | +0.3 % | ✅ |
| question_grouped *(estim.)* | 3 | 26 | 14 031 | – | 51 094 | nouveau | ✅ |
| question_targeted *(estim.)* | 3→3 | 26→26 | 13 959→14 031 | 51 853 | 52 069 | +0.4 % | ✅ |

Coût fixe : +72 tokens par appel (déclaration). Gain si le modèle s'en sert : question 65 981 → 51 094 (−22,6 %), mais seulement −1,9 % face à `component_ids` par canal (question_targeted) : à juger au mode réel.
