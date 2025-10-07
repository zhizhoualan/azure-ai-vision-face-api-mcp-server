"""
Smoke tests to verify all main modules can be imported successfully.
These tests don't require Azure credentials and help catch import errors early.
"""
import pathlib
import sys
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))


def test_import_prompt_parser():
    """Test that prompt_parser module can be imported."""
    from prompt_utils import prompt_parser
    assert hasattr(prompt_parser, 'parse_prompt_for_detect')
    assert hasattr(prompt_parser, 'parse_prompt_for_compare')
    assert hasattr(prompt_parser, 'parse_prompt_for_enroll')


def test_import_prompt_dispatch():
    """Test that prompt_dispatch module can be imported."""
    from prompt_utils import prompt_dispatch
    assert hasattr(prompt_dispatch, 'dispatch_prompt_detect')
    assert hasattr(prompt_dispatch, 'dispatch_prompt_compare')
    assert hasattr(prompt_dispatch, 'dispatch_prompt_enroll')


def test_import_tools():
    """Test that main tool modules can be imported."""
    # These imports require Azure SDK packages but shouldn't fail without credentials
    from tools import CreateLPG
    from tools import ListLPGs
    from tools import DeleteLPG
    from tools import ListPersonsInLPG
    from tools import DeleteFromLPG
    from tools import EnrollFaceToLPG
    from tools import IdentifyFaceInLPG
    from tools import CompareImages
    from tools import AzureFaceAttrib
    
    # Verify key functions exist
    assert hasattr(CreateLPG, 'create_large_person_group')
    assert hasattr(CompareImages, 'compare_source_image_to_target_image')
    assert hasattr(AzureFaceAttrib, 'get_face_dect')


def test_import_blob_tools():
    """Test that blob storage tools can be imported."""
    from tools import BlobFolderTools
    assert hasattr(BlobFolderTools, 'list_blob_folders_and_choose')
    assert hasattr(BlobFolderTools, 'list_public_image_urls')
    assert hasattr(BlobFolderTools, 'download_blob_folder_from_container')


def test_import_openset_attrib():
    """Test that OpenSet attribute tool can be imported."""
    from tools import OpensetFaceAttrib
    assert hasattr(OpensetFaceAttrib, 'get_face_openset_attrib')
