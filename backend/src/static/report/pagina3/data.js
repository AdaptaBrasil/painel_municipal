// Página 3 — Relatório Municipal (versão atualizada)
// Defaults espelham o board Penpot "PÁGINA3"
// (id 51fd00f6-1549-5f73-b2cd-e1493455d680).
// Futuramente estes valores virão de uma API; edite aqui para alterar a página.
window.PAGE_DATA = {
  tokens: {
    colors: {
      primary: '#354F9D',     // headers de card (azul Penpot)
      surface: '#FCFCFC',     // campos de valor (off-white)
      background: '#F2F2F2',  // fundo do board
      headerBox: '#D9D9D9',   // caixa do nome do município e fundos de card
      onSurface: '#1E1E1E',   // texto principal
    },
  },

  location: { city: 'Curitiba', state: 'Paraná' },

  territorio: {
    area: '1.451.062 km²',
    regiaoInfluencia: 'Vilhena',
    densidadeUrbana: '2.000 hab/km²',
    pibPerCapita: 'R$5.000,00',
    idh: '0,772 (médio)',
    rendaMedia: 'R$2.036,34',
    escolaridade: '7 anos',
    expectativaVida: '68 anos',
  },

  populacao: {
    urbana: { pct: '74,76%', total: '11.709' },
    rural:  { pct: '25,24%', total: '3.954' },
    grupos: {
      mulheres: '50%',
      pretosPardos: '64%',
      infantil: '10%',
      idosa: '12%',
      imigrantes: '0,41%',
      indigenas: '0,5%',
      quilombolas: '0%',
    },
  },

  socioeconomicas: {
    firjan: {
      indice: '0.6951',
      bolsaFamiliaFamilias: '18,5%',
      alfabetizados: '90,5%',
    },
    saude: {
      leitos: '8 para cada 1000 hab',
      profissionais: '5 para cada 1000 hab',
      vacinal: '88,7%',
    },
    domicilios: {
      favelas: '5000',
      semiInadequados: '2000',
      semArborizacao: '5',
    },
    acessos: {
      agua: '69,9',
      esgoto: '2,4',
      energia: '98,3',
      residuos: '40,3',
    },
  },
};
