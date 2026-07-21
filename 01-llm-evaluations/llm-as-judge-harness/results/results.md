# LLM-as-Judge (Debiased) — Results

- Pairs: **7**
- Model-A win rate: **0.429** · Model-B win rate: **0.143** · Tie rate: **0.429**
- Position-bias rate (verdict flipped when order swapped): **0.286**

| Pair | Winner | Consistent | Order1 | Order2 | Position bias |
|---|---|---|---|---|---|
| `q1` | a | Y | a | a | - |
| `q2` | b | Y | b | b | - |
| `q3` | a | Y | a | a | - |
| `q4` | a | Y | a | a | - |
| `q5` | tie | N | a | b | Y |
| `q6` | tie | N | a | b | Y |
| `q7` | tie | Y | tie | tie | - |
