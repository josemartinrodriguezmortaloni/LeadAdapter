import pytest

from src.domain.services.seniority_inferrer import Seniority, SeniorityInferrer


class TestSeniorityInferrer:
    def setup_method(self):
        self.inferrer = SeniorityInferrer()

    @pytest.mark.parametrize(
        "title,expected",
        [
            ("CEO", Seniority.C_LEVEL),
            ("CTO at Startup", Seniority.C_LEVEL),
            ("Co-Founder", Seniority.C_LEVEL),
            ("VP of Engineering", Seniority.VP),
            ("Director of Sales", Seniority.DIRECTOR),
            ("Engineering Manager", Seniority.MANAGER),
            ("Senior PHP Developer", Seniority.SENIOR),
            ("Staff Engineer", Seniority.SENIOR),
            ("Junior Data Analyst", Seniority.JUNIOR),
            ("Software Engineer", Seniority.MID),
            ("Developer", Seniority.MID),
        ],
    )
    def test_infer_seniority(self, title: str, expected: Seniority):
        assert self.inferrer.infer(title) == expected

    def test_empty_title_returns_unknown(self):
        assert self.inferrer.infer("") == Seniority.UNKNOWN
