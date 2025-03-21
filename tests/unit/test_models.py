import dataclasses
import json
from datetime import datetime
from typing import Any
import pydantic
import pytest
from icecream import ic

import core
from tests.double import fake


class TestBaseModel:

    @pytest.fixture
    def kwargs(
        self, ignore_keys: set[str], request: pytest.FixtureRequest
    ) -> dict[str, Any]:
        if hasattr(request.node, "callspec"):
            case_name = request.node.callspec.id
            match case_name:
                case case_name if "success:base" in case_name:
                    return {"name": "test"}
                case case_name if "success:all-fields" in case_name:
                    return {"name": "test", "password": "123456"}
                case case_name if "success:override-ignore-keys" in case_name:
                    return {"name": "test", "ignore_keys": ignore_keys}
        return {"name": "test"}

    @pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param({}, id="success:base"),
            pytest.param({}, id="success:all-fields"),
            pytest.param({}, id="success:override-ignore-keys"),
        ],
        indirect=["kwargs"],
    )
    def test_init(self, kwargs: dict[str, Any]):
        model = fake.Model(**kwargs)
        for key, value in kwargs.items():
            assert getattr(model, key) == value

    @pytest.mark.parametrize(
        "model",
        [
            pytest.param(
                {},
                id="success:base",
            ),
            pytest.param(
                {},
                id="success:override-ignore-keys",
            ),
        ],
        indirect=["model"],
    )
    def test_json(
        self,
        model: fake.Model,
        ignore_keys: set[str],
    ):
        model_json = model.json
        for ignore_key in ignore_keys:
            assert ignore_key not in model_json


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
        ic(l0_model.json["j"])
        json.dumps(l0_model.json)
