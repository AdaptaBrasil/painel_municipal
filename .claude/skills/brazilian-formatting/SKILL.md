---
name: brazilian-formatting
description: Brazilian number formatting rules for Folha Municipal. Use when creating/changing any value displayed in the report (currency, percentage, units, IDH, climate scenarios) or when adding fields to *Report entities.
---

# Brazilian Number Formatting

Full reference: `.specs/business-rules/01-number-formatting.md`. Implementation: `CommonBusinessRules` in `backend/src/domain/entities.py`.

## Non-negotiable rules

1. pt-BR convention: `1.234,56` (dot = thousands, comma = decimal).
2. **Truncate** to 2 places, never round (`to_decimal_truncated`).
3. `None` → always the em dash `"—"` (except missing risk dimensions on pagina2, which stay `""`).
4. Formatting happens **only** in the domain's `*Report` wrapper — never in Jinja2 templates, JS or the frontend.

## Which formatter to use

| Situation | Function |
|---|---|
| Generic value with 2 places | `brazilian_formatted_value` |
| Omit `,00` (populations, years) | `brazilian_formatted_value_ignore_two_zeros` |
| Integer counts | `brazilian_formatted_value_integer` |
| Large currency (damages, aggregate GDP) | `brazilian_formatted_value_currency_short` → `R$ 2,00 Mi/Bi` |
| Climate scenarios (`_tend`, `_otim`, `_pes`) | `brazilian_formatted_signed_value` → `+1,23` / `−1,23` (U+2212) |

## Established suffixes

`km²`, `hab/km²`, `%`, `% do município`, `% das famílias pobres`, `anos`, `para cada 1.000 hab`, `para cada mil hab`, `por 100 mil hab`, `°C`, `mm`, `R$ X/hab` (these labels are report content and stay in Brazilian Portuguese). IDH gets a classification: ≥0.800 Muito Alto; 0.700–0.799 Alto; 0.550–0.699 Médio; <0.550 Baixo.

## When adding a new field

1. Add the `Optional` field to the entity.
2. Add the formatting rule to the wrapper's `formatted_data_dict`, reusing the formatters above.
3. Record the rule in `.specs/business-rules/01-number-formatting.md`.
4. If possible, cover it with a unit test (pure function — see `.claude/rules/testing.md`).
