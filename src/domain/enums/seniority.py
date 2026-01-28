"""Niveles de seniority para clasificación de leads."""

from enum import Enum


class Seniority(str, Enum):
    """
    Nivel de seniority inferido desde el job_title de un lead.

    El seniority determina qué estrategia de mensaje usar y cómo
    personalizar la comunicación. Los niveles están ordenados de
    mayor a menor autoridad de decisión.

    Attributes:
        C_LEVEL: CEO, CTO, CFO, Founder - máxima autoridad
        VP: Vice President - reporta a C-Level
        DIRECTOR: Director, Head of - lidera departamentos
        MANAGER: Manager, Team Lead - lidera equipos
        SENIOR: Senior, Staff, Principal - IC experimentado
        MID: Sin indicador de nivel - asumido por defecto
        JUNIOR: Junior, Entry, Intern - inicio de carrera
        UNKNOWN: Sin título disponible - no se puede inferir
    """

    C_LEVEL = "C_LEVEL"
    VP = "VP"
    DIRECTOR = "DIRECTOR"
    MANAGER = "MANAGER"
    SENIOR = "SENIOR"
    MID = "MID"
    JUNIOR = "JUNIOR"
    UNKNOWN = "UNKNOWN"

    @property
    def is_decision_maker(self) -> bool:
        """Determina si este nivel tiene autoridad de decisión de compra."""
        return self in (Seniority.C_LEVEL, Seniority.VP, Seniority.DIRECTOR)

    @property
    def is_technical(self) -> bool:
        """Determina si este nivel es típicamente técnico/IC."""
        return self in (Seniority.SENIOR, Seniority.MID, Seniority.JUNIOR)

    @property
    def communication_tone(self) -> str:
        """Tono de comunicación apropiado para este nivel."""
        tones = {
            Seniority.C_LEVEL: "conciso, orientado a resultados de negocio y ROI",
            Seniority.VP: "estratégico, enfocado en impacto organizacional",
            Seniority.DIRECTOR: "profesional, balance entre estrategia y ejecución",
            Seniority.MANAGER: "colaborativo, enfocado en eficiencia del equipo",
            Seniority.SENIOR: "técnico y directo, respetando su experiencia",
            Seniority.MID: "amigable y educativo, mostrando valor claro",
            Seniority.JUNIOR: "accesible y sin jerga compleja",
            Seniority.UNKNOWN: "profesional y neutro",
        }
        return tones.get(self, "profesional")
