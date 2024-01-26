import os

for speech in os.listdir("data/sounds/speech"):
    for name in os.listdir(os.path.join("data/sounds/speech", speech)):
        os.rename(os.path.join("data/sounds/speech", speech, name),
                  os.path.join("data/sounds/speech", speech, name).lower())
for name in os.listdir("data/music/victory"):
    os.rename(os.path.join("data/music/victory", name),
              os.path.join("data/music/victory", name).lower())
