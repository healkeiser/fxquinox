# Built-in
from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class Project:
    # Required
    name: str

    # Optional
    episodes: list["Episode"] = field(default_factory=list)
    sequences: list["Sequence"] = field(default_factory=list)
    shots: list["Shot"] = field(default_factory=list)
    assets: list["Asset"] = field(default_factory=list)
    publishes: list["Publish"] = field(default_factory=list)
    versions: list["Version"] = field(default_factory=list)
    steps: list["Step"] = field(default_factory=list)
    tasks: list["Task"] = field(default_factory=list)
    render_engines: list["RenderEngine"] = field(default_factory=list)


@dataclass
class Entity:
    # Required
    project: Project
    name: str


@dataclass
class Episode(Entity):
    # Optional
    sequences: list["Sequence"] = field(default_factory=list)
    shots: list["Shot"] = field(default_factory=list)


@dataclass
class Sequence(Entity):
    """Represents a Sequence in a Project.

    Attributes:
        parent (Optional[Union[Project, Episode]]): The parent of the Sequence, which can be either a Project or an
            Episode. Defaults to `None`.
        episode (Optional[Episode]): The Episode that the Sequence belongs to. Defaults to `None`.
        assets (List[Asset], optional): The list of Assets in the Sequence. Defaults to an empty list.
        shots (List[Shot], optional): The list of Shots in the Sequence. Defaults to an empty list.
        publishes (List[Publish], optional): The list of Publishes in the Sequence. Defaults to an empty list.
        versions (List[Version], optional): The list of Versions in the Sequence. Defaults to an empty list.
        steps (List[Step], optional): The list of Steps in the Sequence. Defaults to an empty list.
        tasks (List[Task], optional): The list of Tasks in the Sequence. Defaults to an empty list.
    """

    # Optional
    parent: Optional[Union[Project, Episode]] = None
    episode: Optional[Episode] = None
    assets: List["Asset"] = field(default_factory=list)
    shots: List["Shot"] = field(default_factory=list)
    publishes: List["Publish"] = field(default_factory=list)
    versions: List["Version"] = field(default_factory=list)
    steps: List["Step"] = field(default_factory=list)
    tasks: List["Task"] = field(default_factory=list)


@dataclass
class Shot:
    # Optional
    parent: Optional[Union[Project, Episode]] = None
    sequence: Optional[Sequence] = None
    episode: Optional[Episode] = None
    assets: list["Asset"] = None
    cut_in: int = 1001
    cut_out: int = 1100
    handle_in: int = 901
    handle_out: int = 1200


@dataclass
class Step:
    # Optional
    tasks: list["Task"] = field(default_factory=list)


@dataclass
class Task:
    pass


@dataclass
class Asset:
    pass


@dataclass
class Publish:
    pass


@dataclass
class Version:
    pass


@dataclass
class RenderEngine:
    # Required
    name: str

    # Optional
    version: str = ""
    required_environment: dict = field(default_factory=dict)


def get_project_entity(project_name: str) -> Project:
    pass


def get_sequence_entity(project_name: str) -> Sequence:
    pass


def get_shot_entity(project_name: str, sequence_name: str) -> Shot:
    pass


def get_step_entity(project_name: str) -> Step:
    pass


def get_task_entity(project_name: str) -> Task:
    pass


def get_asset_entity(project_name: str) -> Asset:
    pass
