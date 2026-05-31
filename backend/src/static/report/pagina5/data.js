window.PAGE_DATA = {
  tokens: {
    colors: {
      bg: '#F2F2F2',
      surface: '#D9D9D9',
      surfaceInner: '#FFFFFF',
      border: '#6D797A',
      primary: '#354F9D',
      onPrimary: '#FCFCFC',
      text: '#1E1E1E',
      tableHeaderBg: '#6D797A',
      tableHeaderText: '#FFFFFF',
      mapMarker: '#42A5F5',
      tooltipBg: '#0F0F14',
      tooltipText: '#FFFFFF',
    },
  },

  location: { city: 'Curitiba', state: 'Paraná' },

  climaAtual: {
    title: 'Clima atual a',
    graficos: [
      { id: 'temp-media',  label: 'Temperatura média',           icon: './imgs/icone-temp-media.webp' },
      { id: 'temp-min',    label: 'Temperatura mínima',          icon: './imgs/icone-temp-min.webp' },
      { id: 'temp-max',    label: 'Temperatura máxima',          icon: './imgs/icone-temp-max.webp' },
      { id: 'dias-secos',  label: 'Dias secos consecutivos',     icon: './imgs/icone-dias-secos.webp' },
      { id: 'dias-chuva',  label: 'Dias de chuva',               icon: './imgs/icone-dias-chuva.webp' },
      { id: 'intensidade', label: 'Intensidade de precipitação', icon: './imgs/icone-intensidade-prec.webp' },
    ],
  },

  projecaoClima: {
    title: 'Projeção clima a',
    columns: {
      indicadorHeader: 'Indicador anual',
      passadoHeader: 'Passado',
      projecaoHeader: 'Projeção',
    },
    rows: [
      { icon: './imgs/icone-temp-media.webp',       label: 'Temperatura média',                            passado: '220',  projecao: '+1,50' },
      { icon: './imgs/icone-temp-min.webp',         label: 'Temperatura mínima',                           passado: '100',  projecao: '+1,20' },
      { icon: './imgs/icone-temp-max.webp',         label: 'Temperatura máxima',                           passado: '380',  projecao: '+2,20' },
      { icon: './imgs/icone-dias-secos.webp',       label: 'Números máximo de dias secos consecutivos',    passado: '12',   projecao: '+8' },
      { icon: './imgs/icone-dias-chuva.webp',       label: 'Números máximo de dias de chuva consecutivos', passado: '3',    projecao: '+1' },
      { icon: './imgs/icone-intensidade-prec.webp', label: 'Intensidade de precipitação',                  passado: '10mm', projecao: '+2mm' },
      { icon: './imgs/icone-chuvas-extremas.webp',  label: 'Chuvas extremas',                              passado: '70mm', projecao: '+10mm' },
    ],
  },

  temperaturaSuperficie: {
    title: 'Temperatura máxima da superfície a',
    mapImage: './imgs/mapa-curitiba.webp',
    tooltip: 'Curitiba, State of Paraná, Brazil',
  },
};
