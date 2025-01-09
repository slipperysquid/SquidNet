# Squidnet - Bot net framework

This project is a basic Python-based Bot net framework for educational and ethical testing purposes. It allows you to establish communication with a remote victim, send commands, and remotely run modules.

**Disclaimer:** This code is provided for educational and research purposes only. The author is not responsible for any misuse of this software. Use it responsibly and ethically, and only on systems you have explicit permission to test.

Special thanks to the discontinued BYOB project for inspiring me!: https://github.com/malwaredllc/byob/blob/master

![alt text](squid.png)

## Features

*   **Multi-Session Handling:** Manage multiple client connections simultaneously.
*   **Reverse Shell:** Spawn a basic reverse TCP shell on the target client.
*   **Modular Design:** Easily extend the framework with new modules.
*   **Dynamic Module Loading:** Load modules from a remote server at runtime.
*   **Basic Command Set:** Includes commands for testing connectivity, changing sessions, and more.
*   **Docker Support:** Run the server in a containerized environment.
*   **Encryption for detection avoidance:** Encrypts payloads and Urls in order to avoid detection.
*   **Dynamic Payload Creation:** Dynamically creates staging payloads for Windows and Linux.
*   **Custom Import Hook:** Custom import hook allows importing python modules through http connection.
*   **Keylogger:** Keylogger for Windows and Linux
*   **Nothing Written to Disk:** Everything is done in memory to avoid detection

## Getting Started

### Prerequisites

*   Python 3.12.X
*   Docker (optional, but recommended)
*   pip

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/slipperysquid/SquidNet.git
    cd SquidNet
    ```

### Setup

2.  **Change config to server's public IP**

### Running with Docker (Recommended)

1.  **Build the Docker image:**

    ```bash
    docker build -t squidnet .
    ```

2.  **Run the server (using host networking for external access):**

    ```bash
    docker run -v ./payload:/app/payload -v ./output:/app/output -it --network host squidnet
    ```

### Running without Docker

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Start the server:**

    ```bash
    python3 server.py
    ```


## Usage

1.  **Server Commands:**

    *   `commands`: List all available commands.
    *   `help <command>`: Get help for a specific command.
    *   `payload`: Create the staging payload to be run on victim computer
    *   `session <session_id>`: Switch to a specific session.
    *   `test-con`: test the connection to a session
    *   `shell`: Spawn a reverse shell
    *   `quit`: Exit the server.
    *   `modules`: List the python modules in the modules directory
    *   `keylogger`: Run a keylogger on the current session

## Future Enhancements

*   **Database Integration:** Store session information, logs, and other data in a database.
*   **Persistence:** Implement mechanisms for client persistence on the target system.
*   **Privilege Escalation:** Add modules for privilege escalation.
*   **Cross-Compilation:** Compile payloads for different operating systems automatically.
*   **Web UI:** Develop a web-based user interface for easier management.


## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to discuss improvements or bug fixes.

## License

This project is licensed under the [GNU](LICENSE) - see the LICENSE file for details.

