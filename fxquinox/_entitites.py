"""A selection of Python objects that can be used to store data."""

import logging
import string

logger = logging.getLogger(__name__)


def _get_entity_name(raw_data: dict) -> str:
    """This helper function is used to extract the entity name from the raw data during the creation of an entity.

    Args:
        raw_data (dict): The raw data from which the entity name is to be extracted.

    Returns:
        str: The name of the entity.
    """

    name = raw_data.get("code", None)
    if not name:
        name = raw_data.get("name")
    return name


class JFException(Exception):
    pass


class Project(object):
    __slots__ = (
        "name",
        "id",
        "container",
        "renderers",
        "episodes",
        "sequences",
        "assets",
        "shots",
        "publishes",
        "versions",
        "tasks",
        "template",
        "status",
        "type",
        "sg_type",
        "raw_data",
    )

    def __init__(self, name, id_num=0, container_name="", sg_type=""):
        """Initializes the  Project object.

        Args:
            name (str): The project name.
            id_num (int, optional): The project id number. Defaults to `None`.
            container_name (str, optional): The name of the file system container that this project lives in.
                Defaults to `None`.
        """

        self.name = name
        self.id = id_num
        self.container = container_name
        self.renderers = []
        self.episodes = []
        self.sequences = []
        self.assets = []
        self.shots = []
        self.publishes = []
        self.versions = []
        self.tasks = []
        self.template = False
        self.status = ""
        self.type = "Project"
        self.sg_type = sg_type
        self.raw_data = {}

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "Project(name={}, id_num={}, container_name={})".format(self.name, self.id, self.container)


class Renderer(object):
    __slots__ = (
        "name",
        "id",
        "version",
        "install_path",
        "dcc",
        "required_env_var_dict",
    )

    def __init__(self, name):
        """A Renderer object

        :param name: The name of the renderer
        :type name: str
        """
        self.name = name
        self.id = ""
        self.version = ""
        self.install_path = ""
        self.dcc = ""
        # a dict where each key is the var name required and the value is the string to set against that evn var
        self.required_env_var_dict = {}

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "Renderer(name={})".format(self.name)

    def __eq__(self, other):
        return self.name == other.name


