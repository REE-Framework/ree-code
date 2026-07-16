"""Print the public software mirror of the REE discriminator register."""

from ree.discriminators import list_discriminators

for entry in list_discriminators():
    print(f"{entry.label:4} {entry.programme_status:20} {entry.title}")
