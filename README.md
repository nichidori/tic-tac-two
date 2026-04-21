# Tic Tac Two

Play Tic Tac Toe in the terminal over local network.


## Background

This project was made as a submission for [boot.dev](https://boot.dev)'s Back-end Developer Path first personal project course.

When deciding on the theme of the project, I wanted to add some constraints based on what I have been learning on the courses. Up until this point, the lessons have been mostly in Python, so that was the language I went with. The project should also be terminal-based as I intend to minimize focus on building UI. The site has yet to teach HTTP or REST APIs so I did not plan to use external APIs, but I did want to explore some basic networking on Linux. I also wanted to build something that is heavy on logic instead of regular CRUD apps. I challenged myself to avoid using frameworks or third-party libraries as much as possible.

I chose to develop a turn-based game that makes use of sockets to connect between 2 players on the local network. Initially I thought that building a chess game would be a very interesting learning experience, but it may be out of scope of the project as the game logic and edge cases can get rather complex. I then decided that Tic Tac Toe would be a more fitting first project. I remembered seeing an interesting twist on this classic game, a decay mechanic, so I ended up implementing it.


## Features

- Play the classic 3x3 Tic Tac Toe game in the terminal.

- Create and connect to a game server by IP address.

    The game uses sockets to communicate between 2 game clients. The clients can be on the same system or different computers, as long as both are connected over local network, e.g. the same Wi-Fi.

- Decay mechanism.

    To keep the game dynamic, each player can only maintain a maximum number of marks equal to the board size (3). When a player places a new mark exceeding this limit, their oldest mark is automatically removed.


## Tech Stack

- Python : Programming language.
- `uv` : Package manager.

The project uses no external dependencies except `pytest`.

Notable standard libraries:

- `tty` and `termios` : Terminal I/O manipulation (raw mode).
- `socket` : Network communication between clients.
- `selectors` : Non-blocking I/O (handling socket + keyboard).


## Run

To play the game, simply clone the repo and run the `main.py`.

```
# Clone project
git clone https://github.com/nichidori/tic-tac-two.git
cd tic-tac-two

# Use uv to run
uv run main.py

# Or use the convenience script
./run.sh
```

Make sure that Python (at least version `3.12`) and `uv` is installed.

Note: This project uses some Unix-spesific modules, so it would not work on Windows.


## Takeaways

This was my first experience building a project with Python on my own. I surprisingly like the simplicity of the language. I found the dynamic typing approach kind of frightening, coming from a statically-typed language background, but it was definitely refreshing.

This was supposed to be a backend-focused course, but funnily enough I learnt a lot on building a UI from scratch without any framework. I needed to figure out a proper app architecture to split the code of different components based on their responsibility. I soon realized that I need to introduce the concept of screens and navigation, splitting render logic and input handler, and managing key presses and socket events simultaneously to avoid blocking the program.


## Future Improvements

- [ ] Allow custom board size
- [ ] Allow setting port number by user input on server initialization
- [ ] Add settings to enable/disable decay mechanic
- [ ] Add payload ACK