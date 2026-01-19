from dataclasses import dataclass, field
from typing import Optional

from domain.exceptions.domain_exceptions import InvalidPlaybookError
from domain.value_objects.icp_profile import ICPProfile
from domain.value_objects.product import Product


@dataclass
class Playbook:
    communication_style: str
    products: list[Product]
    icp_profiles: list[ICPProfile] = field(default_factory=list)
    success_cases: list[str] = field(default_factory=list)
    common_objections: list[str] = field(default_factory=list)
    value_propositions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.communication_style.strip():
            raise InvalidPlaybookError(field="communication_style", reason="cannot be empty")
        if not self.products:
            raise InvalidPlaybookError(field="products", reason="cannot be empty")

    def get_product_for_icp(self, icp: ICPProfile) -> Optional[Product]:
        """Obtiene el producto más relevante para un ICP.

        Busca el producto cuyos target_problems mejor coincidan con
        los pain_points del ICP dado.

        Args:
            icp: El perfil de cliente ideal a matchear.

        Returns:
            El producto más relevante o el primero si no hay match claro.
        """
        if not self.products:
            return None

        if not icp.pain_points:
            return self.products[0]

        best_product: Optional[Product] = None
        best_score = 0

        for product in self.products:
            score = sum(
                1
                for pain in icp.pain_points
                for problem in product.target_problems
                if pain.lower() in problem.lower() or problem.lower() in pain.lower()
            )
            if score > best_score:
                best_score = score
                best_product = product

        return best_product if best_product else self.products[0]