class Entity(object):
    """This is the main entity object that we subclass."""

    __slots__ = (
        "project",
        "name",
        "type",
        "sg_type",
        "id",
        "parent",
        "subtype",
        "is_template",
        "publishes",
        "versions",
        "notes",
        "tasks",
        "linked_assets",
        "linked_sequences",
        "linked_episodes",
        "date_created",
        "created_by",
        "date_updated",
        "updated_by",
        "tags",
        "raw_data",
    )

    def __init__(self, project, name, entity_type, id_num=0, parent=None, entity_subtype=""):
        """Initializes the Entity object.

        The main parent class for many  entity objects (E.g. Shots, Assets, Publishes).

        Available methods (see method docstrings for more details):
            * `sort_publishes`
            * `get_latest_publish_for_step`
            * `sort_versions`
            * `get_latest_version_for_step`

        Args:
            project (Project): A  Project object that the entity belongs to.
            name (str): The name of the entity (E.g. the shot code, publish name, version name etc.).
            entity_type (str): The type of entity this is (E.g. Shot, Asset, Publish).
            id_num (int, optional): The Id number in the database for this entity. Defaults to `0`.
            parent (jf entity object, optional): The parent object or entity for this entity (eg for a shot entity the
                parent is often a Sequence or Episode object). Defaults to `None`.
            entity_subtype (str, optional): The entity subtype (E.g. An Asset might have the Character, Prop, or Set
                subtype. Defaults to `""`.
        """

        # Required
        self.project = project
        self.name = name
        self.type = entity_type
        self.sg_type = entity_type

        # Optional
        self.id = id_num
        self.parent = parent
        self.subtype = entity_subtype
        self.is_template = False

        # Lists to that can be populated later
        self.publishes = []
        self.versions = []
        self.notes = []
        self.tasks = []

        # These are for specific entity types
        self.linked_assets = []
        self.linked_sequences = []
        self.linked_episodes = []

        # This if for creation data. These slots would be filled by
        self.date_created = None
        self.created_by = None
        self.date_updated = None
        self.updated_by = None
        self.tags = []

        # This is intended to be a dumping ground for raw pipeline software (eg Shotgun) data
        # eg the results from Shotgun.find() requests etc
        self.raw_data = {}

    @classmethod
    def build(cls, project: Project, raw_data: dict) -> "Entity":
        """Builds an entity object from ShotGrid data.

        Args:
            project (Project): The project entity.
            raw_data (dict): The data from ShotGrid.

        Returns:
            Entity: the entity object.
        """

        name = _get_entity_name(raw_data)
        entity = cls(project, name, raw_data["id"])
        entity.raw_data = raw_data
        entity.sg_type = raw_data["type"]
        return entity

    @staticmethod
    def sort_publishes(publishes):
        """
        Sort the publishes list by name in reverse order (ie latest publish first)
        :param: List of publishes
        :return:
        """

        return publishes.sort(key=lambda x: x.version_number, reverse=True)

    def filter_publish_type(self, publish_type, publish_category, plate, publishes):
        filtered = []
        for pub in publishes:
            if pub.published_file_type == publish_type:
                filtered.append(pub)
            elif pub.category == publish_category:
                filtered.append(pub)
            elif plate and pub.plate_name.lower() == plate.lower():
                filtered.append(pub)

        if not filtered:
            logger.warn(
                "There were no publishes set up on "
                "the  {} object: '{}' of type '{}'".format(self.type, self.name, publish_type)
            )
        return filtered

    def get_publish_for_step(
        self,
        step,
        task_name="",
        published_file_type="",
        publish_category="",
        version=None,
        plate=None,
    ):
        """Get's the latest or specific version publish object from the publishes list that has a step of the same name

        :param step: (str) Step name to find publishes from
        :param task_name: (str) Optional filter to enforce that the task name provided also matches
        :param published_file_type: (str) Optional filter for specific file type. Uses same name as in shotgun.
        :param str publish_category: Optional publish category
        :param version: (int) Optional version number to get specific version publish. None will get latest version.
        :param str plate: Optional name of plate publish linked too

        :return: A  Publish object
        :returns entity_types.Publish
        """

        # create duplicate filtered list, this is to allow for multiple file type filters
        # so the original publishes list is not altered
        filtered_publishes = self.filter_publish_type(published_file_type, publish_category, plate, self.publishes)
        self.sort_publishes(filtered_publishes)

        publish_result = self._get_entity_for_step(filtered_publishes, step, task_name, version)

        if not publish_result:
            logger.warn(
                "No publish match found for step={}, "
                "task={}, publish_file_type={}, version={}".format(step, task_name, filtered_publishes, version)
            )
        return publish_result

    def sort_versions(self):
        """
        Sort the versions list by name in reverse order (ie latest versions first)
        :return:
        """
        self.versions.sort(key=lambda x: x.name.lower().split("_")[-1], reverse=True)

    def get_version_for_step(self, step, task_name="", version=None):
        """Attempts to find the specified version associated with the given step. If no version is specified if will
        find the latest. Task names can be supplied to further filter the version

        :param str step: The name of the step to find a version from
        :param str task_name: Optional - the name of a task to filter versions from a given step from
        :param str version: Optional - a specific version to find

        :return: A  Version instance
        :returns Version
        """

        # sort the versions
        self.sort_versions()
        result = self._get_entity_for_step(self.versions, step, task_name, version)
        if not result:
            logger.warn("No version found for step={}, task={}, version={}".format(step, task_name, version))
        return result

    def _get_entity_for_step(self, entities, step, task_name=None, version=None):
        step = step.lower()
        task = task_name.lower() if task_name else None

        # for each version in the list.
        for entity in entities:
            if not entity.step or not entity.task:
                raise RuntimeError("Task or Step could not be found for {}".format(entity.name))

            if version and entity.version_number != version:
                continue
            # if a task name was provided check that the step name and task name match. if they do return the version
            if task:
                if step == entity.step.name.lower() and task == entity.task.name.lower():
                    return entity
            # if it's just the step name then first compare the step name. then compare the step provided to
            # the task name. If either match return the version found
            else:
                if step == entity.step.name.lower() or step == entity.task.name.lower():
                    return entity
        return None

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}('project={}', name='{}', id={})".format(self.type, self.project, self.name, self.id)


