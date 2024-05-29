# Built-in
from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class FXProject:
    # Required
    name: str

    # Optional
    episodes: list["FXEpisode"] = field(default_factory=list)
    sequences: list["FXSequence"] = field(default_factory=list)
    shots: list["FXShot"] = field(default_factory=list)
    assets: list["FXAsset"] = field(default_factory=list)
    publishes: list["FXPublish"] = field(default_factory=list)
    versions: list["FXVersion"] = field(default_factory=list)
    steps: list["FXStep"] = field(default_factory=list)
    tasks: list["FXTask"] = field(default_factory=list)
    render_engines: list["FXRenderEngine"] = field(default_factory=list)


@dataclass
class FXEntity:
    # Required
    project: FXProject
    name: str


@dataclass
class FXEpisode(FXEntity):
    # Optional
    sequences: list["FXSequence"] = field(default_factory=list)
    shots: list["FXShot"] = field(default_factory=list)


@dataclass
class FXSequence(FXEntity):
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
    parent: Optional[Union[FXProject, FXEpisode]] = None
    episode: Optional[FXEpisode] = None
    assets: List["FXAsset"] = field(default_factory=list)
    shots: List["FXShot"] = field(default_factory=list)
    publishes: List["FXPublish"] = field(default_factory=list)
    versions: List["FXVersion"] = field(default_factory=list)
    steps: List["FXStep"] = field(default_factory=list)
    tasks: List["FXTask"] = field(default_factory=list)


@dataclass
class FXShot:
    """Represents a Shot in a Sequence.

    Attributes:
        parent (Optional[Union[Project, Episode]]): The parent of the Shot, which can be either a Project or an Episode.
            Defaults to `None`.
        sequence (Optional[Sequence]): The Sequence that the Shot belongs to. Defaults to `None`.
        episode (Optional[Episode]): The Episode that the Shot belongs to. Defaults to `None`.
        assets (List[Asset], optional): The list of Assets in the Shot. Defaults to an empty list.
        cut_in (int, optional): The cut-in frame number of the Shot. Defaults to 1001.
        cut_out (int, optional): The cut-out frame number of the Shot. Defaults to 1100.
        handle_in (int, optional): The handle-in frame number of the Shot. Defaults to 901.
        handle_out (int, optional): The handle-out frame number of the Shot. Defaults to 1200.
    """

    # Optional
    parent: Optional[Union[FXProject, FXEpisode]] = None
    sequence: Optional[FXSequence] = None
    episode: Optional[FXEpisode] = None
    assets: list["FXAsset"] = None
    cut_in: int = 1001
    cut_out: int = 1100
    handle_in: int = 901
    handle_out: int = 1200


@dataclass
class FXStep:
    # Optional
    tasks: list["FXTask"] = field(default_factory=list)


@dataclass
class FXTask:
    pass


@dataclass
class FXAsset:
    pass


@dataclass
class FXPublish:
    pass


@dataclass
class FXVersion:
    pass


@dataclass
class FXRenderEngine:
    # Required
    name: str

    # Optional
    version: str = ""
    required_environment: dict = field(default_factory=dict)


def get_project_entity(project_name: str) -> FXProject:
    pass


def get_sequence_entity(project_name: str) -> FXSequence:
    pass


def get_shot_entity(project_name: str, sequence_name: str) -> FXShot:
    pass


def get_step_entity(project_name: str) -> FXStep:
    pass


def get_task_entity(project_name: str) -> FXTask:
    pass


def get_asset_entity(project_name: str) -> FXAsset:
    pass
