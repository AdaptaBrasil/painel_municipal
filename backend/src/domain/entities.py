# backend/src/domain/entities.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from decimal import Decimal
import pandas as pd

from ..helpers.common.formatting.number_formatting_processing import NumberFormattingProcessing

class CommonBusinessRules(BaseModel):
    @staticmethod
    def brazilian_formatted_value(value: Optional[float | int], precision: int = 2) -> Optional[str]:
        if value is None:
            return "—"
        truncated_value = NumberFormattingProcessing.to_decimal_truncated(value, value_to_ignore=None, precision=precision)

        if isinstance(value, (float)):
            return NumberFormattingProcessing.format_number_brazilian(float(truncated_value), precision=precision)
        elif isinstance(value, (int)):
            return NumberFormattingProcessing.format_number_brazilian(int(truncated_value), precision=precision)

        return "—"
    
    @staticmethod
    def brazilian_formatted_value_ignore_two_zeros(value: Optional[float | int]) -> Optional[str]:
        if value is None:
            return "—"
        truncated_value = NumberFormattingProcessing.to_decimal_truncated(value, value_to_ignore=None, precision=2)
        
        if isinstance(value, (float)):
            return NumberFormattingProcessing.format_number_brazilian_ignore_two_zeros(float(truncated_value))
        elif isinstance(value, (int)):
            return NumberFormattingProcessing.format_number_brazilian_ignore_two_zeros(int(truncated_value))
        
        return "—"
    
    @staticmethod
    def brazilian_formatted_value_integer(value: Optional[float | int]) -> Optional[str]:
        if value is None:
            return "—"
        truncated_value = NumberFormattingProcessing.to_decimal_truncated(value, value_to_ignore=None, precision=2)
        
        if isinstance(value, (float, int)):
            return NumberFormattingProcessing.format_number_brazilian_ignore_two_zeros(int(truncated_value))

        return "—"

    @staticmethod
    def brazilian_formatted_value_currency_short(value: Optional[float | int]) -> Optional[str]:
        """
        Format a monetary value in short scale (Mi/Bi) with Brazilian conventions.

        >= 1.000.000.000: divides by 1 Bi, truncates to 2 decimal places -> 'R$ 2,00 Bi'
        >= 1.000.000:     divides by 1 Mi, truncates to 2 decimal places -> 'R$ 2,00 Mi'
        Smaller values fall back to the plain Brazilian currency format.
        """
        if value is None:
            return "—"

        abs_value = abs(value)
        if abs_value >= 1_000_000_000:
            scaled = Decimal(str(value)) / Decimal(1_000_000_000)
            suffix = "Bi"
        elif abs_value >= 1_000_000:
            scaled = Decimal(str(value)) / Decimal(1_000_000)
            suffix = "Mi"
        else:
            return f"R$ {CommonBusinessRules.brazilian_formatted_value(value)}"

        truncated_value = NumberFormattingProcessing.to_decimal_truncated(scaled, value_to_ignore=None, precision=2)
        formatted_value = NumberFormattingProcessing.format_number_brazilian(float(truncated_value))
        return f"R$ {formatted_value} {suffix}"

    @staticmethod
    def brazilian_formatted_signed_value(value: Optional[float | int]) -> Optional[str]:
        """
        Format a value with an explicit sign prefix using Brazilian conventions.

        > 0:   '+1,23'
        < 0:   '−1,23'
        == 0:  '=0,00' (values that truncate to 0,00 count as zero)
        None:  '—'
        """
        if value is None:
            return "—"

        truncated_value = NumberFormattingProcessing.to_decimal_truncated(value, value_to_ignore=None, precision=2)
        if truncated_value > 0:
            return f"+{CommonBusinessRules.brazilian_formatted_value(value)}"
        if truncated_value < 0:
            return f"−{CommonBusinessRules.brazilian_formatted_value(abs(value))}"
        return f"+{CommonBusinessRules.brazilian_formatted_value(abs(value))}"



class County(BaseModel):
    county_id: int
    geocode: int
    county: str
    state: str
    region: str
    display: Optional[str] = None
    
