"""Shared test fixtures and configuration"""
import pytest
from fastapi.testclient import TestClient
from sys import path
from pathlib import Path

# Add src directory to path for imports
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in path:
    path.insert(0, src_path)

from app import app


@pytest.fixture
def client():
    """Fixture that provides a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Fixture providing a sample email for testing"""
    return "teststudent@mergington.edu"


@pytest.fixture
def existing_activity():
    """Fixture providing the name of an activity that exists in the app"""
    return "Chess Club"


@pytest.fixture
def nonexistent_activity():
    """Fixture providing the name of an activity that doesn't exist"""
    return "Nonexistent Activity"