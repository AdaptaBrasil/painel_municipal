// Página 0 FINAL — Capa "Fichas Municipais".
// Defaults pixel-idênticos ao export Penpot do board "PÁGINA-0-FINAL-22-07"
// (board id 6b684bd9-7100-582c-9c69-fbb9ea440efe).
// Futuramente estes valores virão de uma API; edite aqui para trocar de município.
window.PAGE_DATA = {
  "tokens": {
    "colors": {
      "primary": "#1AA9B1",
      "accent": "#E07055",
      "vulnerability": "#B3CD27",
      "exposure": "#FAC95E",
      "surface": "#FFFFFF",
      "background": "#D9D9D9",
      "onPrimary": "#FCFCFC"
    }
  },
  // Título da capa (duas linhas empilhadas; pesos distintos preservados no CSS).
  "header": {
    "titleLine1": "Fichas",
    "titleLine2": "Municipais"
  },
  // Município exibido no rodapé (cidade em peso 700, UF em peso 400).
  "location": {
    "city": "São José do Vale do Rio Preto",
    "state": "RJ"
  },
  // Marca ("Adapta" peso 400 + "Cidades" peso 900).
  "brand": {
    "namePrefix": "Adapta",
    "nameSuffix": "Cidades"
  },
  // Imagens de fundo (vazio = mantém o PNG referenciado no CSS, em ./imgs/).
  // Preencha com uma URL/caminho para trocar por município (ex.: dados da API).
  "images": {
    "quadradoAzul": "",
    "quadradoVerde": "",
    "mapaBrasil": "",
    "retanguloVermelho": "",
    "elipseVermelho": ""
  }
};
