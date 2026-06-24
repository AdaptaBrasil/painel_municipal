# backend/src/domain/entities.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd

from ..helpers.common.formatting.number_formatting_processing import NumberFormattingProcessing

class CommonBusinessRules(BaseModel):
    @staticmethod
    def brazilian_formatted_value(value: Optional[float | int]) -> Optional[str]:
        if value is None:
            return "—"
        truncated_value = NumberFormattingProcessing.to_decimal_truncated(value, value_to_ignore=None, precision=2)
        
        if isinstance(value, (float)):
            return NumberFormattingProcessing.format_number_brazilian(float(truncated_value))
        elif isinstance(value, (int)):
            return NumberFormattingProcessing.format_number_brazilian(int(truncated_value))
        
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

class County(BaseModel):
    county_id: int
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
    imigrantes: Optional[float] = None
    indigenas: Optional[float] = None
    quilombolas: Optional[float] = None
    
    # Socioeconomic conditions
    ## IDH and related indicators
    idh: Optional[float] = None
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

class MunicipalIndicatorsReport(BaseModel):
    municipal_indicators: MunicipalIndicators
    
    @property
    def formatted_data_dict(self) -> Dict[str, Any]:
        data = self.municipal_indicators.dict()
        for key, value in data.items():
            if value is None:
                data[key] = "—"
                continue
            if key == "area":
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)} km²"
            elif key in ["renda_media", "pib"]:
                data[key] = f"R$ {CommonBusinessRules.brazilian_formatted_value(value)}"
            elif key == "densidade_urb":
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)} hab/km²"
            elif key in ["pop_urb_pct", "pop_rural_pct", "mulheres", "pretos_pardos", "pop_inf", "pop_idosa", "imigrantes", "indigenas", "quilombolas", "alfabet", "cob_vacinal"]:
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)}%"
            elif key in ["bolsa_familia"]:
                data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)}% das famílias pobres" 
            elif key in ["firjan", "acesso_agua2", "acesso_esgoto", "acesso_energia", "acesso_lixo"]:
                data[key] = CommonBusinessRules.brazilian_formatted_value(value)
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
            elif key == "idh":
                if not isinstance(value, (float, int)):
                    data[key] = "—"
                elif value >= 0.800:
                    data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)} (Muito Alto)"
                elif 0.700 <= value < 0.800:
                    data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)} (Alto)"
                elif 0.550 <= value < 0.700:
                    data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)} (Médio)"
                else:
                    data[key] = f"{CommonBusinessRules.brazilian_formatted_value(value)} (Baixo)"
                
        return data

    @property
    def formatted_data_df(self) -> pd.DataFrame:
        return pd.DataFrame([self.formatted_data_dict])

class ProjectInfo(BaseModel):
    name: str
    version: str
    description: str