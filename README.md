# Automated-Molecular-Docking

Overview
The Automated Molecular Docking project automates the preparation of protein and drug compound structures for molecular docking simulations, which predict potential interactions between a ligand (drug compound) and a target protein. The system simplifies drug discovery by handling tasks like fetching molecular files, processing them for docking, and running the simulations. This project minimizes manual intervention, making it efficient and user-friendly.

Features
->Automatic File Retrieval: Fetches PDB files for proteins from the Protein Data Bank and SDF files for ligands from PubChem.
->File Preparation: Prepares protein and ligand files for docking by removing water molecules, adding hydrogens, and applying charges.
->Automated Docking Simulation: Converts files into the required PDBQT format and runs docking simulations.
->Email-Based Interaction: Accepts PDB IDs and compound IDs via email and sends back simulation results.

Requirements
Before running the project, make sure you have the following dependencies installed:
1)Python 3.x
2)Requests: For fetching PDB and SDF files
3)Open Babel: Used for manipulating molecular structures
4)MK_Ligand: For ligand preparation
5)IMAPLIB & smtplib: For handling email interactions

Installation
1)Clone the Repository:
2)Install Dependencies: Install the required Python packages and ensure you have the necessary external tools like Open Babel and MK_Ligand installed.
3)Configure Email Credentials: Update the email_bot.py file with your email credentials to handle email-based inputs.

Usage
1. Running Locally
You can interact with the system via email. Here’s the process to use the automated molecular docking system:
1)Input: Send an email containing the protein PDB ID and ligand CID in the following format:
2)Automated Workflow: The bot will automatically fetch the files for the provided PDB ID and CID, prepare them, and run the docking simulation.
3)Output: Once completed, you will receive a response email indicating the status of the conversion or simulation. If successful, the PDBQT files for the protein and ligand will be available.

2. Running the Script
If you prefer not to use email, you can run the script directly. For example, to manually input PDB ID and CID:

Project Structure
Key Files
fetch_and_convert.py: The main script for converting ligand and protein files to PDBQT format.
email_bot.py: Automates receiving PDB ID and CID via email, running conversions, and sending results back.
requirements.txt: Contains a list of Python dependencies for easy installation.
Contributing
We welcome contributions to improve the system! If you would like to contribute:

Fork the repository.
Create a new branch with your feature or bugfix.
Submit a pull request for review.

Contact
For any issues or inquiries, please contact:

Project Lead: Layaa Seeda
