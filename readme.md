# Squidnet - Bot net framework

This project is a basic Python-based Bot net framework for educational and ethical testing purposes. It allows you to establish communication with a remote victim, send commands, and remotely run modules.

**Disclaimer:** This code is provided for educational and research purposes only. The author is not responsible for any misuse of this software. Use it responsibly and ethically, and only on systems you have explicit permission to test.

![alt text](squid.png)

## Features

*   **Multi-Session Handling:** Manage multiple client connections simultaneously.
*   **Reverse Shell:** Spawn a basic reverse TCP shell on the target client.
*   **Modular Design:** Easily extend the framework with new modules.
*   **Dynamic Module Loading:** Load modules from a remote server at runtime.
*   **Basic Command Set:** Includes commands for testing connectivity, changing sessions, and more.
*   **Docker Support:** Run the server in a containerized environment.

## Getting Started

### Prerequisites

*   Python 3.x
*   Docker (optional, but recommended)
*   pip

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Running with Docker (Recommended)

1.  **Build the Docker image:**

    ```bash
    docker build -t squidnet .
    ```

2.  **Run the server (using host networking for external access):**

    ```bash
    docker run -it --network host squidnet
    ```

### Running without Docker

1.  **Start the server:**

    ```bash
    python3 server.py
    ```

### Running the Loader

1. **Modify the loader**
  Modify the `loader.py` file so that the url variable points to your servers ip address. For example:
    ```
    url = f"http://<server_ip>:5001/client.py"
    ```
2.  **Run the loader**

    ```bash
    python3 loader.py
    ```

## Usage

1.  **Server Commands:**

    *   `commands`: List all available commands.
    *   `help <command>`: Get help for a specific command.
    *   `session <session_id>`: Switch to a specific session.
    *   `test-con`: test the connection to a session
    *   `shell`: Spawn a reverse shell (currently requires manual interaction on the client-side to complete the connection, check server logs for the client ip address).
    *   `quit`: Exit the server.

2.  **Client Deployment:**

    *   The `loader.py` script downloads and executes `client.py`. You'll need to modify `loader.py` to point to your server's IP address and port where the module server is running (default: `http://<server_ip>:5001/client.py`).

## Future Enhancements

*   **Complete Reverse Shell Implementation:**  Fully develop the `tcp_shell.py` module.
*   **Windows Payloads:** Add support for Windows clients.
*   **Database Integration:** Store session information, logs, and other data in a database.
*   **Persistence:** Implement mechanisms for client persistence on the target system.
*   **Privilege Escalation:** Add modules for privilege escalation.
*   **Cross-Compilation:** Compile payloads for different operating systems automatically.
*   **Authentication and Encryption:** Secure communication between the server and clients.
*   **Web UI:** Develop a web-based user interface for easier management.


## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to discuss improvements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details. (You'll need to create a LICENSE file and put the MIT License text in it).

