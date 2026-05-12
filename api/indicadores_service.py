# api/indicadores_service.py

from datetime import date
from typing import Dict, Any

from .rnds_client import RNDSClient
import config_rnds


def calcular_indicadores_unidade(
    cnes: str,
    data_inicio: str,
    data_fim: str
) -> Dict[str, Any]:
    """
    Calcula indicadores básicos de APS para uma unidade (CNES) em um período.

    Por enquanto:
      - total_atendimentos: número de Encounter retornados pela RNDS no período.
      - total_pacientes_atendidos: número de pacientes distintos nesses atendimentos.

    Depois vamos evoluir para indicadores APS específicos (hipertensão, diabetes, pré-natal etc.).
    """
    client = RNDSClient()

    # 1. Buscar dados clínicos relevantes na RNDS (por enquanto apenas Encounter)
    encounters_bundle = client.buscar_encounters_por_cnes_periodo(
        cnes=cnes,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    # 2. Extrair estatísticas básicas do bundle de Encounter
    total_atendimentos = _contar_encounters(encounters_bundle)
    total_pacientes_atendidos = _contar_pacientes_distintos(encounters_bundle)

    # 3. Montar objeto de retorno
    indicadores = {
        "cnes": cnes,
        "periodo_inicio": data_inicio,
        "periodo_fim": data_fim,
        "fonte": "RNDS-FHIR",
        "indicadores": {
            "total_atendimentos": {
                "descricao": "Total de atendimentos registrados na RNDS para a unidade no período",
                "valor": total_atendimentos
            },
            "total_pacientes_atendidos": {
                "descricao": "Total de pacientes distintos atendidos no período, segundo a RNDS",
                "valor": total_pacientes_atendidos
            },
            # Aqui depois adicionaremos indicadores APS específicos (ex.: hipertensos acompanhados, etc.)
        }
    }

    return indicadores


def _contar_encounters(bundle: Dict[str, Any]) -> int:
    """
    Conta quantos Encounter existem no bundle FHIR retornado pela RNDS.

    Espera um recurso do tipo Bundle com campo 'entry'.
    """
    if not bundle:
        return 0

    if bundle.get("resourceType") != "Bundle":
        return 0

    entries = bundle.get("entry", [])
    return len(entries)


def _contar_pacientes_distintos(bundle: Dict[str, Any]) -> int:
    """
    Conta o número de pacientes distintos (Patient) presentes nos Encounter do bundle.

    A estratégia aqui é:
      - Percorrer cada entry -> resource do tipo Encounter.
      - Verificar se há um campo 'subject' com 'reference' do tipo 'Patient/ID'.
      - Extrair o ID do Patient e colocar em um set para contagem distinta.

    Obs: a estrutura exata pode variar; vamos ajustar conforme a resposta real da RNDS.
    """
    if not bundle:
        return 0

    if bundle.get("resourceType") != "Bundle":
        return 0

    pacientes_ids = set()

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if not resource:
            continue

        if resource.get("resourceType") != "Encounter":
            continue

        subject = resource.get("subject")
        if not subject:
            continue

        reference = subject.get("reference")  # Ex.: "Patient/12345"
        if not reference:
            continue

        # Extrai apenas o ID do paciente após "Patient/"
        if reference.startswith("Patient/"):
            paciente_id = reference.split("Patient/")[-1]
        else:
            paciente_id = reference

        if paciente_id:
            pacientes_ids.add(paciente_id)

    return len(pacientes_ids)