class Shot(Entity):
    __slots__ = (
        "sequence",
        "episode",
        "assets",
        "cut_in",
        "cut_out",
        "handle_in",
        "handle_out",
        "handle_cut_in",
        "handle_cut_out",
        "roll_cut_in",
        "roll_cut_out",
        "roll_count_in",
        "roll_count_out",
        "client_cut_in",
        "client_cut_out",
        "client_name",
        "handle_duration",
        "cut_duration",
        "stage",
        "parent_shots",
        "status",
    )

    def __init__(
        self,
        project,
        name,
        id_num=0,
        parent=None,
        sequence=None,
        episode=None,
        assets=None,
        cut_in=0,
        cut_out=0,
        handle_in=1,
        handle_out=1,
        roll_count_in=0,
        roll_count_out=0,
        stage=None,
        tags=None,
        parent_shots=None,
        client_cut_in=0,
        client_cut_out=0,
        client_name="",
        status=None,
    ):
        """A  Shot object

        :param project: A  project object that the shot belongs too
        :type project: Project

        :param name: The name of the shot
        :type name: str

        :param id_num: (Optional) The Id number of the shot
        :type id_num: int

        :param parent: (Optional) The parent Entity for the shot (eg: Episode or Sequence)
        :type parent: Entity

        :param sequence: (Optional) The Sequence that the shot belongs too
        :type sequence: Sequence

        :param episode: (Optional) A  Episode that the shot belongs too
        :type episode: Episode

        :param assets: (Optional) List of  Assets that belong to the shot
        :type assets: list

        :param cut_in: (Optional) The cut in (frame)
        :type cut_in: int

        :param cut_out: (Optional) The cut out (frame)
        :type cut_out: int

        :param handle_in: (Optional) The handle in (frame)
        :type handle_in: int

        :param handle_out: (Optional) The handle out (frame)
        :type handle_out: int

        :param roll_count_in: (Optional) The count in (frame offset)
        :type roll_count_in: int

        :param roll_count_out: (Optional) The count out (frame offset)
        :type roll_count_out: int

        :param tags: (Optional) Additional shotgun tags
        :type tags: set

        :param parent_shots: (Optional) The parent shots of the current shot
        :type parent_shots: list

        :param client_cut_in: (Optional) The client cut in of a shot
        :type client_cut_in: int

        :param client_cut_out: (Optional) The client cut out of a shot
        :type client_cut_out: int

        :param client_name: (Optional) The client name of a shot
        :type client_name: str

        :return None
        :returns None
        """

        super(Shot, self).__init__(project, name, "Shot", id_num, parent=parent)

        self.sequence = sequence
        if self.sequence:
            self.linked_sequences.append(self.sequence)

        self.episode = episode
        if self.episode:
            self.linked_episodes.append(self.episode)

        self.assets = assets

        # set the cut in and out
        if cut_in is None or cut_out is None:
            raise RuntimeError(
                "The 'Cut In' and/or 'Cut Out' for the shot has not been set in shotgun, "
                "please ensure these are set correctly for shot %s" % name
            )

        self.tags = tags or []
        self.stage = stage

        self.parent_shots = parent_shots
        self.client_name = client_name
        self._update_edit_attr(
            cut_in,
            cut_out,
            client_cut_in,
            client_cut_out,
            handle_in,
            handle_out,
            roll_count_in,
            roll_count_out,
        )

    def _update_edit_attr(
        self,
        cut_in,
        cut_out,
        client_cut_in,
        client_cut_out,
        handle_count_in,
        handle_count_out,
        roll_count_in,
        roll_count_out,
    ):
        self.cut_in = cut_in
        self.cut_out = cut_out

        self.client_cut_in = client_cut_in if client_cut_in else self.cut_in
        self.client_cut_out = client_cut_out if client_cut_in else self.cut_out

        project_handles_in = self.project.raw_data.get("sg_handles_in")
        if project_handles_in and handle_count_in == 1:
            self.handle_in = int(project_handles_in)
        else:
            self.handle_in = handle_count_in

        project_handles_out = self.project.raw_data.get("sg_handles_out")
        if project_handles_out and handle_count_out == 1:
            self.handle_out = int(project_handles_out)
        else:
            self.handle_out = handle_count_out

        self.handle_cut_in = self.cut_in - self.handle_in
        self.handle_cut_out = self.cut_out + self.handle_out

        self.roll_count_in = roll_count_in
        self.roll_count_out = roll_count_out

        self.roll_cut_in = self.handle_cut_in - self.roll_count_in
        self.roll_cut_out = self.handle_cut_out + self.roll_count_out

        # calculate the cut and handle durations
        self.cut_duration = self.cut_out - self.cut_in + 1
        self.handle_duration = self.handle_cut_out - self.handle_cut_in + 1

    @classmethod
    def build(cls, project, raw_data):
        name = _get_entity_name(raw_data)

        assets = raw_data.get("assets", []) or []

        sequence = raw_data.get("sg_sequence", None)
        jf_sequence = Sequence.build(project, sequence) if sequence else None

        episode = raw_data.get("sg_episode", None)
        jf_episode = Episode.build(project, episode) if episode else None
        parent = jf_sequence or jf_episode or None

        entity = cls(project, name, id_num=raw_data["id"], parent=parent)
        entity.sg_type = raw_data["type"]
        if assets:
            entity.assets = [Asset.build(project, asset) for asset in assets]
        entity.sequence = jf_sequence
        entity.episode = jf_episode
        if jf_episode and jf_sequence:
            entity.parent = jf_sequence
        elif jf_episode and not jf_sequence:
            entity.parent = jf_episode
        elif jf_sequence and not jf_episode:
            entity.parent = jf_sequence
        entity.client_name = raw_data.get("sg_client_shot_name", "") or ""
        entity.status = raw_data.get("sg_status_list", None)
        entity.raw_data = raw_data
        cut_in = raw_data.get("sg_cut_in", 0) or 0
        cut_out = raw_data.get("sg_cut_out", 0) or 0
        handle_count_in = raw_data.get("sg_handle_count_in", 1) or 1
        handle_count_out = raw_data.get("sg_handle_count_out", 1) or 1
        roll_count_in = raw_data.get("sg_roll_count_in", 1) or 1
        roll_count_out = raw_data.get("sg_roll_count_out", 1) or 1
        client_cut_in = raw_data.get("sg_client_cut_in", None) or None
        client_cut_out = raw_data.get("sg_client_cut_out", 1) or 1
        entity._update_edit_attr(
            cut_in,
            cut_out,
            client_cut_in,
            client_cut_out,
            handle_count_in,
            handle_count_out,
            roll_count_in,
            roll_count_out,
        )
        entity.tags = raw_data.get("tags", []) or []
        return entity

    def get_latest_publish_cache_for_step(self, cache_name, step, task_name=""):
        """
        Get the latest Alembic Cache publish for a specific cache for a given step and or task
        :param str cache_name: specific name of cache to find publish for, e.g. testAssetA_testAssetA_Rigging4
        :param str step: step name to find publish for
        :param str task_name: task name to find publish for
        :return: Publish entity for latest publish
        """
        sorted_publishes = self.publishes
        self.sort_publishes(sorted_publishes)
        filtered_publishes = [
            publish
            for publish in sorted_publishes
            if cache_name in publish.name and publish.published_file_type == "Alembic Cache"
        ]

        result = self._get_entity_for_step(filtered_publishes, step, task_name)
        if not result:
            logger.warn("Publish not found for cache={}".format(cache_name))
        return result


