<<<<<<< HEAD
# config_rnds.py

import os

# URL base FHIR da RNDS (ajuste para o ambiente de homologação que você receber)
RNDS_BASE_URL = os.getenv("RNDS_BASE_URL", "https://rnds-fhir.saude.gov.br")  # [web:25]

# Credenciais (apenas placeholders por enquanto)
RNDS_CLIENT_ID = os.getenv("RNDS_CLIENT_ID", "")
RNDS_CLIENT_SECRET = os.getenv("RNDS_CLIENT_SECRET", "")
RNDS_SCOPE = os.getenv("RNDS_SCOPE", "openid profile")

# CNES da unidade (substituir pelo real)
=======
# config_rnds.py

import os

# URL base FHIR da RNDS (ajuste para o ambiente de homologação que você receber)
RNDS_BASE_URL = os.getenv("RNDS_BASE_URL", "https://rnds-fhir.saude.gov.br")  # [web:25]

# Credenciais (apenas placeholders por enquanto)
RNDS_CLIENT_ID = os.getenv("RNDS_CLIENT_ID", "")
RNDS_CLIENT_SECRET = os.getenv("RNDS_CLIENT_SECRET", "")
RNDS_SCOPE = os.getenv("RNDS_SCOPE", "openid profile")

# CNES da unidade (substituir pelo real)
>>>>>>> a9bb5b2 (fix: corrige entrada do backend e dependências para deploy na Vercel)
CNES_UNIDADE_PADRAO = os.getenv("CNES_UNIDADE_PADRAO", "0000000")