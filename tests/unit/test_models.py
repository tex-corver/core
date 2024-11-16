from tests.double import fake

import pytest
from icecream import ic


class TestBaseModel:

    @pytest.mark.parametrize(
        "model, expected_ignore_keys",
        [
            pytest.param(
                "fake_model",
                set(["password"]),
                id="base_case",
            ),
            pytest.param(
                "fake_ignore_keys_model",
                set(["pin"]),
                id="override_ignore_keys",
            ),
        ],
    )
    def test_ignore_keys_model_json(
        self,
        model,
        expected_ignore_keys,
        request,
    ):
        model = request.getfixturevalue(model)
        ic(model.json)
        assert model.ignore_keys == expected_ignore_keys
        for ignore_key in model.ignore_keys:
            assert ignore_key not in model.json