class RiskFactor(BaseModel):
    risk_id: Optional[int] = None
    detail_id: Optional[int] = None
    sep_id: Optional[int] = None
    county_id: Optional[int] = None
    legend_id: Optional[int] = None
    
    sep: Optional[str] = None
    risk: Optional[str] = None
    detail: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    
    level: Optional[int] = None
    year: Optional[str] = None
    value: Optional[float] = None
    color: Optional[str] = None
    current_value: Optional[float] = None
    current_value_color: Optional[str] = None
    future_value: Optional[float] = None
    future_color: Optional[str] = None
    imageurl: Optional[str] = None
    risk_url: Optional[str] = None

class RiskFactorReport(BaseModel):
    risk_factors: List[RiskFactor]
        
    @property
    def formatted_data_dict(self) -> List[Dict[str, Any]]:
        grouped_risks = {}
        
        for rf in self.risk_factors:
            if rf.risk_id not in grouped_risks:
                grouped_risks[rf.risk_id] = {
                    "county_id": rf.county_id,
                    "risk_id": rf.risk_id,
                    "sep": rf.sep,
                    "risk": rf.risk,
                    "county": rf.county,
                    "state": rf.state,
                    "color": rf.color,
                    "imageurl": rf.imageurl,
                    "risk_url": rf.risk_url,
                    "current_value": rf.current_value,
                    "current_value_color": rf.current_value_color,
                    "formatted_current_value": CommonBusinessRules.brazilian_formatted_value(rf.current_value),
                    
                    "future_value": rf.future_value,
                    "future_color": rf.future_color,
                    "formatted_future_value": CommonBusinessRules.brazilian_formatted_value(rf.future_value),
                    
                    "Ameaça": "",
                    "Exposição": "",
                    "Vulnerabilidade": "",
                    "Sensibilidade": "",
                    "Capacidade adaptativa": ""
                }
            
            if rf.detail:
                # If the detail is "capacidade adaptativa", we want to keep it as is, otherwise we can capitalize it
                # coluna_transposta = rf.detail.capitalize() if rf.detail.lower() == "capacidade adaptativa" else rf.detail
                
                grouped_risks[rf.risk_id][rf.detail] = rf.value
                grouped_risks[rf.risk_id][f"{rf.detail}_color"] = rf.color
                
        # Apply formatting to the specific columns after all values have been assigned
        for key, item in grouped_risks.items():
            for col in ["Ameaça", "Exposição", "Vulnerabilidade", "Sensibilidade", "Capacidade adaptativa"]:
                if col in item and item[col] is not None:
                    item[col] = CommonBusinessRules.brazilian_formatted_value(item[col])
                
        return list(grouped_risks.values())

    @property
    def formatted_data_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.formatted_data_dict)

class MunicipalIndicators(BaseModel):
    
    # Territorial fields
    county_id: Optional[int] = None
    area: Optional[float] = None
    regic_influencia: Optional[str] = None
    pop_urb_pessoas: Optional[float] = None # TODO: apply brazilian formatting to this field in the report
    pop_urb_pct: Optional[float] = None
    pop_rural_pessoas: Optional[float] = None
    pop_rural_pct: Optional[float] = None
    densidade_urb: Optional[float] = None
    pib: Optional[float] = None
    
    # Population characteristics fields
    mulheres: Optional[float] = None
    pretos_pardos: Optional[float] = None
    pop_inf: Optional[float] = None
    pop_idosa: Optional[float] = None
    indigenas: Optional[float] = None
    quilombolas: Optional[float] = None
    
    # Socioeconomic conditions
    ## IDH and related indicators
    idh_m: Optional[float] = None
    renda_media: Optional[float] = None
    escolaridade: Optional[float] = None
    expec_vida: Optional[float] = None
    
    ## Social programs
    firjan: Optional[float] = None
    bolsa_familia: Optional[float] = None
    alfabet: Optional[float] = None
    
    ## Infrastructure and services
    leito_hab: Optional[float] = None
    prof_hab: Optional[float] = None
    cob_vacinal: Optional[float] = None
    
    ## Vulnerable populations
    pop_fav: Optional[float] = None
    dom_semi_inadeq: Optional[float] = None
    
    ## Access to services
    acesso_agua2: Optional[float] = None
    acesso_esgoto: Optional[float] = None
    acesso_energia: Optional[float] = None
    acesso_lixo: Optional[float] = None
    
    # MOBILIDADE POPULATION
    imig_regist: Optional[int] = None
    solic_refugio: Optional[int] = None
    imigrantes: Optional[float] = None
    tx_turismo: Optional[float] = None
    

