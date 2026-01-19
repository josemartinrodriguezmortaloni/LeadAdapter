import re

from domain.enums.seniority import Seniority


class SeniorityInferrer:
    """
    Infiere el nivel de seniority a partir del job_title.

    Estrategia de inferencia:
    - Busca patrones conocidos (CEO, Senior, Junior, etc.) en el título
    - Si encuentra un patrón, retorna el seniority correspondiente
    - Si NO encuentra patrones pero hay título, asume MID (nivel más común)
    - Si NO hay título (vacío/None), retorna UNKNOWN

    La distinción MID vs UNKNOWN es importante:
    - MID: Hay título pero sin indicadores de nivel → inferencia educada
    - UNKNOWN: No hay datos suficientes → no se puede inferir

    Esto impacta en la selección de estrategia de mensaje:
    - MID permite usar estrategias como TECHNICAL_PEER o CURIOSITY_HOOK
    - UNKNOWN fuerza usar estrategias genéricas de fallback
    """

    # Patrones ordenados por prioridad (más senior primero)
    PATTERNS = [
        (r"\b(ceo|cto|cfo|coo|cio|founder|co-founder|owner)\b", Seniority.C_LEVEL),
        (r"\b(vp|vice\s*president)\b", Seniority.VP),
        (r"\b(director|head\s+of)\b", Seniority.DIRECTOR),
        (r"\b(manager|lead|team\s*lead|tech\s*lead)\b", Seniority.MANAGER),
        (r"\b(sr\.?|senior|staff|principal)\b", Seniority.SENIOR),
        (r"\b(jr\.?|junior|entry|trainee|intern)\b", Seniority.JUNIOR),
    ]

    def infer(self, job_title: str) -> Seniority:
        """
        Infiere seniority desde el título del puesto.

        Args:
            job_title: Título del puesto (ej: "Senior PHP Developer")

        Returns:
            Seniority: Nivel inferido según las siguientes reglas:
                - UNKNOWN si job_title es vacío o None
                - Nivel específico si matchea algún patrón conocido
                - MID si hay título pero sin indicadores de nivel

        Ejemplos:
            >>> inferrer = SeniorityInferrer()
            >>> inferrer.infer("CEO")
            Seniority.C_LEVEL
            >>> inferrer.infer("Senior PHP Developer")
            Seniority.SENIOR
            >>> inferrer.infer("Junior Data Analyst")
            Seniority.JUNIOR
            >>> inferrer.infer("Software Engineer")  # Sin indicador de nivel
            Seniority.MID
            >>> inferrer.infer("")  # Sin título
            Seniority.UNKNOWN
        """
        if not job_title:
            return Seniority.UNKNOWN

        title_lower = job_title.lower()
        for pattern, seniority in self.PATTERNS:
            if re.search(pattern, title_lower, re.IGNORECASE):
                return seniority

        # Título presente pero sin indicadores de nivel → asumimos MID
        # (nivel más común en la industria, safe default para personalización)
        return Seniority.MID
