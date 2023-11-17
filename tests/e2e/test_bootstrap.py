from collections.abc import Callable
import logging
import os
import pytest
import sqlalchemy
from sqlalchemy import orm as sqlalchemy_orm, Table, Column, Integer, String, MetaData, ForeignKey

import core
from core import orm
import utils

@orm.map_once
def start_mappers(
    metadata: sqlalchemy.MetaData = None,
):
    if metadata is None:
        uow = core.UnitOfWork()
    sqlalchemy_orm.configure_mappers()