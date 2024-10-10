import requests
import os
def fetch_pdb(pdb_id, save_directory="."):
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    response = requests.get(url)
    
    if response.status_code == 200:
        pdb_content = response.text
        save_path = os.path.join(save_directory, f"{pdb_id}.pdb")
        with open(save_path, "w") as file:
            file.write(pdb_content)
        print(f"PDB file {pdb_id}.pdb has been successfully downloaded to {save_path}.")
        return pdb_content
    else:
        print(f"Failed to retrieve PDB file for ID: {pdb_id}.")
        return None


def fetch_ligand_sdf(pubchem_cid, save_directory="."):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{pubchem_cid}/SDF"
    response = requests.get(url)
    
    if response.status_code == 200:
        sdf_content = response.text
        save_path = os.path.join(save_directory, f"{pubchem_cid}.sdf")
        with open(save_path, "w") as file:
            file.write(sdf_content)
        print(f"SDF file for PubChem CID {pubchem_cid} has been successfully downloaded to {save_path}.")
        return sdf_content
    else:
        print(f"Failed to retrieve SDF file for CID: {pubchem_cid}.")
        return None
    
def fetch_data(query, save_directory="."):
    # Parse the query string
    parts = query.split(',')
    pdb_id = parts[0].split('=')[1].strip()
    pubchem_cid = parts[1].split('=')[1].strip()
    
    # Create the directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)
    
    # Fetch the PDB and SDF files
    fetch_pdb(pdb_id, save_directory)
    fetch_ligand_sdf(pubchem_cid, save_directory)


query = "Protein=4MZI,Ligand=160355"
save_directory = r"C:/Users/iamri/OneDrive/Desktop/molecular docking/"  # Change this to your desired directory
fetch_data(query, save_directory)