class Asset(Entity):
    def __init__(self, project, name, id_num=0, asset_type=""):
        """A  Asset object

        :param project: The project the asset belongs to
        :type project: Project

        :param name: The name of the asset
        :type name: str

        :param id_num: Optional - The id number of the asset
        :type id_num: int

        :param asset_type: Optional - The type of the asset
        :type asset_type: str
        """

        super(Asset, self).__init__(project, name, "Asset", id_num)
        # set the asset type to the subtype of this entity
        self.subtype = asset_type

        # if template is in the type name then set the is_template attribute to True
        if "template" in self.subtype.lower():
            self.is_template = True

        # set a cut in/out for assets (this is used on AnimCycles
        self.cut_in = 0
        self.cut_out = 0

    @classmethod
    def build(cls, project, raw_data):
        name = _get_entity_name(raw_data)
        asset_type = raw_data.get("sg_asset_type", "") or ""
        entity = cls(project, name, id_num=raw_data["id"], asset_type=asset_type)
        entity.raw_data = raw_data
        entity.sg_type = raw_data["type"]
        return entity

    def get_highest_lod(self, step, task_basename):
        """
        Gets the highest Level of detail publish object for the asset.

        It is assumed that the task_basename is the prefix to an Alphabetised test of tasks where the later the letter
        in the alphabet the higher the LOD.

        :param string step: The name of the step the base tasks belong too

        :param string task_basename: The prefix for the LOD task sequence. EG 'Rigging' for LOD's 'RiggingA',
        'RiggingB', 'RiggingC' etc

        :return: Publish
        """
        highest_lod = None

        for letter in string.ascii_uppercase:
            # get the latest lod publish for current letter
            lod_publish = self.get_publish_for_step(step, task_name="%s%s" % (task_basename, letter))
            if lod_publish:
                highest_lod = lod_publish

        if not highest_lod:
            highest_lod = self.get_publish_for_step(step, task_basename)
        return highest_lod


class AssetInstance(Entity):
    __slots__ = ("shot", "asset", "status", "tags", "index", "active")

    def __init__(self, project, name, id_num=0):
        """A  Asset object

        :param project: The project the asset belongs to
        :type project: Project

        :param name: The name of the asset
        :type name: str

        :param id_num: Optional - The id number of the asset
        :type id_num: int
        """

        super(AssetInstance, self).__init__(project, name, "AssetInstance", id_num)
        self.status = ""
        self.shot = None
        self.asset = None
        self.tags = []
        self.index = None
        self.active = None

    @classmethod
    def build(cls, project, raw_data):
        name = _get_entity_name(raw_data)
        entity = cls(project, name, id_num=raw_data["id"])
        entity.raw_data = raw_data
        entity.created_by = raw_data.get("created_by", "") or ""
        entity.tags = raw_data.get("tags", []) or []
        entity.sg_type = raw_data["type"]
        entity.active = raw_data["sg_active"]
        entity.index = raw_data["sg_index"]
        shot = raw_data.get("sg_shot", None)
        if shot:
            entity.shot = Shot.build(project, shot)
        asset = raw_data.get("sg_asset", None)
        if asset:
            entity.asset = Asset.build(project, asset)
        return entity


class Sequence(Entity):
    __slots__ = ("shots", "assets", "episode")

    def __init__(self, project, name, id_num=0, parent=None):
        """A  Sequence object

        :param project: a  project object
        :type project: Project

        :param name: The name of the sequence
        :type name: str

        :param id_num: (Optional) The id for the sequence
        :type id_num: int

        :param parent: (Optional) The parent entity for the sequence(Eg:  Episode or  Project)
        :type parent: Entity
        """

        super(Sequence, self).__init__(project, name, "Sequence", id_num, parent=parent)
        self.shots = []
        self.assets = []
        self.episode = None

    @classmethod
    def build(cls, project, raw_data):
        name = _get_entity_name(raw_data)
        episode = raw_data.get("episode", None)
        jf_episode = Episode.build(project, episode) if episode else None
        parent = jf_episode or project
        entity = cls(project, name, raw_data["id"], parent=parent)
        entity.episode = jf_episode
        entity.sg_type = raw_data["type"]

        shots = raw_data.get("shots", None)
        if shots:
            entity.shots = [Shot.build(project, shot) for shot in shots]
        assets = raw_data.get("assets", None)
        if assets:
            entity.assets = [Asset.build(project, asset) for asset in assets]
        entity.raw_data = raw_data
        return entity


