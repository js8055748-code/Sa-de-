# api/rnds_client.py

from typing import Dict, Any, Optional

import config_rnds


class RNDSClient:
    """
    Cliente para comunicação com a RNDS (versão de teste/mocked).

    Neste momento, NÃO chamamos nenhum endpoint real.
    Em vez disso, retornamos um Bundle FHIR fictício para testarmos a
    rota /api/indicadores/unidade sem depender da RNDS real.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config_rnds.RNDS_BASE_URL

    def buscar_encounters_por_cnes_periodo(
        self,
        cnes: str,
        data_inicio: str,
        data_fim: str
    ) -> Dict[str, Any]:
        """
        Em vez de chamar a RNDS, retorna um Bundle FHIR de exemplo.

        Assim evitamos erros de JSONDecodeError enquanto a integração real
        (URL, autenticação, filtros) não está configurada.
        """
        # Bundle FHIR fictício com 3 Encounter e 2 pacientes distintos
        bundle_exemplo = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 3,
            "entry": [
                {
                    "resource": {
                        "resourceType": "Encounter",
                        "id": "enc-1",
                        "subject": {
                            "reference": "Patient/pac-1"
                        }
                    }
                },
                {
                    "resource": {
                        "resourceType": "Encounter",
                        "id": "enc-2",
                        "subject": {
                            "reference": "Patient/pac-2"
                        }
                    }
                },
                {
                    "resource": {
                        "resourceType": "Encounter",
                        "id": "enc-3",
                        "subject": {
                            "reference": "Patient/pac-1"
                        }
                    }
                },
            ]
        }
        return bundle_exemplo