from typing import Optional

from domain.entities.lead import Lead
from domain.entities.playbook import Playbook
from domain.value_objects.icp_profile import ICPProfile


class ICPMatcher:
    """
    Servicio de dominio que encuentra el ICP (Ideal Customer Profile) más
    relevante para un lead dado.

    Algoritmo de Matching
    ---------------------
    El matching se basa en un sistema de scoring ponderado (0-1) que evalúa
    la compatibilidad entre el lead y cada ICP del playbook:

    1. **Match por título** (peso: 0.5)
       Compara el job_title del lead contra los target_titles del ICP.
       Ejemplo: "Senior PHP Developer" matchea con ICP que tiene
       target_titles=["developer", "engineer"].

    2. **Match por keywords de sector** (peso: 0.3)
       Busca keywords_sector del ICP dentro del job_title del lead.
       Ejemplo: ICP con keywords_sector=["fintech", "saas"] matchea
       con lead cuyo título contiene esas palabras.

    3. **Match por skills** (peso: 0.2)
       Cruza las skills del lead con los keywords_sector del ICP.
       Ejemplo: Lead con skills=["python", "aws"] matchea con ICP
       que tiene keywords_sector=["cloud", "python"].

    Umbral Mínimo
    -------------
    Se requiere un score >= 0.3 para considerar un match válido.
    Si ningún ICP supera el umbral, retorna None.

    Ejemplo de Uso
    --------------
    ```python
    matcher = ICPMatcher()
    matched_icp = matcher.match(lead, playbook)
    if matched_icp:
        pain_points = matched_icp.pain_points
    ```
    """

    def match(self, lead: Lead, playbook: Playbook) -> Optional[ICPProfile]:
        """
        Encuentra el ICP que mejor matchea con el lead.

        Itera sobre todos los ICPs del playbook, calcula un score de
        compatibilidad para cada uno, y retorna el de mayor score
        siempre que supere el umbral mínimo (0.3).

        Args:
            lead: El lead a evaluar. Debe tener al menos job_title.
            playbook: Configuración comercial con lista de icp_profiles.

        Returns:
            El ICPProfile con mayor score si supera el umbral,
            None si no hay ICPs o ninguno supera el umbral mínimo.

        Example:
            >>> lead = Lead(first_name="Juan", job_title="CTO", company_name="Acme")
            >>> matched = matcher.match(lead, playbook)
            >>> matched.name if matched else "Sin match"
            'Decision Makers Tech'
        """
        if not playbook.icp_profiles:
            return None

        best_match: Optional[ICPProfile] = None
        best_score = 0

        for icp in playbook.icp_profiles:
            score = self._calculate_match_score(lead, icp)
            if score > best_score:
                best_score = score
                best_match = icp

        # Umbral mínimo de matching
        if best_score < 0.3:
            return None
        return best_match

    def _calculate_match_score(self, lead: Lead, icp: ICPProfile) -> float:
        """
        Calcula el score de compatibilidad entre un lead y un ICP.

        El score es un valor normalizado entre 0 y 1 que representa
        qué tan bien el lead encaja con el perfil de cliente ideal.

        Fórmula de Cálculo
        ------------------
        score = (title_score * 0.5) + (keyword_score * 0.3) + (skills_score * 0.2)

        Donde cada componente se calcula como:
        - title_score: matches encontrados / total target_titles
        - keyword_score: keywords encontrados en título / total keywords_sector
        - skills_score: skills que matchean / total skills del lead

        Args:
            lead: Lead con job_title y opcionalmente skills.
            icp: ICPProfile con target_titles, keywords_sector.

        Returns:
            Score normalizado entre 0.0 y 1.0.
            - 0.0: Sin ninguna coincidencia
            - 0.5: Match parcial (ej: solo título coincide)
            - 1.0: Match perfecto en todos los criterios

        Note:
            El score se limita a 1.0 máximo aunque la suma supere ese valor.
        """
        score = 0.0
        title_lower = lead.job_title.lower()

        # Match por título (peso: 0.5)
        title_matches = sum(1 for keyword in icp.target_titles if keyword.lower() in title_lower)

        if icp.target_titles:
            score += 0.5 * (title_matches / len(icp.target_titles))

        # Match por keywords de sector (peso: 0.3)
        keyword_matches = sum(
            1 for keyword in icp.keywords_sector if keyword.lower() in title_lower
        )
        if icp.keywords_sector:
            score += 0.3 * (keyword_matches / len(icp.keywords_sector))

        # Match por skills del lead (peso: 0.2)
        if lead.skills and icp.keywords_sector:
            skills_matches = sum(
                1
                for skill in lead.skills
                if any(kw.lower() in skill.lower() for kw in icp.keywords_sector)
            )
            score += 0.2 * (skills_matches / len(lead.skills))

        return min(score, 1.0)
