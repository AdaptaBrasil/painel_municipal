import tomllib

from ..core.config import settings
from ..domain.entities import ProjectInfo
from ..domain.interfaces import ProjectInfoServiceInterface

class TomlProjectInfoService(ProjectInfoServiceInterface):
    def get_project_info(self) -> ProjectInfo:
        toml_path = settings.pyproject_path
        
        try:
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
        except (FileNotFoundError, tomllib.TOMLDecodeError):
            data = {}

        project = data.get("project", {})
        
        return ProjectInfo(
            name=project.get("name", "Unknown"),
            version=project.get("version", "Unknown"),
            description=project.get("description", "No description provided.")
        )