class MunicipalIndicatorsReport(BaseModel):
    municipal_indicators: MunicipalIndicators
    
    @property
    def formatted_data_dict(self) -> Dict[str, Any]:
        data = self.municipal_indicators.model_dump()
        for key, value in data.items():
            if value is None:
                data[key] = "—"
                continue
            if key == "area":
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)} km²"
            elif key in ["renda_media", "pib"]:
                data[key] = f"R$ {CommonBusinessRules.brazilian_formatted_value(value)}"
            elif key == "densidade_urb":
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value_integer(value)} hab/km²"
            elif key in ["pop_urb_pct", "pop_rural_pct", "mulheres", "pretos_pardos", "pop_inf", "pop_idosa", "imigrantes", "indigenas", "quilombolas", "alfabet", "cob_vacinal"]:
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)}%"
            elif key in ["bolsa_familia"]:
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)}% das famílias pobres" 
            elif key in ["firjan"]:
                data[key] = CommonBusinessRules.brazilian_formatted_value(value, precision=4)
            elif key in ["acesso_agua2", "acesso_esgoto", "acesso_energia", "acesso_lixo"]:
                data[key] = f'{CommonBusinessRules.brazilian_formatted_value(value)}%'
            elif key in ["pop_urb_pessoas", "pop_rural_pessoas"]:
                if not isinstance(value, (float, int)):
                    data[key] = "—"
                else:
                    data[key] = CommonBusinessRules.brazilian_formatted_value_ignore_two_zeros(value)
            elif key in ["leito_hab", "prof_hab"]:
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)} para cada 1.000 hab"
            elif key in ["escolaridade", "expec_vida"]:                
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value_ignore_two_zeros(value)} anos"
            elif key in ["pop_fav", "dom_semi_inadeq"]:
                data[key] = CommonBusinessRules.brazilian_formatted_value_ignore_two_zeros(value)
            elif key == "idh_m":
                if not isinstance(value, (float, int)):
                    data[key] = "—"
                elif value >= 0.800:
                    data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value, precision=3)} (Muito Alto)"
                elif 0.700 <= value < 0.800:
                    data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value, precision=3)} (Alto)"
                elif 0.550 <= value < 0.700:
                    data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value, precision=3)} (Médio)"
                else:
                    data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value, precision=3)} (Baixo)"
            
            elif key in ["imig_regist", "solic_refugio"]:
                data[key] = CommonBusinessRules.brazilian_formatted_value_integer(value)
            elif key in ["imigrantes", "tx_turismo"]:
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)}%"
            
            
        return data

    @property
    def formatted_data_df(self) -> pd.DataFrame:
        return pd.DataFrame([self.formatted_data_dict])


class ClimateProjection(BaseModel):
    geocode: Optional[int] = None
    nm_munic: Optional[str] = None
    county_id: Optional[int] = None
    
    temp_med: Optional[float] = None
    temp_med_tend: Optional[float] = None
    temp_med_otim: Optional[float] = None
    temp_med_pes: Optional[float] = None

    temp_max: Optional[float] = None
    temp_max_tend: Optional[float] = None
    temp_max_otim: Optional[float] = None
    temp_max_pes: Optional[float] = None

    temp_min: Optional[float] = None
    temp_min_otim: Optional[float] = None
    temp_min_tend: Optional[float] = None
    temp_min_pes: Optional[float] = None
    
    dias_secos: Optional[float] = None
    dias_secos_tend: Optional[float] = None
    dias_secos_otim: Optional[float] = None
    dias_secos_pes: Optional[float] = None

    dias_chuva: Optional[float] = None
    dias_chuva_tend: Optional[float] = None
    dias_chuva_otim: Optional[float] = None
    dias_chuva_pes: Optional[float] = None

    chuva_ext: Optional[float] = None
    chuva_ext_pes: Optional[float] = None
    chuva_ext_tend: Optional[float] = None
    chuva_ext_otim: Optional[float] = None

    precip: Optional[float] = None
    precip_tend: Optional[float] = None
    precip_otim: Optional[float] = None
    precip_pes: Optional[float] = None
    
    nivel_mar: Optional[float] = None
    nivel_mar_tend: Optional[float] = None
    nivel_mar_30: Optional[float] = None
    nivel_mar_50: Optional[float] = None
    
    # Correção 
    nivel_mar_otim: Optional[float] = None
    nivel_mar_pes: Optional[float] = None
    
