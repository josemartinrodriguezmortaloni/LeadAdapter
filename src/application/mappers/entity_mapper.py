"""
Mapper para conversión entre DTOs y entidades de dominio.

Este módulo centraliza la lógica de mapeo entre los DTOs de la capa
de aplicación y las entidades del dominio, siguiendo el principio
de separación de responsabilidades.
"""

from dataclasses import dataclass

from application.dtos.requests import LeadDTO, PlaybookDTO, SenderDTO
from domain.entities.lead import Lead
from domain.entities.playbook import Playbook
from domain.entities.sender import Sender
from domain.value_objects.campaign_history import CampaignHistory
from domain.value_objects.icp_profile import ICPProfile
from domain.value_objects.product import Product
from domain.value_objects.work_experience import WorkExperience


@dataclass
class EntityMapper:
    """
    Mapper para conversión bidireccional entre DTOs y entidades.

    Centraliza la lógica de transformación siguiendo el patrón
    Data Mapper, manteniendo las entidades de dominio libres de
    conocimiento sobre la capa de aplicación.

    Example:
        >>> mapper = EntityMapper()
        >>> lead = mapper.to_lead(lead_dto)
        >>> sender = mapper.to_sender(sender_dto)
    """

    def to_lead(self, dto: LeadDTO) -> Lead:
        """
        Convierte LeadDTO a entidad de dominio Lead.

        Args:
            dto: DTO con datos del lead desde la request.

        Returns:
            Entidad Lead del dominio.
        """
        work_experience = [
            WorkExperience(
                company=exp.company,
                title=exp.title,
                start_date=exp.start_date,
                end_date=exp.end_date,
                description=exp.description,
            )
            for exp in dto.work_experience
        ]

        campaign_history = None
        if dto.campaign_history:
            campaign_history = CampaignHistory(
                total_attempts=dto.campaign_history.total_attempts,
                last_contact_date=dto.campaign_history.last_contact_date,
                last_channel=dto.campaign_history.last_channel,
                responses_received=dto.campaign_history.responses_received,
            )

        return Lead(
            first_name=dto.first_name,
            last_name=dto.last_name,
            job_title=dto.job_title,
            company_name=dto.company_name,
            work_experience=work_experience,
            campaign_history=campaign_history,
            bio=dto.bio,
            skills=list(dto.skills),
            linkedin_url=dto.linkedin_url,
        )

    def to_sender(self, dto: SenderDTO) -> Sender:
        """
        Convierte SenderDTO a entidad de dominio Sender.

        Args:
            dto: DTO con datos del sender desde la request.

        Returns:
            Entidad Sender del dominio.
        """
        return Sender(
            name=dto.name,
            company_name=dto.company_name,
            job_title=dto.job_title,
            email=dto.email,
        )

    def to_playbook(self, dto: PlaybookDTO) -> Playbook:
        """
        Convierte PlaybookDTO a entidad de dominio Playbook.

        Args:
            dto: DTO con datos del playbook desde la request.

        Returns:
            Entidad Playbook del dominio.
        """
        products = [
            Product(
                name=prod.name,
                description=prod.description,
                category=prod.category,
                key_benefits=list(prod.key_benefits),
                target_problems=list(prod.target_problems),
            )
            for prod in dto.products
        ]

        icp_profiles = [
            ICPProfile(
                name=icp.name,
                target_titles=list(icp.target_titles),
                target_industries=list(icp.target_industries),
                pain_points=list(icp.pain_points),
                keywords_sector=list(icp.keywords_sector),
            )
            for icp in dto.icp_profiles
        ]

        return Playbook(
            communication_style=dto.communication_style,
            products=products,
            icp_profiles=icp_profiles,
            success_cases=list(dto.success_cases),
            common_objections=list(dto.common_objections),
            value_propositions=list(dto.value_propositions),
        )
