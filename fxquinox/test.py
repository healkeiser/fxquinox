import entities

project = entities.Project(name="Project")
sequences = [
    entities.Sequence(project=project, name="001"),
    entities.Sequence(project=project, name="002"),
    entities.Sequence(project=project, name="003"),
]
project.sequences = sequences

print(project)
print(str(project))
print(repr(project))

print(project.sequences)
