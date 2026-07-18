// Página 6 — Saúde municipal (perfil epidemiológico, estrutura e recursos,
// políticas e programas, cobertura vacinal).
// Defaults gerados a partir do board Penpot "PÁGINA6"
// (id acb7058d-36c5-59f7-b731-6e5b089b9d5f), pixel-idênticos ao export.
//
// Itens com "id" são alimentados pelo backend: o id é o nome exato do
// atributo em MunicipalHealth (backend/src/domain/entities.py), e o valor
// injetado vem já formatado de MunicipalHealthReport.formatted_data_dict
// (ver o <script> de injeção no index.html). Itens sem "id" ainda não têm
// dado no backend e mantêm o valor estático do protótipo.
window.PAGE_DATA = {
  "tokens": {
    "colors": {
      "primary": "#354F9D",
      "panel": "#ABC837",
      "chip": "#D9D9D9",
      "border": "#6D797A",
      "onPrimary": "#FCFCFC",
      "surface": "#FFFFFF",
      "text": "#1E1E1E"
    }
  },
  "location": {
    "city": "Curitiba",
    "state": "Paraná"
  },
  "perfilEpidemiologico": {
    "title": "Perfil epidemiológico",
    "taxaIncidenciaLabel": "Taxa de incidência:",
    "incidencia": [
      {
        "id": "incid_arbo_2025",
        "label": "Arboviroses:",
        "valor": "28 por 100 mil hab"
      },
      {
        "id": "incid_lepto_2025",
        "label": "Leptospirose:",
        "valor": "8 por 100 mil hab"
      },
      {
        "id": "incid_hepatitea_2023",
        "label": "Hepatite A:",
        "valor": "5 por 100 mil hab"
      }
    ],
    "taxaInternacaoLabel": "Taxa de internação:",
    "internacao": [
      {
        "id": "inter_doenc_circ_2025",
        "label": "Doenças aparelho circulatório:",
        "valor": "10255 por 100 mil hab"
      },
      {
        "id": "intern_doenc_resp_2025",
        "label": "Doenças aparelho respiratório:",
        "valor": "8148 por 100 mil hab"
      },
      {
        "id": "intern_dda_2025",
        "label": "Monitoramento de diarreia aguda:",
        "valor": "4 por 100 mil hab"
      }
    ],
    "painelCalorLabel": "Painel de excesso de calor:"
  },
  "estruturaRecursos": {
    "title": "Estrutura e Recursos em Saúde",
    "itens": [
      {
        "label": "Estabelecimentos de saúde atendem SUS:",
        "valor": "45"
      },
      {
        "label": "Estabelecimentos de saúde não atendem SUS:",
        "valor": "15"
      },
      {
        "label": "Hospital (geral e especializado):",
        "valor": "0"
      },
      {
        "label": "Centro de saúde e UBS:",
        "valor": "26"
      },
      {
        "label": "UPA:",
        "valor": "2 por hab"
      },
      {
        "label": "Centro de atenção psicossocial:",
        "valor": "3 Caps"
      },
      {
        "label": "Centros especializados em reabilitação:",
        "valor": "0"
      },
      {
        "label": "Equipe multiprofissional:",
        "valor": "1"
      },
      {
        "label": "Equipe saúde bucal:",
        "valor": "11"
      },
      {
        "id": "leitos_1000_hab",
        "label": "Leitos:",
        "valor": "8 para cada 1000 hab"
      },
      {
        "id": "prof_saude_hab_2025",
        "label": "Profissionais de saúde:",
        "valor": "5 para cada 1000 hab"
      },
      {
        "id": "medicos_hab_2025",
        "label": "Médicos:",
        "valor": "3 por 1000 hab"
      },
      {
        "id": "despesas_saude",
        "label": "Despesas em saúde:",
        "valor": "R$5000/hab"
      }
    ]
  },
  "politicasProgramas": {
    "title": "Políticas e Programas de Saúde",
    "itens": [
      {
        "label": "Programa Academia da Saúde (PAS):",
        "valor": "3 polos"
      },
      {
        "label": "Programa Farmácia Popular do Brasil (PFPB):",
        "valor": "3.516 beneficiados"
      },
      {
        "label": "Programa Dignidade Menstrual (PDM):",
        "valor": "221 beneficiadas"
      },
      {
        "label": "Política Nacional de Saúde Integral da População Negra (PNSIPN):",
        "valor": "sem ações"
      }
    ],
    "planoAdaptaSusLabel": "Plano AdaptaSUS:"
  },
  "coberturaVacinal": {
    "title": "Cobertura Vacinal",
    "itens": [
      {
        "id": "cob_vac_geral",
        "label": "Geral:",
        "valor": "78"
      },
      {
        "id": "cob_vac_menor_2",
        "label": "Menores \n2 anos:",
        "valor": "88,7"
      },
      {
        "id": "cob_vac_influenza_novo",
        "label": "Influenza 60+:",
        "valor": "56"
      }
    ]
  }
};
