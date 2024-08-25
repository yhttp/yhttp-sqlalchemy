import abc

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column as sa_mapped_column

from yhttp.core import guard as yguard


class FieldMixin(metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    @abc.abstractmethod
    def _satype(self):
        raise NotImplementedError

    def column(self, *args, nullable=None, **kwargs):
        if nullable is not None:
            kwargs['nullable'] = nullable
        else:
            kwargs['nullable'] = self.optional

        return sa_mapped_column(
            self._satype,
            *args,
            **kwargs
        )


class String(FieldMixin, yguard.String):
    @property
    def _satype(self):
        if self.length:
            return sa.String(self.length[1])
        return sa.String


class Integer(FieldMixin, yguard.Integer):
    @property
    def _satype(self):
        return sa.Integer
