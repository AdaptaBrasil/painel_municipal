// AdaptaBrasil — Página 4 (Diagnóstico municipal: desastres, gestão e uso do solo)
// Valores dinâmicos da tela. Futuramente alimentados por uma API.
// Os rótulos/títulos fixos permanecem estáticos no index.html.
window.PAGE_DATA = {
  tokens: {
    colors: {
      primary: '#354F9D',
      surface: '#FCFCFC',
      background: '#F2F2F2',
      onSurface: '#1E1E1E',
    },
  },

  location: { city: 'Curitiba', state: 'Paraná' },

  // Painel "Uso do solo"
  usoDoSolo: {
    bioma: 'Amazônia',
    vegetacaoNatural: '10% do município',
    agropecuaria: '30%',
    unidadesConservacao: '8% do município',
    terrasIndigenas: '0% do município',
  },

  // Painel "Gestão municipal" — ordem visual do protótipo.
  // status: 'possui' (POSSUI) | 'naoPossui' (NÃO POSSUI) | 'ausente' (AUSENTE)
  gestaoMunicipal: [
    { plano: 'Plano Diretor incluindo Proteção e Defesa Civil', status: 'possui' },
    { plano: 'Plano Diretor de Drenagem e Manejo de Águas Pluviais', status: 'possui' },
    { plano: 'Plano de Contingência', status: 'naoPossui' },
    { plano: 'Plano Municipal de Redução de Riscos', status: 'naoPossui' },
    { plano: 'Plano Municipal de Saneamento Básico', status: 'naoPossui' },
    { plano: 'Plano Municipal de Resíduos Sólidos', status: 'possui' },
    { plano: 'Plano Municipal de Habitação', status: 'naoPossui' },
    { plano: 'Plano Municipal de Transporte', status: 'ausente' },
  ],

  // Painel "Desastres"
  desastres: {
    historico: {
      estiagensIncendios: '20',
      geoHidrologicos: '8',
      tornadosVendavais: '5',
      obitos: '10',
      desabrigados: '20',
      desalojados: '200',
      danosPrejuizos: 'R$24,5 Mi',
    },
    cemaden: {
      escolasAreasRisco: '',
      pessoasAreasRisco: '',
      totalEventos: '',
    },
  },
};