class Episode(Entity):
    __slots__ = ("shots", "assets", "sequences")

    def __init__(self, project, name, id_num=0, parent=None):
        """Episode object

        :param project: A  Project object
        :type project: Project

        :param name: The name of the episode
        :type name: str

        :param id_num: (Optional) The id for the episode
        :type id_num: int

        :param parent: (Optional) The parent entity for the episode(Eg:  Project)
        :type parent: Entity
        """

        super(Episode, self).__init__(project, name, "Episode", id_num, parent=parent)
        self.shots = []
        self.assets = []
        self.sequences = []

    @classmethod
    def build(cls, project, raw_data):
        name = _get_entity_name(raw_data)
        entity = cls(project, name, raw_data["id"], parent=project)
        sequences = raw_data.get("sequences", None)
        shots = raw_data.get("sg_shots", None)
        assets = raw_data.get("assets", None)
        if sequences:
            entity.sequences = [Sequence.build(project, seq) for seq in sequences]
        if shots:
            entity.shots = [Shot.build(project, shot) for shot in shots]
        if assets:
            entity.assets = [Asset.build(project, asset) for asset in assets]
        entity.raw_data = raw_data
        entity.sg_type = raw_data["type"]
        return entity


class Publish(Entity):
    __slots__ = (
        "windows_file_path",
        "linked_versions",
        "version_number",
        "step",
        "task",
        "description",
        "published_file_type",
        "category",
        "path_cache",
        "plate_name",
    )

    def __init__(
        self,
        project,
        name,
        id_num=0,
        step=None,
        task=None,
        windows_file_path="",
        linked_versions=None,
        version_number=0,
        category=None,
        plate_name="",
    ):
        """A  Publish object

        :param project: A  Project object
        :type project: Project

        :param name: The name of the publish
        :type name: str

        :param id_num: (Optional) The id number for the publish
        :type id_num: int

        :param step: (Optional) A  Step object
        :type step: Step

        :param task: (Optional) A  Task object
        :type task: Task

        :param windows_file_path: (Optional) A path to where the publish file is
        :type windows_file_path: str

        :param linked_versions: (Optional) A list of Linked  Version entities
        :type linked_versions: list

        :param version_number: (Optional)  A version number associated with the publish
        :type version_number: int

        :param category: A name from sg_category field for Shotgun database
        :type category: str

        :param str plate_name: (Optional) Name of the plate the publish is for
        """

        super(Publish, self).__init__(project, name, "Publish", id_num=id_num)

        # todo: just have file path (that can work out and select the right path based on the current os)
        self.windows_file_path = windows_file_path

        self.linked_versions = linked_versions or []
        self.version_number = version_number

        self.step = step
        self.task = task

        self.description = ""
        self.published_file_type = None
        self.path_cache = ""

        self.category = category
        self.plate_name = plate_name

    @classmethod
    def build(cls, project, raw_data):
        name = _get_entity_name(raw_data)
        # I'm peppering in several 'or' statements here to account for returned-but-empty fields, and so provide
        # the same default value as if they'd not been requested (e.g. raw_data.get("something", default_val))
        path = raw_data.get("path", "") or ""
        windows_path = ""
        if path:
            windows_path = path.get("local_path_windows", "") or ""
        version = raw_data.get("version_number", 0) or 0
        entity = cls(
            project,
            name,
            id_num=raw_data["id"],
            windows_file_path=windows_path,
            version_number=version,
        )
        entity.raw_data = raw_data
        task = raw_data.get("task", None)
        if task:
            entity.task = Task.build(project, task)
            if entity.task.step:
                entity.step = entity.task.step
        version = raw_data.get("version", None)
        if version:
            entity.linked_versions.append(Version.build(project, version))
        entity.description = raw_data.get("description", "") or ""
        published_file_type = raw_data.get("published_file_type", {}) or {}
        entity.published_file_type = published_file_type.get("name", "") if published_file_type else ""
        entity.path_cache = raw_data.get("path_cache_storage", "") or ""
        publish_category = raw_data.get("sg_publish_category", {}) or {}
        entity.category = publish_category.get("name", "") if publish_category else ""
        entity.sg_type = raw_data["type"]

        created_by = raw_data.get("created_by", {}) or {}
        entity.created_by = User(name=created_by.get("name", ""), id_num=created_by.get("id", 0))
        entity.plate_name = raw_data.get("sg_plate_name", "") or ""
        entity.date_created = raw_data.get("created_at", None)
        return entity

    def version_num_as_padded_string(self, padding=3):
        """Converts the version number into a padded string

        :param padding: The amount of padding to add
        :type padding: int

        :return: The padded version string
        :returns str
        """
        return "{}".format(self.version_number).zfill(padding)

    def get_publish_for_step(
        self,
        step,
        task_name="",
        published_file_type="",
        publish_category="",
        plate=None,
        version=None,
    ):
        raise JFException("You can't get a latest publish of a publish!")


