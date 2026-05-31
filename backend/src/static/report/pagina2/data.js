// Página 2 — Painel Adapta Cidades
// Defaults espelham exatamente o board Penpot "PÁGINA 2 v3"
// (id 8ef3c28e-73bc-5f97-acaf-eb5da6b054e8).
window.PAGE_DATA = {
  tokens: {
    colors: {
      primary: '#354F9D',        // barra de títulos, coluna LINK, header da flor de risco
      background: '#F2F2F2',     // fundo do board
      headerBox: '#D9D9D9',      // caixa do nome do município e coluna RISCO
      onSurface: '#1E1E1E',
      onPrimary: '#FCFCFC',
      // headers de coluna (barra de títulos)
      colAmeaca: '#05A1A7',
      colExposicao: '#FAD075',
      colVulnerabilidade: '#ABC837',
      // faixas semânticas de risco
      riskVeryHigh: '#F40000',
      riskHigh: '#FC8402',
      riskMedium: '#FFCD00',
      riskLow: '#AADE00',
      riskVeryLow: '#06C351',
    },
  },

  location: { city: 'Curitiba', state: 'Paraná' },

  header: {
    barraTitulos: {
      risco: 'RISCO',
      link: 'LINK',
      tempoAtual: 'TEMPO',          tempoAtualL2: 'ATUAL',
      futuro2050: '2050',
      ameaca: 'AMEAÇA',
      exposicao: 'EXPOSIÇÃO',
      vulnerabilidade: 'VULNERABILIDADE',
      sensibilidade: 'SENSIBILIDADE',
      capacidadeAdaptativa: 'CAPACIDADE', capacidadeAdaptativaL2: 'ADAPTATIVA',
    },
  },

  rows: [
    { name: 'Estresse Hídrico',                       tempoAtual: 'Muito Alto',  futuro2050: 'Muito Alto',  ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Deslizamento',                           tempoAtual: 'Alto',        futuro2050: 'Alto',        ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Nível do Mar',                           tempoAtual: 'Muito Baixo', futuro2050: 'Muito Baixo', ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Malária',                                tempoAtual: 'Médio',       futuro2050: 'Médio',       ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Inundação',                              tempoAtual: 'Médio',       futuro2050: 'Médio',       ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Disponibilidade',                        tempoAtual: 'Médio',       futuro2050: 'Médio',       ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Alagamentos',                            tempoAtual: 'Médio',       futuro2050: 'Médio',       ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Arborviroses dengue, zika, chikungunya', tempoAtual: 'Médio',       futuro2050: 'Médio',       ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Leishmaniose',                           tempoAtual: 'Médio',       futuro2050: 'Médio',       ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Erosão',                                 tempoAtual: 'Médio',       futuro2050: 'Médio',       ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Acesso',                                 tempoAtual: 'Médio',       futuro2050: 'Médio',       ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
    { name: 'Enxurrada',                              tempoAtual: 'Médio',       futuro2050: 'Médio',       ameaca: '0,70', exposicao: '0,70', vulnerabilidade: '0,70', sensibilidade: '0,70', capacidadeAdaptativa: '0,70' },
  ],

  legendaTitle: 'Legenda',
  legend: [
    { label: 'Muito alto',  range: '0,80 a 1,00' },
    { label: 'Alto',        range: '0,60 a 0,79' },
    { label: 'Médio',       range: '0,40 a 0,59' },
    { label: 'Baixo',       range: '0,20 a 0,39' },
    { label: 'Muito baixo', range: '0,00 a 0,19' },
  ],

  florDeRisco: {
    title: 'flor de risco',
    petalLabels: {
      center: 'risco',
      hazard: 'Perigo/ameaça',
      vulnerability: 'vulnerabilidade',
      exposure: 'Exposição',
      sensitivity: 'Sensibilidade + capacidade adaptativa',
    },
  },
};
