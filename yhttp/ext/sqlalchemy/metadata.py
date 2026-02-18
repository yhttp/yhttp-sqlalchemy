import abc

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column as sa_mapped_column

from yhttp.core import guard as yguard


class FieldMixin(metaclass=abc.ABCMeta):
    def __init__(self, *args, example=None, **kwargs):
        self.example = example
        super().__init__(*args, **kwargs)

    def __call__(self, *, example=None, **kwargs):
        kwargs['example'] = self.example if example is None else example

        if 'name' not in kwargs:
            kwargs['name'] = self.name

        return super(FieldMixin, self).__call__(**kwargs)

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


class Boolean(FieldMixin, yguard.Boolean):
    @property
    def _satype(self):
        return sa.Boolean
