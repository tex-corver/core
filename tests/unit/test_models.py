from tests.double import fake

import pytest
from icecream import ic


class TestBaseModel:

    def test_model_response(
        self,
        fake_model: fake.Model,
    ):
        ic(fake_model.json)
        assert "password" not in fake_model.json