class Cut(Entity):
    __slots__ = (
        "revision_number",
        "description",
        "cut_items",
        "duration",
        "fps",
        "open_notes",
        "status",
        "cut_type",
        "attachments",
    )

    def __init__(
        self,
        project,
        name,
        id_num=0,
        cut_items=None,
        tags=None,
        parent=None,
        # add all params
    ):
        super(Cut, self).__init__(project, name, "Cut", id_num=id_num, parent=parent)
        self.revision_number = None
        self.description = ""
        self.cut_items = cut_items
        self.duration = None
        self.fps = None
        self.open_notes = ""
        self.status = ""
        self.cut_type = ""
        self.attachments = ""
        self.tags = tags or []

    @classmethod
    def build(cls, project, raw_data):
        name = _get_entity_name(raw_data)
        tags = raw_data.get("tags", []) or []
        raw_parent = raw_data.get("entity")
        raw_cut_items = raw_data.get("cut_items")
        try:
            parent = globals().get(raw_parent.get("type")).build(project, raw_parent)
        except AttributeError:
            parent = raw_parent
        cut_items = []
        if raw_cut_items:
            cut_items = raw_cut_items

        entity = cls(project, name, id_num=raw_data["id"], cut_items=cut_items, tags=tags, parent=parent)
        entity.raw_data = raw_data
        entity.revision_number = raw_data.get("revision_number")
        entity.description = raw_data.get("description")
        entity.duration = raw_data.get("duration")
        entity.fps = raw_data.get("fps")
        entity.open_notes = raw_data.get("open_notes")
        entity.status = raw_data.get("sg_status_list")
        entity.cut_type = raw_data.get("sg_cut_type")
        entity.attachments = raw_data.get("attachments")
        return entity


class Version(Entity):
    __slots__ = (
        "frames_resolution",
        "first_frame",
        "frame_range",
        "last_frame",
        "path_to_frames",
        "path_to_mov",
        "path_to_proxy",
        "path_to_folder",
        "path_to_geometry",
        "linked_publishes",
        "step",
        "task",
        "status",
        "stage",
    )

    def __init__(
        self,
        project,
        name,
        id_num=0,
        step=None,
        task=None,
        linked_publishes=None,
        status=None,
        stage=None,
        tags=None,
        parent=None,
    ):
        """A  Version entity
        :param project: The Project that the version belongs to
        :type project: Project

        :param name: The name of the Version
        :type name: str

        :param id_num: Optional - The id number of the Version
        :type id_num: int

        :param step: Optional - The Step associated with this Version
        :type step: Step

        :param task: Optional - The Task associated with this Version
        :type task: Task

        :param linked_publishes: Optional - The Publishes associated with this Version
        :type linked_publishes: list

        :param status: Optional - The sg_status_list of this version
        :type linked_publishes: list

        :param stage: Optional - The sg_stage of this version
        :type linked_publishes: list

        :param tags: Optional - The tags of this version
        :type tags: set

        :param parent: Optional - The parent entity for the Version
        :type parent: dict
        """

        super(Version, self).__init__(project, name, "Version", id_num=id_num, parent=parent)

        self.first_frame = ""
        self.frame_range = ""
        self.last_frame = ""
        self.path_to_frames = ""
        self.path_to_proxy = ""
        self.path_to_mov = ""
        self.path_to_folder = ""
        self.path_to_geometry = ""
        self.linked_publishes = linked_publishes or []
        self.step = step
        self.task = task
        self.status = status
        self.stage = stage
        self.tags = tags or []

    @classmethod
    def build(cls, project, raw_data):
        name = _get_entity_name(raw_data)
        stage = raw_data.get("sg_stage", None)
        tags = raw_data.get("tags", []) or []
        raw_parent = raw_data.get("entity")
        try:
            parent = globals().get(raw_parent.get("type")).build(project, raw_parent)
        except AttributeError:
            parent = raw_parent

        entity = cls(project, name, id_num=raw_data["id"], stage=stage, tags=tags, parent=parent)
        entity.raw_data = raw_data
        entity.created_by = raw_data.get("created_by", "") or ""
        entity.frames_resolution = raw_data.get("sg_frames_resolution", "") or ""
        entity.first_frame = raw_data.get("sg_first_frame", "") or ""
        entity.frame_range = raw_data.get("frame_range", "") or ""
        entity.last_frame = raw_data.get("sg_last_frame", "") or ""
        entity.path_to_mov = raw_data.get("sg_path_to_movie", "") or ""
        entity.path_to_geometry = raw_data.get("sg_path_to_geometry", "") or ""
        entity.path_to_frames = raw_data.get("sg_path_to_frames", "") or ""
        entity.path_to_proxy = raw_data.get("sg_path_to_proxy", "") or ""
        entity.path_to_folder = raw_data.get("sg_path_to_folder", "") or ""
        entity.status = raw_data.get("sg_status_list", "") or ""
        entity.sg_type = raw_data["type"]
        task = raw_data.get("sg_task", None)
        if task:
            entity.task = Task.build(project, task)
            if entity.task.step:
                entity.step = entity.task.step
        publishes = raw_data.get("published_files", None)
        if publishes:
            entity.linked_publishes = [Publish.build(project, publish) for publish in publishes]
        return entity