class ClimateProjectionReport(BaseModel):
    climate_projection: ClimateProjection
    
    
    @property
    def pure_data_dict(self) -> Dict[str, Any]:
        return self.climate_projection.model_dump()
    @property
    def formatted_data_dict(self) -> Dict[str, Any]:
        data = self.climate_projection.model_dump()
        for key, value in data.items():
            if value is None:
                data[key] = "—"
                continue

            # Scenario columns (tendência observada, otimista, pessimista) carry an explicit sign
            if key.endswith(("_tend", "_otim", "_pes", "_30", "_50")):
                formatted_value = CommonBusinessRules.brazilian_formatted_signed_value(value)
            else:
                formatted_value = CommonBusinessRules.brazilian_formatted_value(value)

            if key in ["temp_med", "temp_med_tend", "temp_med_otim", "temp_med_pes",
                       "temp_max", "temp_max_tend", "temp_max_otim", "temp_max_pes",
                       "temp_min", "temp_min_tend", "temp_min_otim", "temp_min_pes"]:
                data[key] = f"{formatted_value} °C"
            elif key in ["dias_secos", "dias_secos_tend", "dias_secos_otim", "dias_secos_pes",
                         "dias_chuva", "dias_chuva_tend", "dias_chuva_otim", "dias_chuva_pes"]:
                data[key] = formatted_value
            elif key in ["chuva_ext", "chuva_ext_tend", "chuva_ext_otim", "chuva_ext_pes",
                         "precip", "precip_tend", "precip_otim", "precip_pes"]:
                data[key] = f"{formatted_value} mm"
            
            elif key in ["nivel_mar", "nivel_mar_tend"]:
                data[key] = f"{formatted_value} cm"
                
            elif key in ["nivel_mar_30"]:
                data["nivel_mar_otim"] = f"{formatted_value} cm"
                data[key] = f"{formatted_value} cm"
            elif key in ["nivel_mar_50"]:
                data["nivel_mar_pes"] = f"{formatted_value} cm"
                data[key] = f"{formatted_value} cm"

        return data

    @property
    def formatted_data_df(self) -> pd.DataFrame:
        return pd.DataFrame([self.formatted_data_dict])


class MunicipalResilienceProfile(BaseModel):
    # Identificação do município
    county_id: Optional[int] = None
    geocode: Optional[int] = None
    
    # Uso do solo
    bioma: Optional[str] = None
    veg_natural: Optional[float] = None
    agropec: Optional[float] = None
    ucs: Optional[str] = None
    ti: Optional[str] = None
    # TODO: Missing fields for : Uso e cobertura da terra
    
    # gestão municipal
    plano_saneam: Optional[str] = None
    plano_residuos: Optional[str] = None
    plano_drenagem: Optional[str] = None
    plano_transporte: Optional[str] = None
    plano_hab: Optional[str] = None
    plano_diretor: Optional[str] = None
    plano_rrd: Optional[str] = None
    plano_conting: Optional[str] = None
    cid_resilientes: Optional[str] = None
    
    # Desastres
    estiagem_incend: Optional[float] = None
    geohidro: Optional[float] = None
    tornad_vendav: Optional[float] = None
    obitos: Optional[float] = None
    desabrig: Optional[float] = None
    desaloj: Optional[float] = None
    danos_prej_tot: Optional[float] = None
    
    # Monitoramento de desastres (CEMADEN)
    escola_risco: Optional[float] = None
    eventos_geohidro: Optional[float] = None
    pessoas_area_risco_cemaden: Optional[float] = None
    
    # TODO: Missing fields for : Áreas de risco

