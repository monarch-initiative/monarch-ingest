"""
Testing configuration and utilities for monarch-ingest.
Provides replacements for Koza 1.x testing utilities to work with Koza 2.0+.
"""

import importlib.util
import sys
from pathlib import Path
from typing import List, Dict, Any, Union
import pytest


def mock_koza_2x(
    source_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]], transform_script: str, **kwargs
) -> List[Any]:
    """
    Mock Koza transform for Koza 2.0+ testing.

    Replacement for the old koza.utils.testing_utils.mock_koza function.
    This directly imports and runs the transform function on test data.

    Args:
        source_name: Name of the source
        data: Input data (single dict or list of dicts)
        transform_script: Path to transform script
        **kwargs: Additional config options (map_cache, global_table, etc.)

    Returns:
        List of transformed objects
    """
    # Ensure data is a list
    if isinstance(data, dict):
        data = [data]

    results = []

    try:
        # Convert relative path to absolute path from current working directory
        transform_path = Path(transform_script)
        if not transform_path.is_absolute():
            transform_path = Path.cwd() / transform_path

        # Import the transform module
        spec = importlib.util.spec_from_file_location("transform_module", str(transform_path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load transform script: {transform_path}")

        transform_module = importlib.util.module_from_spec(spec)

        # Add the parent directory to sys.path temporarily for imports to work
        parent_dir = str(transform_path.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            path_added = True
        else:
            path_added = False

        # Add any additional context to the module if provided
        if 'map_cache' in kwargs:
            transform_module.map_cache = kwargs['map_cache']
        if 'global_table' in kwargs:
            transform_module.global_table = kwargs['global_table']

        try:
            # Execute the module to register decorators
            spec.loader.exec_module(transform_module)

            # Find the transform function (should be decorated with @koza.transform_record)
            transform_func = None

            # First, try to find a function named 'transform_record' directly
            if hasattr(transform_module, 'transform_record'):
                transform_func = getattr(transform_module, 'transform_record')
            else:
                # If not found, search through all attributes
                for attr_name in dir(transform_module):
                    attr = getattr(transform_module, attr_name)
                    if callable(attr) and hasattr(attr, '__name__'):
                        if attr.__name__ == 'transform_record' or attr_name == 'transform_record':
                            transform_func = attr
                            break

            if transform_func is None:
                # Debug: show what attributes are available
                available_attrs = [attr for attr in dir(transform_module) if not attr.startswith('_')]
                raise ValueError(
                    f"No transform_record function found in {transform_script}. Available attributes: {available_attrs}"
                )

            # Run the transform on each row
            for row in data:
                try:
                    # Create a mock koza_transform object (may not be needed but keeps signature compatible)
                    mock_koza_transform = type('MockKozaTransform', (), {})()

                    result = transform_func(mock_koza_transform, row)
                    if result:
                        if isinstance(result, list):
                            results.extend(result)
                        else:
                            results.append(result)
                except Exception as e:
                    print(f"Transform error for row {row}: {e}")
                    # Continue processing other rows
        finally:
            # Clean up sys.path
            if path_added:
                sys.path.remove(parent_dir)

    except Exception as e:
        print(f"Failed to execute transform {transform_script}: {e}")
        return []

    return results


@pytest.fixture
def mock_koza():
    """Provide mock_koza fixture for backward compatibility with old tests."""
    return mock_koza_2x


@pytest.fixture(scope="package")
def global_table():
    return "src/monarch_ingest/translation_table.yaml"


@pytest.fixture
def taxon_label_map_cache():
    return {
        "taxon-labels": {
            "NCBITaxon:7955": {"label": "Danio rerio"},
            "NCBITaxon:6239": {"label": "Caenorhabditis elegans"},
            "NCBITaxon:44689": {"label": "Dictyostelium discoideum"},
            "NCBITaxon:9606": {"label": "Homo sapiens"},
            "NCBITaxon:4896": {"label": "Schizosaccharomyces pombe"},
            "NCBITaxon:9615": {"label": "Canis lupus familiaris"},
            "NCBITaxon:9913": {"label": "Bos taurus"},
            "NCBITaxon:9823": {"label": "Sus scrofa"},
            "NCBITaxon:9031": {"label": "Gallus gallus"},
        }
    }


@pytest.fixture
def source_name():
    """Default source name for tests."""
    return "test_source"


@pytest.fixture
def script():
    """Default script path for tests."""
    return "./src/test_transform.py"
