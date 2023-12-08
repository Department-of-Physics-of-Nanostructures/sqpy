# Description
This project is a Python-based terminal application designed for managing and interacting with SLURM jobs. It provides a user-friendly interface to view, navigate, and manage SLURM job queues using a curses based graphical interface. Features include viewing job details, cancelling jobs, and refreshing job lists, all through a convenient text-based interface.

The program leverages Python's curses library for the terminal UI, subprocess for interacting with SLURM commands, and follows object-oriented programming principles for modular and maintainable code.

# Features
View SLURM job queues in a structured, table-like format.
Navigate through the job list with keyboard controls.
Cancel jobs with a confirmation dialog.
Refresh job list dynamically.
Popup windows for displaying messages and confirmations.

## Installation
To install this application, you can use the following command:

```bash
pip install sqpy
```

## Usage
After installation, the application can be launched by running its command in the terminal:


## Keyboard Controls:
UP ARROW: Move up in the job list.
DOWN ARROW: Move down in the job list.
Ctrl + K: Open the cancel job dialog for the selected job.
Ctrl + R: Refresh the job list.
Q: Quit the application.

## Dependencies
Python 3.6 or higher

## Contributing
Contributions to this project are welcome! To contribute, please follow these steps:

## Fork the repository.
Create a new branch for your feature.
Add your changes and commit them.
Push to your branch and submit a pull request.

## License
This project is licensed under the GPL3 - see the LICENSE file for details.