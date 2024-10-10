import utils

import core

from . import models, schemas

__all__ = [
    "create_model",
    "create_model_with_error",
    "handle_created_model_1",
    "handle_created_model_2",
    "handle_created_model_3",
]

logger = utils.get_logger()


def create_model(
    command: schemas.CreateModelCommand,
    uow: core.UnitOfWork,
):
    with uow:
        uow.repo.add(
            models.Model(
                name=command.name,
                message_id=command._id,
            )
        )
        uow.commit()


def create_model_with_error(
    command: schemas.CreateModelErrorCommand,
    uow: core.UnitOfWork,
):
    with uow:
        try:
            uow.repo.add(
                models.Model(
                    name=command.name,
                    message_id=command._id,
                )
            )
            raise ValueError("Error while handling create model command")
        except ValueError as e:
            uow.rollback()
            raise


def handle_created_model_1(event: schemas.CreatedModelEvent):
    logger.info(event.model)


def handle_created_model_2(event: schemas.CreatedModelEvent):
    logger.info(event.model.id)


def handle_created_model_3(event: schemas.CreatedModelErrorEvent):
    logger.info(event.model)
    raise ValueError("Error while handling created model event")
