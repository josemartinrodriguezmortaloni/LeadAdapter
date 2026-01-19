from dataclasses import dataclass, field
from typing import ClassVar

from domain.enums.seniority import Seniority


@dataclass(frozen=True)
class ICPProfile:
    """
    Perfil de Cliente Ideal (Ideal Customer Profile).

    Define las características del cliente objetivo para personalizar
    mensajes de outreach. Incluye títulos objetivo, industrias,
    pain points y keywords del sector.

    Attributes:
        name: Nombre descriptivo del ICP (ej: "Decision Makers Tech")
        target_titles: Títulos de puesto objetivo (ej: ["CTO", "VP Engineering"])
        target_industries: Industrias objetivo (ej: ["SaaS", "Fintech"])
        company_size_range: Rango de tamaño de empresa (empleados)
        pain_points: Problemas típicos de este perfil
        keywords_sector: Keywords del sector para matching
    """

    # Keywords para filtrar pain points según tipo de rol
    _RELEVANCE_KEYWORDS: ClassVar[dict[str, frozenset[str]]] = {
        "executive": frozenset(
            [
                "roi",
                "costo",
                "presupuesto",
                "escalar",
                "crecer",
                "revenue",
                "inversión",
                "competencia",
                "mercado",
                "estrategia",
                "visión",
                "roadmap",
            ]
        ),
        "manager": frozenset(
            [
                "equipo",
                "productividad",
                "deadline",
                "contratar",
                "retención",
                "talento",
                "coordinación",
                "delivery",
                "recursos",
                "capacidad",
                "planning",
            ]
        ),
        "technical": frozenset(
            [
                "bug",
                "deuda técnica",
                "legacy",
                "performance",
                "documentación",
                "testing",
                "deploy",
                "integración",
                "herramientas",
                "arquitectura",
                "código",
            ]
        ),
    }

    name: str
    target_titles: list[str] = field(default_factory=list)
    target_industries: list[str] = field(default_factory=list)
    company_size_range: tuple[int, int] = (1, 10000)
    pain_points: list[str] = field(default_factory=list)
    keywords_sector: list[str] = field(default_factory=list)

    def matches_title(self, job_title: str) -> bool:
        """
        Check rápido de elegibilidad por título.

        Verifica si el job_title del lead contiene alguno de los
        target_titles de este ICP. Este es un check binario simple,
        NO un scoring. Para matching con scoring, usar ICPMatcher.

        Args:
            job_title: Título del puesto del lead.

        Returns:
            True si algún target_title está contenido en el job_title.

        Example:
            >>> icp = ICPProfile(name="Devs", target_titles=["developer", "engineer"])
            >>> icp.matches_title("Senior Developer")
            True
            >>> icp.matches_title("Product Manager")
            False

        Note:
            Para matching sofisticado con scoring (títulos + keywords + skills),
            usar el servicio de dominio ICPMatcher.match().
        """
        if not self.target_titles:
            return False
        title_lower = job_title.lower()
        return any(target.lower() in title_lower for target in self.target_titles)

    def get_relevant_pain_points(self, seniority: Seniority) -> list[str]:
        """
        Retorna pain points relevantes según el seniority del lead.

        Filtra los pain_points del ICP basándose en el nivel de seniority.
        Ejecutivos (C-Level, VP, Director) ven problemas de negocio (ROI,
        crecimiento), managers ven problemas de equipo (productividad,
        deadlines), y técnicos ven problemas de implementación (bugs, legacy).

        Args:
            seniority: Nivel de seniority del lead, ya inferido por
                SeniorityInferrer. Ejemplo: Seniority.C_LEVEL, Seniority.SENIOR.

        Returns:
            Lista filtrada de pain points relevantes para el rol.
            Si no hay pain points que matcheen los keywords del rol,
            retorna todos los pain points como fallback.

        Example:
            >>> icp.pain_points = ["Escalar el equipo", "Bugs en producción", "ROI bajo"]
            >>> icp.get_relevant_pain_points(Seniority.C_LEVEL)
            ['Escalar el equipo', 'ROI bajo']
            >>> icp.get_relevant_pain_points(Seniority.SENIOR)
            ['Bugs en producción']
        """
        if not self.pain_points:
            return []

        role_type = self._seniority_to_role_type(seniority)
        keywords = self._RELEVANCE_KEYWORDS.get(role_type)

        if not keywords:
            return list(self.pain_points)

        # Filtrar pain points que contengan keywords relevantes
        relevant = [pain for pain in self.pain_points if any(kw in pain.lower() for kw in keywords)]

        # Si el filtro es muy estricto, retornar todos
        return relevant if relevant else list(self.pain_points)

    def _seniority_to_role_type(self, seniority: Seniority) -> str:
        """
        Mapea un Seniority a un tipo de rol para filtrar pain points.

        El mapeo agrupa los 8 niveles de Seniority en 3 categorías de rol,
        cada una con keywords de pain points diferentes:

        - executive: C_LEVEL, VP, DIRECTOR → problemas de negocio
        - manager: MANAGER → problemas de equipo
        - technical: SENIOR, MID, JUNIOR, UNKNOWN → problemas técnicos

        Args:
            seniority: Nivel de seniority del lead.

        Returns:
            Tipo de rol: 'executive' | 'manager' | 'technical'
        """
        if seniority in (Seniority.C_LEVEL, Seniority.VP, Seniority.DIRECTOR):
            return "executive"
        if seniority == Seniority.MANAGER:
            return "manager"
        return "technical"
