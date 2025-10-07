import pathlib
import sys
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from prompt_utils.prompt_parser import (
    parse_prompt_for_detect,
    parse_prompt_for_compare,
    parse_prompt_for_enroll,
    ParsedDetect,
    ParsedCompare,
    ParsedEnroll,
)


class TestParsePromptForDetect:
    """Test parse_prompt_for_detect function."""

    def test_parse_local_image_with_mask_and_glasses(self):
        """Test parsing local image path with mask and glasses keywords."""
        prompt = "Check all the faces inside detection1.jpg wearing the mask or glasses"
        result = parse_prompt_for_detect(prompt)
        
        assert isinstance(result, ParsedDetect)
        assert result.file_path == "detection1.jpg"
        assert result.is_url is False
        assert result.return_MASK is True
        assert result.return_GLASSES is True

    def test_parse_url_image_with_mask_and_glasses(self):
        """Test parsing URL image with mask and glasses keywords."""
        url = "https://example.com/images/detection1.jpg"
        prompt = f"Check all the faces inside {url} wearing the mask or glasses"
        result = parse_prompt_for_detect(prompt)
        
        assert isinstance(result, ParsedDetect)
        assert result.file_path == url
        assert result.is_url is True
        assert result.return_MASK is True
        assert result.return_GLASSES is True

    def test_parse_local_image_with_mask_only(self):
        """Test parsing with mask keyword only."""
        prompt = "Check all the faces inside photo.png wearing the mask"
        result = parse_prompt_for_detect(prompt)
        
        assert result.file_path == "photo.png"
        assert result.is_url is False
        assert result.return_MASK is True
        assert result.return_GLASSES is False

    def test_parse_local_image_with_glasses_only(self):
        """Test parsing with glasses keyword only."""
        prompt = "Check all the faces inside photo.jpeg wearing glasses"
        result = parse_prompt_for_detect(prompt)
        
        assert result.file_path == "photo.jpeg"
        assert result.is_url is False
        assert result.return_MASK is False
        assert result.return_GLASSES is True

    def test_parse_no_mask_no_glasses(self):
        """Test parsing without mask or glasses keywords."""
        prompt = "Check all the faces inside photo.bmp"
        result = parse_prompt_for_detect(prompt)
        
        assert result.file_path == "photo.bmp"
        assert result.is_url is False
        assert result.return_MASK is False
        assert result.return_GLASSES is False

    def test_parse_invalid_no_image(self):
        """Test that parsing fails when no image is found."""
        prompt = "Check all the faces"
        with pytest.raises(ValueError, match="Could not find image path or URL"):
            parse_prompt_for_detect(prompt)

    def test_parse_different_image_extensions(self):
        """Test parsing various image file extensions."""
        extensions = ["jpg", "jpeg", "png", "bmp", "gif", "webp"]
        for ext in extensions:
            prompt = f"Check faces in image.{ext}"
            result = parse_prompt_for_detect(prompt)
            assert result.file_path == f"image.{ext}"


class TestParsePromptForCompare:
    """Test parse_prompt_for_compare function."""

    def test_parse_both_local_images(self):
        """Test comparing two local images."""
        prompt = "Compare the identification1.jpg with findsimilar.jpg"
        result = parse_prompt_for_compare(prompt)
        
        assert isinstance(result, ParsedCompare)
        assert result.left == "identification1.jpg"
        assert result.right == "findsimilar.jpg"
        assert result.left_is_url is False
        assert result.right_is_url is False

    def test_parse_local_and_url(self):
        """Test comparing local image with URL."""
        url = "https://example.com/images/findsimilar.jpg"
        prompt = f"Compare the identification1.jpg with {url}"
        result = parse_prompt_for_compare(prompt)
        
        assert result.left == "identification1.jpg"
        assert result.right == url
        assert result.left_is_url is False
        assert result.right_is_url is True

    def test_parse_both_urls(self):
        """Test comparing two URLs."""
        url1 = "https://example.com/images/img1.jpg"
        url2 = "https://example.com/images/img2.png"
        prompt = f"Compare {url1} with {url2}"
        result = parse_prompt_for_compare(prompt)
        
        assert result.left == url1
        assert result.right == url2
        assert result.left_is_url is True
        assert result.right_is_url is True

    def test_parse_without_the_keyword(self):
        """Test comparing without 'the' keyword."""
        prompt = "Compare image1.jpg with image2.jpg"
        result = parse_prompt_for_compare(prompt)
        
        assert result.left == "image1.jpg"
        assert result.right == "image2.jpg"

    def test_parse_invalid_format(self):
        """Test that parsing fails with invalid format."""
        prompt = "Show me the difference between images"
        with pytest.raises(ValueError, match="Unrecognized compare prompt format"):
            parse_prompt_for_compare(prompt)


class TestParsePromptForEnroll:
    """Test parse_prompt_for_enroll function."""

    def test_parse_single_local_image(self):
        """Test enrolling single local image."""
        prompt = "Enroll the face in detection1.jpg to the person group 'test-group' as 'test-person'"
        result = parse_prompt_for_enroll(prompt)
        
        assert isinstance(result, ParsedEnroll)
        assert result.file_path_list == ["detection1.jpg"]
        assert result.person_name == "test-person"
        assert result.group_uuid == "test-group"
        assert result.is_url is False
        assert result.check_quality is True

    def test_parse_single_url_image(self):
        """Test enrolling single URL image."""
        url = "https://example.com/images/detection1.jpg"
        prompt = f"Enroll the face in {url} to the person group test-group as test-person"
        result = parse_prompt_for_enroll(prompt)
        
        assert result.file_path_list == [url]
        assert result.person_name == "test-person"
        assert result.group_uuid == "test-group"
        assert result.is_url is True

    def test_parse_multiple_local_images(self):
        """Test enrolling multiple local images."""
        prompt = "Enroll the faces in img1.jpg,img2.jpg to the person group test-group as test-person"
        result = parse_prompt_for_enroll(prompt)
        
        assert result.file_path_list == ["img1.jpg", "img2.jpg"]
        assert result.person_name == "test-person"
        assert result.group_uuid == "test-group"
        assert result.is_url is False

    def test_parse_without_quotes(self):
        """Test parsing without quotes around names."""
        prompt = "Enroll the face in photo.png to the person group my-group as my-person"
        result = parse_prompt_for_enroll(prompt)
        
        assert result.file_path_list == ["photo.png"]
        assert result.person_name == "my-person"
        assert result.group_uuid == "my-group"

    def test_parse_plural_faces(self):
        """Test parsing with 'faces' keyword."""
        prompt = "Enroll the faces in photo.png to the person group my-group as my-person"
        result = parse_prompt_for_enroll(prompt)
        
        assert result.file_path_list == ["photo.png"]
        assert result.person_name == "my-person"
        assert result.group_uuid == "my-group"

    def test_parse_invalid_format(self):
        """Test that parsing fails with invalid format."""
        prompt = "Upload face image"
        with pytest.raises(ValueError, match="Unrecognized enroll prompt format"):
            parse_prompt_for_enroll(prompt)

    def test_parse_with_various_extensions(self):
        """Test parsing with various image extensions."""
        for ext in ["jpg", "jpeg", "png", "bmp"]:
            prompt = f"Enroll the face in image.{ext} to the person group group1 as person1"
            result = parse_prompt_for_enroll(prompt)
            assert result.file_path_list == [f"image.{ext}"]
