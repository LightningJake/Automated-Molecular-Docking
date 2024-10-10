import os
import subprocess

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command '{cmd}' failed with return code {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise

def convert_ligand(ligand_sdf, output_pdbqt):
    cmd = f'mk_prepare_ligand -i {ligand_sdf} -o {output_pdbqt}'
    print(f'Running: {cmd}')
    run_command(cmd)

def prepare_protein(protein_pdb, intermediate_pdb, final_pdbqt):
    # Remove water molecules
    remove_water_command = f'obabel {protein_pdb} -O {intermediate_pdb} -xr'
    print(f'Running: {remove_water_command}')
    run_command(remove_water_command)

    # Add hydrogens
    add_hydrogens_command = f'obabel {intermediate_pdb} -O {intermediate_pdb} -h'
    print(f'Running: {add_hydrogens_command}')
    run_command(add_hydrogens_command)

    # Add Kollman charges and convert to PDBQT
    add_charges_command = f'obabel {intermediate_pdb} -O {final_pdbqt} --partialcharge gasteiger'
    print(f'Running: {add_charges_command}')
    run_command(add_charges_command)

def main():
    ligand_sdf = 'ligand.sdf'
    ligand_pdbqt = 'ligand.pdbqt'
    protein_pdb = 'protein.pdb'
    intermediate_pdb = 'protein_h.pdb'
    final_pdbqt = 'protein.pdbqt'
    
    try:
        convert_ligand(ligand_sdf, ligand_pdbqt)
        prepare_protein(protein_pdb, intermediate_pdb, final_pdbqt)
        print('Conversion successful.')
    except subprocess.CalledProcessError as e:
        print(f'Error during conversion: {e}')

if __name__ == "__main__":
    main()

