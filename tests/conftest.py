import types
from typing import Iterable

import pytest
from koza.app import KozaApp
from koza.koza_runner import set_koza
from koza.model.config.source_config import PrimaryFileConfig
from koza.model.source import Source, SourceFile


@pytest.fixture(scope="package")
def mock_koza():

    # This should be extracted out but for quick prototyping
    def _mock_write(self, source_name, *entities):
        self._entities = list(*entities)

    def _make_mock_koza_app(
        name: str,
        data: Iterable,
        transform_code: str,
        map_cache=None,
        filters=None,
        translation_table=None,
    ):
        mock_source_file_config = PrimaryFileConfig(
            name=name, files=[], transform_code=transform_code,
        )
        mock_source_file = SourceFile(mock_source_file_config)
        mock_source_file._reader = data

        mock_source = Source(source_files=[mock_source_file])

        koza = KozaApp(mock_source)
        # TODO filter mocks
        koza.source.translation_table = translation_table
        koza.map_cache = map_cache
        koza.write = types.MethodType(_mock_write, koza)

        return koza

    def _transform(
        name: str,
        data: Iterable,
        transform_code: str,
        map_cache=None,
        filters=None,
        translation_table=None,
    ):
        koza_app = _make_mock_koza_app(
            name,
            data,
            transform_code,
            map_cache=map_cache,
            filters=filters,
            translation_table=translation_table,
        )
        set_koza(koza_app)
        koza_app.process_sources()
        return koza_app._entities if hasattr(koza_app, "_entities") else list()

    return _transform