class Playlist(Entity):
    __slots__ = ("description", "versions")

    def __init__(self, project, name, id_num=0, description=None, versions=None):
        """A  Playlist entity.

        :param Project project: The Project that the playlist belongs to.
        :param str name: The name of the playlist.
        :param int id_num: Optional - The id number of the playlist.
        :param str description: Optional - The description of the playlist.
        :param list versions: Optional - The versions of the playlist.
        """
        super(Playlist, self).__init__(project, name, "Playlist", id_num=id_num)
        self.description = description or ""
        self.versions = versions or []

    @classmethod
    def build(cls, project, raw_data):
        name = _get_entity_name(raw_data)
        description = raw_data.get("description", "") or ""
        entity = cls(project, name, id_num=raw_data["id"], description=description)
        entity.raw_data = raw_data

        versions = raw_data.get("versions", None)
        if versions:
            entity.versions = [Version.build(project, version) for version in versions]

        created_by = raw_data.get("created_by", {}) or {}
        entity.created_by = User.build(created_by) if created_by else None

        updated_by = raw_data.get("updated_by", {}) or {}
        entity.updated_by = User.build(updated_by) if updated_by else None

        entity.tags = raw_data.get("tags", []) or []
        return entity


class Task(Entity):
    __slots__ = (
        "step",
        "status_code",
        "start_date",
        "end_date",
        "stage",
        "assigned_to",
    )

    def __init__(self, project, name, id_num=0, parent=None, step=None, status_code=""):
        """A  pipeline Task object
        :param project: The project that this Task belongs to
        :type project: Project

        :param name: The name of the Task
        :type name: str

        :param id_num: Optional - The id number for the Task
        :type id_num: int

        :param parent: Optional - The parent for the Task
        :type parent: Entity

        :param parent: Optional - The parent step for the Task
        :type step: Step

        :param status_code: Optional - The status code for the task
        :type status_code: str
        """

        super(Task, self).__init__(project, name, entity_type="Task", id_num=id_num, parent=parent)

        self.step = step
        self.status_code = status_code
        self.start_date = None
        self.end_date = None
        self.stage = None

        # can be populated with User objects
        self.assigned_to = []

    @classmethod
    def build(cls, project, raw_data):
        name = raw_data.get("content", None)
        if not name:
            name = raw_data.get("name", None)
        sg_parent = raw_data.get("entity", None)
        parent = None
        if sg_parent:
            if sg_parent["type"] == "Shot":
                parent = Shot.build(project, sg_parent)
            elif sg_parent["type"] == "Asset":
                parent = Asset.build(project, sg_parent)

        entity = cls(project, name, id_num=raw_data["id"], parent=parent)
        step = raw_data.get("step", None)
        if step:
            entity.step = Step.build(step)
        entity.raw_data = raw_data
        entity.status_code = raw_data.get("sg_status_list", "") or ""
        assignees = raw_data.get("task_assignees", []) or []
        entity.assigned_to = [User.build(assignee) for assignee in assignees]
        entity.start_date = raw_data.get("start_data", None)
        entity.end_date = raw_data.get("due_date", None)
        entity.stage = raw_data.get("sg_stage", None)
        entity.sg_type = raw_data["type"]
        return entity


class Step(object):
    __slots__ = (
        "name",
        "id",
        "short_name",
        "for_entity_type",
        "tasks",
        "raw_data",
    )

    def __init__(self, name, id_num=0, short_name="", for_entity_type=""):
        """A  pipeline Step object

        :param name: The name of the Step
        :type name: str

        :param id_num: The id for the Step
        :type id_num: int

        :param short_name: The short code or name for the step
        :type short_name: str

        :param for_entity_type: The type of entity that this step can be used for
        :type for_entity_type: str
        """
        self.name = name
        self.id = id_num
        self.short_name = short_name
        self.for_entity_type = for_entity_type

        # can be populated with Task objects
        self.tasks = []
        self.raw_data = {}

    @classmethod
    def build(cls, raw_data):
        name = raw_data.get("code", None)
        if not name:
            name = raw_data.get("name", "") or ""
        short_name = raw_data.get("short_name", "") or ""
        entity_type = raw_data.get("entity_type", "") or ""
        entity = cls(
            name,
            id_num=raw_data["id"],
            short_name=short_name,
            for_entity_type=entity_type,
        )
        entity.raw_data = raw_data
        return entity

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "Step(name='{}', id={})".format(self.name, self.id)


class TaskTemplate(object):
    def __init__(self, name, id_num=0):
        """A  TaskTemplate object

        :param name: The name of the task template
        :type name: str
        """

        self.name = name
        self.id = id_num
        self.type = "TaskTemplate"

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        id_num = "" if self.id == 0 else ", id_num={}".format(self.id)
        return "TaskTemplate('{}{}')".format(self.name, id_num)


class PublishCategory(object):
    __slots__ = ("name", "id", "description", "type")

    def __init__(self, name, id_num=0):
        """A  PublishCategory object

        :param name: The name of the Category
        :type name: str
        """

        self.name = name
        self.id = id_num
        self.description = ""
        self.type = "PublishCategory"

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "PublishCategory('name={}, id={}')".format(self.name, id)