class MunicipalResilienceProfileReport(BaseModel):
    municipal_resilience_profile: MunicipalResilienceProfile
    
    @property
    def formatted_data_dict(self) -> Dict[str, Any]:
        data = self.municipal_resilience_profile.model_dump()
        for key, value in data.items():
            if value is None:
                data[key] = "—"
                continue
            
            if key in ["veg_natural", "agropec"]:
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)}% do município"                
            elif key in ["estiagem_incend", "geohidro", "tornad_vendav", "obitos", "desabrig", "desaloj"]:
                data[key] = CommonBusinessRules.brazilian_formatted_value_integer(value)
            elif key in ["danos_prej_tot"]:
                data[key] = CommonBusinessRules.brazilian_formatted_value_currency_short(value)
            elif key in ["escola_risco", "eventos_geohidro", "pessoas_area_risco_cemaden"]:
                data[key] = CommonBusinessRules.brazilian_formatted_value_integer(value)
                
        return data

    @property
    def formatted_data_df(self) -> pd.DataFrame:
        return pd.DataFrame([self.formatted_data_dict])

class MunicipalHealth(BaseModel):
    county_id: Optional[int] = None
    geocode: Optional[int] = None
    
    # Perfil epidemiológico
    incid_arbo_2025: Optional[int] = None
    incid_lepto_2025: Optional[int] = None
    incid_hepatitea_2023: Optional[int] = None
    intern_dda_2025: Optional[int] = None
    
    inter_doenc_circ_2025: Optional[int] = None
    intern_doenc_resp_2025: Optional[int] = None
    
    leitos_1000_hab: Optional[int] = None
    prof_saude_hab_2025: Optional[int] = None
    medicos_hab_2025: Optional[int] = None
    
    despesas_saude: Optional[float] = None
    
    cob_vac_geral: Optional[str] = None
    cob_vac_menor_2: Optional[float] = None
    cob_vac_influenza: Optional[float] = None

class MunicipalHealthReport(BaseModel):
    municipal_health: MunicipalHealth
    
    @property
    def formatted_data_dict(self) -> Dict[str, Any]:
        data = self.municipal_health.model_dump()
        for key, value in data.items():
            if value is None:
                data[key] = "—"
                continue

            if key in ["incid_arbo_2025", "incid_lepto_2025", "incid_hepatitea_2023", "intern_dda_2025",
                       "inter_doenc_circ_2025", "intern_doenc_resp_2025"]:
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value_integer(value)} por 100 mil hab"
            elif key in ["leitos_1000_hab", "prof_saude_hab_2025", "medicos_hab_2025"]:
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value_integer(value)} para cada mil hab"
            elif key == "despesas_saude":
                data[key] = f"R${CommonBusinessRules.brazilian_formatted_value_ignore_two_zeros(value)}/hab"
            elif key in ["cob_vac_menor_2", "cob_vac_influenza"]:
                data[key] = f'{CommonBusinessRules.brazilian_formatted_value_ignore_two_zeros(value)}%'
            elif key == "cob_vac_geral":
                if isinstance(value, str):
                    normalized_value = value.replace(".", "").replace(",", ".")
                    try:
                        numeric_value = float(normalized_value)
                        data[key] = f'{CommonBusinessRules.brazilian_formatted_value_ignore_two_zeros(numeric_value)}%'
                    except ValueError:
                        data[key] = value
                else:
                    data[key] = f'{CommonBusinessRules.brazilian_formatted_value_ignore_two_zeros(value)}%'
                
        return data

    @property
    def formatted_data_df(self) -> pd.DataFrame:
        return pd.DataFrame([self.formatted_data_dict])

class ProjectInfo(BaseModel):
    name: str
    version: str
    description: str