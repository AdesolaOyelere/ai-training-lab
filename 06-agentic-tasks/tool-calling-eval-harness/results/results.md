# Tool-Calling Eval — Results

- Tasks: **8**
- Valid-call rate: **0.750**
- Tool-selection accuracy: **0.875**
- Arg match (given correct tool): **0.571**
- Full pass rate: **0.500**

| Task | valid | tool | args | fully | errors |
|---|---|---|---|---|---|
| `t1` | Y | Y | Y | Y | — |
| `t2` | Y | Y | Y | Y | — |
| `t3` | Y | Y | N | N | — |
| `t4` | Y | N | N | N | — |
| `t5` | N | Y | N | N | missing required arg: to_currency |
| `t6` | Y | Y | Y | Y | — |
| `t7` | Y | Y | Y | Y | — |
| `t8` | N | Y | N | N | wrong type for max_results: str |
