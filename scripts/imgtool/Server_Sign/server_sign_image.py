import sys
import os
import time
import subprocess
	
def eaton_server_sign(file_path, user_name, user_pwd):
    if file_path is None:
        print("zephyr.tmp.unusigned.bin not found")
        print("Process Terminated ")
        sys.exit()
    print("\n Input File: " + str(file_path) + "\n")
    output_file = os.path.realpath(os.path.join(file_path, '..', 'zephyr.tmp.signed.bin.p7b'))
    if user_name is None:
        username = input("Enter User Name (Eaton ID):")
    else:
        username = user_name
    if username.strip() == '':
        print("NO User Entered \n ")
        print(" Process Terminated ")
        sys.exit()
    server_home = os.environ.get('SIGNSERVER_HOME')
    worker = os.environ.get('SIGNSERVER_WORKER')
    if worker is None or worker.strip() == '':
        print("SIGNSERVER_WORKER not set, defaulting to 'FW-GridAdvisor3-CMS'")
        worker = 'FW-GridAdvisor3-CMS'

    import platform
    is_windows = platform.system().lower().startswith('win')

    if is_windows:
        if server_home is None:
            print("SIGNSERVER_HOME  - should be the path of sign server utility installed on your system \n ")
            print("Process Terminated ! ")
            sys.exit()
        print("Value read from Environment Variable : \n 1. SIGNSERVER_HOME : " + str(server_home) + " \n 2. SIGNSERVER_WORKER : " + str(worker) + "\n")
        arr = os.listdir(server_home)
        if 'bin' in arr:
            path = str(server_home) + "/bin"
            if user_pwd is None:
                str_arg = "signclient.cmd signdocument -workername " + str(worker) + " -servlet " + "/signserver/worker/" + str(worker) + " -truststore " + str(server_home) + "/eaton-truststore.jks -truststorepwd eaton -infile " + str(file_path) + " -hosts signserverp3.tcc.etn.com,signserverp4.tcc.etn.com -port 8443 -username " + str(username) + " -outfile " + str(output_file)
            else:
                str_arg = "signclient.cmd signdocument -workername " + str(worker) + " -servlet " + "/signserver/worker/" + str(worker) + " -truststore " + str(server_home) + "/eaton-truststore.jks -truststorepwd eaton " + " -password " + str(user_pwd) + " -infile " + str(file_path) + " -hosts signserverp3.tcc.etn.com,signserverp4.tcc.etn.com -port 8443 -username " + str(username) + " -outfile " + str(output_file)
            os.chdir(path)
            subprocess.run(str_arg)
        else:
            print("Please check the path for SIGNSERVER_HOME bin folder not found")
            print("Process Terminated !")
            sys.exit(1)
    else:
        # Linux/Unix: Use curl to POST the file to the signserver servlet
        # The form field name is assumed to be 'file' (adjust if needed)
        url = f"https://signserverp3.tcc.etn.com:8443/signserver/worker/{worker}"
        curl_cmd = [
            "curl", "-k", "--user", username,
            "--form", f"file=@{file_path}", url
        ]
        if user_pwd is not None:
            curl_cmd[3] = f"{username}:{user_pwd}"
        print("Running curl command: ", ' '.join(curl_cmd))
        with open(output_file, "wb") as out_f:
            result = subprocess.run(curl_cmd, stdout=out_f)
        if result.returncode != 0:
            print("curl command failed!")
            print("Process Terminated !")
            sys.exit(1)

    # Common: Extract signature from .p7b file
    openssl_command = f"openssl asn1parse -inform DER -in {output_file} > {output_file}.txt"
    print(str(openssl_command) + "\n")
    os.popen(openssl_command)
    time.sleep(2)
    outfile = os.path.realpath(os.path.join(file_path, '..', 'zephyr.tmp.signed.bin.p7b.txt'))
    print(str(outfile))
    file1 = open(outfile, 'r')
    Lines = file1.readlines()
    address = None
    for line in Lines:
        if 'OCTET STRING' in line:
            address = line.partition(':')[0]
    if address is not None:
        print("address : " + str(address))
        sig_extract_cmd = f"openssl asn1parse -inform DER -in {output_file} -out {output_file}.sig -noout -strparse {address}"
        subprocess.run(sig_extract_cmd, shell=True)
    else:
        print("OCTET STRING not found in the output file.")
        print("Process Terminated!")
        sys.exit(1)
