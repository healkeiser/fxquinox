from . import entities  # Issue there


class Project:
    def __init__(self, name, start_date, end_date):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.sequences = []

    def add_sequences(self, sequence: entities.Sequence):
        self.sequences.append(sequence)


class Sequence(Project):
    def __init__(self, name, duration, start_date, end_date):
        super().__init__(name, start_date, end_date)
        self.duration = duration
        self.shots = []

    def add_shots(self, shot: entities.Shot):
        self.shots.append(shot)


class Shot(Sequence):
    def __init__(self, name, duration, start_date, end_date):
        super().__init__(name, duration, start_date, end_date)
        self.sequence = None

    def set_sequence(self, sequence: entities.Sequence):
        self.sequence = sequence


class Step(Shot):
    def __init__(self, name, duration, start_date, end_date):
        super().__init__(name, duration, start_date, end_date)


class Task(Step):
    def __init__(self, name, duration, start_date, end_date):
        super().__init__(name, duration, start_date, end_date)


class Asset(Shot):
    def __init__(self, name, asset_type):
        super().__init__(name, asset_type)
        self.name = name
        self.asset_type = asset_type