class User(object):
    __slots__ = (
        "name",
        "first_name",
        "last_name",
        "login",
        "id",
        "type",
        "assigned_projects",
        "assigned_tasks",
        "permission_level",
        "raw_data",
        "email",
    )

    def __init__(self, name, first_name="", last_name="", login="", id_num=0, email=""):
        """A  User object

        :param name: The name of the user
        :type name: str

        :param first_name: Optional - The first name of the user
        :type first_name: str

        :param last_name: Optional - The last name of the user
        :type last_name: str

        :param login: Optional - The login string for the user
        :type login: str

        :param id_num: Optional - The Id of the user in the database
        :type id_num: int

        :param email: Optional - The email of the user
        :type email: str
        """

        self.name = name
        self.first_name = first_name
        self.last_name = last_name
        self.login = login or "{}.{}".format(first_name, last_name)
        self.id = id_num

        self.type = "User"
        self.assigned_projects = []
        self.assigned_tasks = []
        self.permission_level = ""
        self.raw_data = {}
        self.email = email or "{}.{}@jellyfishpictures.co.uk".format(first_name, last_name)

    @classmethod
    def build(cls, raw_data):
        name = raw_data.get("name", "")
        login = raw_data.get("login", "")
        firstname = raw_data.get("firstname", "")
        lastname = raw_data.get("lastname", "")
        email = raw_data.get("email", "")
        entity = cls(
            name,
            first_name=firstname,
            last_name=lastname,
            login=login,
            id_num=raw_data["id"],
            email=email,
        )
        permission_rule_set = raw_data.get("permission_rule_set", {})
        entity.permission_level = permission_rule_set.get("name", "")
        entity.raw_data = raw_data
        projects = raw_data.get("projects", None)
        if projects:
            entity.assigned_projects = [Project(project["name"], id_num=project["id"]) for project in projects]
        return entity

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "User(name='{}', id={})".format(self.name, self.id)


class Note(object):
    __slots__ = ("subject", "note", "from_user", "to_user", "id")

    def __init__(self, subject, note, from_user, id_num=0, to_user=None):
        """A  Note object
        :param subject:
        :param note:
        :param from_user:
        :param id_num:
        :param to_user:
        """
        self.subject = subject
        self.note = note
        self.from_user = from_user
        self.to_user = to_user
        self.id = id_num

    def __str__(self):
        return "{}".format(self.subject)

    def __repr__(self):
        return "Note('{}'{})".format(self.subject, self.id)


class Software(object):
    def __init__(self, name, major_version=0, minor_version=0, patch_version=0, path_to_exe=""):
        """A  software (eg Maya, Nuke, Photoshop etc) object

        :param name: The name of the software
        :type name: str

        :param major_version: The major version of the software
        :type major_version: int

        :param minor_version: The minor version of the software
        :type minor_version: int

        :param patch_version: The patch version of the software
        :type patch_version: int

        :param path_to_exe: The path to the executable for the software
        :type path_to_exe: str
        """

        self.name = name.lower()
        self.major_version = major_version
        self.minor_version = minor_version
        self.patch_version = patch_version
        self.path_to_exe = path_to_exe
        self.path_to_batch_exe = ""

    def derive_common_exe_path(self):
        # type: ()->str
        """
        Attempts to derive the exe path from the variables supplied.
        :return: Path to the exe
        :returns: str
        """
        if self.name.lower() == "maya":
            self.path_to_exe = r"C:\Program Files\Autodesk\Maya{}\bin\maya.exe".format(self.major_version)
            self.path_to_batch_exe = r"C:\Program Files\Autodesk\Maya{}\bin\mayabatch.exe".format(self.major_version)

        if self.name.lower() == "nuke":
            self.path_to_exe = r"C:\Program Files\Nuke{major}.{minor}v{patch}\Nuke{major}.{minor}.exe".format(
                major=self.major_version,
                minor=self.minor_version,
                patch=self.patch_version,
            )

        return self.path_to_exe


class PipelineConfiguration(object):
    __slots__ = (
        "name",
        "windows_path",
        "id",
        "project",
        "plugins",
        "descriptor",
        "plugin_ids",
        "env_def_repo_branch",
        "env_def_repo_path",
        "env_def_repo_version",
        "jftoolkit_repo",
        "jftoolkit_repo_branch",
        "jftoolkit_repo_version",
        "type",
        "raw_data",
    )

    def __init__(
        self,
        name,
        id_num=0,
        project="",
        windows_path="",
        descriptor="",
        plugin_ids="",
        env_def_repo_path="",
        env_def_repo_branch="",
        env_def_repo_version="",
        jftoolkit_repo="",
        jftoolkit_repo_branch="",
        jftoolkit_repo_version="",
    ):
        """A  PipelineConfiguration object

        :param str name: The name of the PipelineConfiguration

        :param int id_num: The id for the PipelineConfiguration

        :param Project project: The project entity of the PipelineConfiguration

        :param str windows_path: The windows path for a centralised config

        :param str descriptor: The descriptor of the config location for a distributed config

        :param str plugin_ids: The unique identifier for the specific configuration on disk

        :param str env_def_repo_branch: The branch to use for the environment definitions

        :param str env_def_repo_path: The .git repo location for the environment definitions repo
        """

        self.name = name
        self.windows_path = windows_path
        self.id = id_num
        self.project = project
        self.plugin_ids = plugin_ids
        self.descriptor = descriptor
        self.env_def_repo_branch = env_def_repo_branch
        self.env_def_repo_path = env_def_repo_path
        self.env_def_repo_version = env_def_repo_version
        self.jftoolkit_repo = jftoolkit_repo
        self.jftoolkit_repo_branch = jftoolkit_repo_branch
        self.jftoolkit_repo_version = jftoolkit_repo_version
        self.type = "PipelineConfiguration"
        self.raw_data = {}
