# Dataset Generation

This directory contains the core components for generating the InSDN DDoS dataset. The primary script for this process is `test.py`, which orchestrates the environment setup, traffic generation, and data processing.

## Key Components:

*   **`test.py`**: The main script for dataset generation.
*   **`requirements.txt`**: Lists the Python dependencies required to run `test.py`.
*   **`src/`**: Contains source code modules used by `test.py`, including:
    *   `src/attacks/`: Scripts for generating various DDoS attack traffic.
    *   `src/controller/`: Ryu controller application.
    *   `src/utils/`: Utility functions for PCAP processing and other tasks.
*   **`output/`**: Directory for storing generated PCAP files, CSV outputs, and logs.

For detailed information on the dataset generation process, refer to the `test.py` script and its comprehensive documentation in [TEST.md](TEST.md).
