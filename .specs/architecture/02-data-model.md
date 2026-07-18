# Data Model

## Data source

PostgreSQL database, schema **`painel_municipal`**. The application is **read-only**: all queries are parameterized `SELECT`s (asyncpg, `$1` placeholders). The universal join key is **`county_id`** (integer, > 0).

## Consumed tables

| Table | Repository | Entity | Feeds |
|---|---|---|---|
| `adapta_data` | `CountyRepository` | `County` | Municipality list, cover (pagina0), headers |
| `quatro_pg_2` | `RiskFactorRepository` | `RiskFactor` (list) | pagina2 — risk factors |
| `pg_3` | `MunicipalIndicatorsRepository` | `MunicipalIndicators` | pagina3 — municipal indicators |
| `pq_4` | `MunicipalResilienceProfileRepository` | `MunicipalResilienceProfile` | pagina4 — resilience profile |
| `pag5_climaticos_observados_cenarios` | `ClimateProjectionRepository` | `ClimateProjection` | pagina5 — climate projections (and `geocode` for every page's file name) |
| `pg_6` | `MunicipalHealthRepository` | `MunicipalHealth` | pagina6 — municipal health |

## Entities (field summary)

### County
`county_id`, `geocode` (IBGE code), `county`, `state`, `region`, `display` (derived: `CONCAT(county, ' - ', state)`).

### RiskFactor
Granular rows per risk × detail. Key fields: `risk_id`, `detail_id`, `sep_id`, `county_id`, `sep`, `risk`, `detail` (dimension: Ameaça, Exposição, Vulnerabilidade, Sensibilidade, Capacidade adaptativa), `level`, `year`, `value`, `color`, `current_value`/`current_value_color`, `future_value`/`future_color`, `imageurl`, `risk_url`.
Query ordering: `current_value desc, sep_id, risk, detail`.

### MunicipalIndicators
Groups: territory (`area`, `regic_influencia`, `pop_urb_*`, `pop_rural_*`, `densidade_urb`, `pib`); population characteristics (`mulheres`, `pretos_pardos`, `pop_inf`, `pop_idosa`, `indigenas`, `quilombolas`); socioeconomics (`idh_m`, `renda_media`, `escolaridade`, `expec_vida`, `firjan`, `bolsa_familia`, `alfabet`); infrastructure/services (`leito_hab`, `prof_hab`, `cob_vacinal`, `pop_fav`, `dom_semi_inadeq`, `acesso_agua2`, `acesso_esgoto`, `acesso_energia`, `acesso_lixo`); mobility (`imig_regist`, `solic_refugio`, `imigrantes`, `tx_turismo`).

### MunicipalResilienceProfile
Land use (`bioma`, `veg_natural`, `agropec`, `ucs`, `ti`); municipal management (plans `plano_saneam`, `plano_residuos`, `plano_drenagem`, `plano_transporte`, `plano_hab`, `plano_diretor`, `plano_rrd`, `plano_conting`, `cid_resilientes` — textual values such as "possui"/"não possui"); disasters (`estiagem_incend`, `geohidro`, `tornad_vendav`, `obitos`, `desabrig`, `desaloj`, `danos_prej_tot`); CEMADEN monitoring (`escola_risco`, `eventos_geohidro`, `pessoas_area_risco_cemaden`).

### ClimateProjection
For each climate variable — `temp_med`, `temp_max`, `temp_min`, `dias_secos`, `dias_chuva`, `chuva_ext`, `precip` — there are 4 columns: observed value, `*_tend` (observed trend), `*_otim` (optimistic scenario) and `*_pes` (pessimistic scenario). Sea level: `nivel_mar`, `nivel_mar_tend`, `nivel_mar_30`, `nivel_mar_50`. Also carries `geocode` and `nm_munic`.

### MunicipalHealth
Epidemiological profile (`incid_arbo_2025`, `incid_lepto_2025`, `incid_hepatitea_2023`, `intern_dda_2025`, `inter_doenc_circ_2025`, `intern_doenc_resp_2025`); resources (`leitos_1000_hab`, `prof_saude_hab_2025`, `medicos_hab_2025`, `despesas_saude`); vaccine coverage (`cob_vac_geral` — may arrive as a string in Brazilian format —, `cob_vac_menor_2`, `cob_vac_influenza_novo`).

## Invariants and conventions

1. **All indicator fields are optional** (`Optional`); a missing value is always rendered as the em dash `"—"` (never `null`, `None`, `0` or empty).
2. Every entity has a `*Report` wrapper exposing:
   - `formatted_data_dict` — data ready for the template (Brazilian formatting applied);
   - `formatted_data_df` — same content as a `pandas.DataFrame`;
   - `ClimateProjectionReport` additionally exposes `pure_data_dict` (unformatted — used to extract `geocode`).
3. Templates receive **formatted data only**; no number formatting happens in JS or Jinja2.
4. `RiskFactorReport.formatted_data_dict` **transposes** the rows: it groups by `risk_id` and turns each `detail` into a column (`Ameaça`, `Exposição`, `Vulnerabilidade`, `Sensibilidade`, `Capacidade adaptativa`), with the matching color in `{detail}_color`.
