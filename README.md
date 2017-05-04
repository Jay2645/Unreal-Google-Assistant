# Unreal Engine 4 Google Assistant

This is a full project which aims to integrate the [Google Assistant SDK](https://developers.google.com/assistant/sdk/) into Unreal Engine 4.

## Why would I want to use this?

The idea is twofold: Players can either control things inside the game with their voice *or* things in the game could have an effect in "real life". Here's a couple examples:

* A chess game where you control the pieces by saying "Knight to B5."

* A game called Space Marine: Evolved Combat where (in the game) you walk up to a console and insert your AI helper Jortana. Then (in real life), you can give Jortana commands like "Hack into the light bridge array" and the (ingame) Jortana will do stuff in the game based on your voice input.

* A game where when you get hit, the lights in your (real-life) game room slowly dim and turn red, then return to normal as you get healthy again.

* A game with a Robotic helper (using Raspberry Pi) that does things in real life as you play the game, like [R.O.B. on the NES](https://www.youtube.com/watch?v=ocrTkuPMmvI).

* A D&D-like game where you can give your character ***any*** command, like "Tell a joke to the giant monster" and see your actions play out on the screen without needing to map 20 bazillion inputs or have the player type the command out.

You can do anything that a Google Home can do, so as the functionality of things that work with Google Home expands, you can expand as well. You can also take advantage of [Actions on Google](https://docs.api.ai/docs/actions-on-google-integration) to design even more things, referencing your Actions on Google API directly from the game itself.

## Getting Setup

I'm still working on this bit. There are a couple steps needed to get it working:

1. You need to have [Unreal Engine Python](https://github.com/20tab/UnrealEnginePython) installed and configured. It's included as a submodule in this repository, but it took some configuration for me to get it working properly, and I'm not sure whether these changes will work outside of my personal Ubuntu machine that I develop on. Since this is a full project, I would clone this project first and try to get Unreal Engine Python's example program working first (it's in their README).

2. You need to follow the [Google Assistant Raspberry Pi setup instructions](https://developers.google.com/assistant/sdk/prototype/getting-started-pi-python/config-dev-project-and-account) to install Google Assistant via Python and make sure everything is working properly. Mostly, you need to play around with the Cloud Platform Console and get Google OAuth working. Don't bother making a virtual environment; you want pip to install the Google Assistant dependencies into your Python 3 directory, as we need to access them in Unreal. Mainly, we need to be able to access grpc, which for me installed to '~/.local/lib/python3.5/site-packages'. I haven't tested this in Windows yet, so I don't know where it gets installed to in Windows.

3. Place the client secret JSON file in `Content/Scripts/assistant_credentials.json`. When the project first loads, it'll find this file and open a web browser, where you can give your Google Assistant project access to your Google account.

## Using the Project

Once that is done, you should be able to see the Python scripts inside the `Content/Scripts` folder. Right now, there's only a test class, helpfully named `testclass.py`. There should already be a Blueprint set up in the `Content` directory called `TestPyActor`. This is a normal PyActor class (found in the UnrealEnginePython project), with a Python Module `testclass` and a Python Class `Hero`.

If everything goes right, your game ***should*** freeze for 5-6 seconds when you hit play. Your microphone is enabled while the game is frozen (there's no multithreading yet). If you talk during this time, it'll be sent to Google's servers and the Google Assistant will reply back to you. Try testing it with "Tell me a joke".

Bear in mind that at the moment, it uses your **system's** microphone and speakers -- NOT anything in Unreal.

## To-Do

* Use the `uobject.play_sound_at_location()` class to play sound rather than directly out of the computer's speakers.

* (Tangentally related): Create a helper class which converts from Python structures (like the wave module) into Unreal structures (a USoundWave or a  USoundWaveProcedural).

* Move microphone input onto a separate thread to stop it locking the game thread waiting for input

* Allow activation of the Google Assistant by pressing a button

* Expose common functions to Blueprint, allowing Blueprint access to the Google Assistant

Feel free to fork and submit pull requests as needed, if there's any functionality you want to add. This is still very early in development, so there's a lot to do still before it's ready for prime-time.
