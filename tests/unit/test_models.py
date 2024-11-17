import dataclasses
import json
from datetime import datetime

import pydantic
import pytest
from icecream import ic

import core
from tests.double import fake


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


class L2Model(core.BaseModel):
    a: int = 4
    b: list[str] = dataclasses.field(default=["a", "b"])


class L1Model(core.BaseModel):
    c: str = "c"
    d: L2Model = dataclasses.field(default_factory=lambda: L2Model())
    e: list[L2Model] = dataclasses.field(
        default_factory=lambda: [L2Model for _ in range(3)]
    )

    def __init__(
        self,
        c="c",
        d=L2Model(),
        e=[L2Model() for _ in range(3)],
    ):
        super().__init__()
        self.c = c
        self.d = d
        self.e = e


class PydanticModel(pydantic.BaseModel):
    created_time: datetime = pydantic.Field(default_factory=datetime.now)


class L0Model(core.BaseModel):
    f: str = "f"
    g: L1Model = dataclasses.field(default_factory=lambda: L1Model())
    h: list[L1Model] = dataclasses.field(
        default_factory=lambda: [L1Model for _ in range(3)]
    )
    i: dict[str, L1Model] = dataclasses.field(
        default_factory=lambda: {f"{i}": L1Model() for i in range(3)}
    )
    j: list[PydanticModel] = dataclasses.field(
        default_factory=lambda: [PydanticModel() for _ in range(3)]
    )

    def __init__(
        self,
        f="f",
        g=L1Model(),
        h=[L1Model() for _ in range(3)],
        i={f"{i}": L1Model() for i in range(3)},
        j=[PydanticModel() for _ in range(3)],
    ):
        super().__init__()
        self.f = f
        self.g = g
        self.h = h
        self.i = i
        self.j = j


class TestInheritModel:
    @pytest.fixture
    def l0_model(self):
        return L0Model()

    def test_json(self, l0_model: L0Model):
        ic(l0_model.json['j'])
        json.dumps(l0_model.json)
