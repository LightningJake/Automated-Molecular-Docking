import os
import subprocess
import requests
import asyncio
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

EMAIL = 'chubchubjake@gmail.com'
PASSWORD = 'tffy jtcs dgkk fmyz'

IMAP_SERVER = 'imap.gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465  # Correct SMTP SSL port

async def run_command(cmd):
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            print(f'Successfully ran: {cmd}')
            print(stdout.decode())
        else:
            print(f'Error in command: {cmd}')
            print(stderr.decode())
            raise subprocess.CalledProcessError(process.returncode, cmd, stdout, stderr)
    except Exception as e:
        print(f"Exception occurred while running command: {e}")
        raise

async def convert_ligand(ligand_sdf, output_pdbqt):
    cmd = f'mk_prepare_ligand -i {ligand_sdf} -o {output_pdbqt}'
    print(f'Running: {cmd}')
    await run_command(cmd)

async def prepare_protein(protein_pdb, intermediate_pdb, final_pdbqt):
    # Remove water molecules
    remove_water_command = f'obabel {protein_pdb} -O {intermediate_pdb} -xr'
    print(f'Running: {remove_water_command}')
    await run_command(remove_water_command)

    # Add hydrogens
    add_hydrogens_command = f'obabel {intermediate_pdb} -O {intermediate_pdb} -h'
    print(f'Running: {add_hydrogens_command}')
    await run_command(add_hydrogens_command)

    # Add Kollman charges and convert to PDBQT
    # add_charges_command = f'obabel {intermediate_pdb} -O {final_pdbqt} --partialcharge gasteiger'
    # print(f'Running: {add_charges_command}')
    # await run_command(add_charges_command)

async def dock_with_vina(protein_pdbqt, ligand_pdbqt, output_dir, center_x, center_y, center_z, size_x, size_y, size_z):
    vina_command = (
        f'vina --receptor {protein_pdbqt} --ligand {ligand_pdbqt} '
        f'--out "{os.path.join(output_dir, "out.pdbqt")}" '
        f'--center_x {center_x} --center_y {center_y} --center_z {center_z} '
        f'--size_x {size_x} --size_y {size_y} --size_z {size_z}'
    )
    
    log_file = os.path.join(output_dir, "docking_log.txt")
    
    try:
        # Run the command asynchronously
        process = await asyncio.create_subprocess_shell(
            vina_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for the command to finish and capture the output
        stdout, stderr = await process.communicate()
        
        # Decode the output
        stdout_decoded = stdout.decode()
        stderr_decoded = stderr.decode()
        
        # Check if the command was successful
        if process.returncode == 0:
            print(f'Docking log:\n{stdout_decoded}')
            with open(log_file, "w") as log:
                log.write(stdout_decoded)
            print(f'Docking successful. Log saved to {log_file}')
        else:
            print(f'Docking failed. Error:\n{stderr_decoded}')
            raise subprocess.CalledProcessError(process.returncode, vina_command, stdout, stderr)
    except Exception as e:
        print(f'Error during docking: {e}')
        raise

async def conversions(ligand, protein, output_dir='output', center_x=0, center_y=0, center_z=0, size_x=20, size_y=20, size_z=20):
    ligand_sdf = f'{ligand}.sdf'
    ligand_pdbqt = f'{ligand}.pdbqt'
    protein_pdb = f'{protein}.pdb'
    intermediate_pdb = f'{protein}_h.pdb'
    final_pdbqt = f'{protein}.pdbqt'

    try:
        await convert_ligand(ligand_sdf, ligand_pdbqt)
        await prepare_protein(protein_pdb, intermediate_pdb, final_pdbqt)
        print('Conversion successful.')

        await dock_with_vina(final_pdbqt, ligand_pdbqt, output_dir, center_x, center_y, center_z, size_x, size_y, size_z)
        print('Docking successful.')

    except subprocess.CalledProcessError as e:
        print(f'Error during conversion or docking: {e}')

async def fetch_pdb(pdb_id, save_directory="."):
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

async def fetch_ligand_sdf(pubchem_cid, save_directory="."):
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

async def fetch_data(pubchem_cid, pdb_id, save_directory="."):
    os.makedirs(save_directory, exist_ok=True)
    
    await fetch_pdb(pdb_id, save_directory)
    await fetch_ligand_sdf(pubchem_cid, save_directory)
    await conversions(pubchem_cid, pdb_id, save_directory)
    out_dir=save_directory+"output/"
    output_files = [os.path.join(out_dir, 'out.pdbqt'), os.path.join(out_dir, 'docking_log.txt')]
    return output_files

async def send_email_with_attachments(to_email, subject, body, attachments):
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    for file in attachments:
        part = MIMEBase('application', 'octet-stream')
        with open(file, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file)}')
        msg.attach(part)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, to_email, msg.as_string())
        print(f'Email sent to {to_email} with attachments: {attachments}')

async def check_and_respond():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')

    status, data = mail.search(None, 'UNSEEN')
    email_ids = data[0].split()

    for email_id in email_ids:
        status, data = mail.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        from_ = email.utils.parseaddr(msg['From'])[1]
        subject = msg['Subject']

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        lines = body.split('\n')
        protein = ligand = ''
        for line in lines:
            if line.startswith('protein:'):
                protein = line.split(':')[1].strip()
            elif line.startswith('ligand:'):
                ligand = line.split(':')[1].strip()

        save_directory = r"C:/Users/iamri/OneDrive/Desktop/molecular docking/"
        output_files = await fetch_data(ligand, protein, save_directory)

        response_subject = f"Results for Protein: {protein}, Ligand: {ligand}"
        response_body = "Attached are the docking results."
        await send_email_with_attachments(from_, response_subject, response_body, output_files)

        await asyncio.sleep(60)

    mail.logout()

def main():
    while True:
        asyncio.run(check_and_respond())

if __name__ == '__main__':
    main()
