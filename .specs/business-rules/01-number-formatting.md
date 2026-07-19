# Business Rules — Brazilian Number Formatting

Source: `CommonBusinessRules` in `backend/src/domain/entities.py` and `NumberFormattingProcessing` in `backend/src/helpers/common/formatting/number_formatting_processing.py`.

## General principles

1. **Brazilian convention**: comma as decimal separator, dot as thousands separator (e.g. `1.234,56`).
2. **Truncation, not rounding**: values are truncated to 2 decimal places before formatting (`to_decimal_truncated`, precision=2).
3. **Missing value** (`None`): **always** render the em dash `"—"`.
4. All formatting happens **in the domain** (`*Report` wrappers), never in the template or frontend.

## Formatters

| Function | Rule | Example |
|---|---|---|
| `brazilian_formatted_value` | Truncates to 2 places and formats pt-BR | `1234.567` → `1.234,56` |
| `brazilian_formatted_value_ignore_two_zeros` | Same, but omits decimals when they are `,00` | `1234.00` → `1.234` |
| `brazilian_formatted_value_integer` | Converts to truncated integer and formats | `1234.9` → `1.234` |
| `brazilian_formatted_value_currency_short` | ≥ 1 bn → `R$ X,XX Bi`; ≥ 1 mn → `R$ X,XX Mi`; below → `R$` + full format | `2_000_000_000` → `R$ 2,00 Bi` |
| `brazilian_formatted_signed_value` | Explicit sign: `+` positive, `−` (minus sign U+2212) negative, `+0,00` for zero | `-1.23` → `−1,23` |

## Suffixes and units per indicator

### Municipal indicators (pagina3)
- `area` → `{value} km²`
- `renda_media`, `pib` → `R$ {value}`
- `densidade_urb` → `{integer} hab/km²`
- Percentages (`pop_urb_pct`, `pop_rural_pct`, `mulheres`, `pretos_pardos`, `pop_inf`, `pop_idosa`, `imigrantes`, `indigenas`, `quilombolas`, `alfabet`, `cob_vacinal`, `acesso_agua2`, `acesso_esgoto`, `acesso_energia`, `acesso_lixo`, `solic_refugio`, `tx_turismo`) → `{value}%`
- `bolsa_familia` → `{value}% das famílias pobres`
- `pop_urb_pessoas`, `pop_rural_pessoas`, `pop_fav`, `dom_semi_inadeq` → format without trailing decimal zeros
- `leito_hab`, `prof_hab` → `{value} para cada 1.000 hab`
- `escolaridade`, `expec_vida` → `{value} anos`
- `firjan`, `imig_regist` → plain formatted value

### IDH (HDI) classification
| Range | Label |
|---|---|
| ≥ 0.800 | `(Muito Alto)` |
| 0.700 – 0.799 | `(Alto)` |
| 0.550 – 0.699 | `(Médio)` |
| < 0.550 | `(Baixo)` |

Final format: `0,754 (Alto)`.

### Climate projections (pagina5)
- Scenario columns (suffixes `_tend`, `_otim`, `_pes`) use the **explicit sign** (`brazilian_formatted_signed_value`).
- Temperatures (`temp_med*`, `temp_max*`, `temp_min*`) → `{value} °C`
- Extreme rain and precipitation (`chuva_ext*`, `precip*`) → `{value} mm`
- Sea level (`nivel_mar`, `nivel_mar_tend`, `nivel_mar_30`, `nivel_mar_50`) → `{value} mm`
- Dry/rainy days → unitless value

### Resilience profile (pagina4)
- `veg_natural`, `agropec` → `{value}% do município`
- Disaster counts (`estiagem_incend`, `geohidro`, `tornad_vendav`, `obitos`, `desabrig`, `desaloj`, `escola_risco`, `eventos_geohidro`, `pessoas_area_risco_cemaden`) → formatted integer
- `danos_prej_tot` → short-scale currency (`R$ X,XX Mi`/`Bi`)

### Municipal health (pagina6)
- Incidences and hospitalizations (`incid_*`, `intern_*`, `inter_*`) → `{integer} por 100 mil hab`
- `leitos_1000_hab`, `prof_saude_hab_2025`, `medicos_hab_2025` → `{value with 2 decimal places} para cada mil hab` (float; values that truncate to zero collapse to a bare `0`)
- `despesas_saude` → `R${value}/hab`
- Facility/team counts (`atendem_ao_sus`, `nao_atendem_ao_sus`, `upa_26`, `caps_26`, `cer_26`, `e_multi_2026`, `saude_bucal_26`) → formatted integer (no decimals, no unit)
- `hospitais`, `centro_saude`: arrive as **text**; `"-"` (or empty) means missing → `—`; otherwise displayed as-is
- `pas_26` → `{integer} polos`; `pfpb_26` → `{integer} beneficiados`; `pdm_26` → `{integer} beneficiadas` (zero collapses to a bare `0`)
- `pnsipn_21`: string `Sim`/`Não` straight from the database, displayed as-is
- Vaccine coverage (`cob_vac_menor_2`, `cob_vac_influenza_novo`) → `{value}%`
- `cob_vac_geral`: may arrive as a **string in Brazilian format** (`"1.234,5"`); it must be normalized (strip thousands `.`, replace `,` with `.`) before formatting; if conversion fails, display the original value.

## Risk factors (pagina2)

- Rows are grouped by `risk_id`; each `detail` becomes a transposed column: `Ameaça`, `Exposição`, `Vulnerabilidade`, `Sensibilidade`, `Capacidade adaptativa`, with the associated color in `{detail}_color`.
- `current_value` and `future_value` also get formatted versions (`formatted_current_value`, `formatted_future_value`).
- Missing dimensions remain as the empty string `""` (blank cell, not em dash).

> Note: user-facing labels and unit suffixes (e.g. `para cada 1.000 hab`, `% do município`) are report content and stay in Brazilian Portuguese by design.
