import requests
import os
import subprocess

import pylibsrcml
import srcml_database

"""
To download from GitHub:

Input Link: https://github.com/srcML/srcML
Download Link: https://github.com/srcML/srcML/archive/refs/heads/master.zip

"""

def download_github_repo(github_link):
    repo_name = "/".join(github_link.split("/")[-2:])
    download_link = github_link + "/archive/refs/heads/master.zip"
    save_location = "data/"+repo_name
    print(repo_name)
    if not os.path.isdir(save_location):
        os.makedirs(save_location)

    print("Downloading")
    #download the code
    response = requests.get(download_link,stream=True)
    if response.status_code == 200:
        with open(save_location+"/code.zip",'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True
    return False

def convert_to_srcml(repo_name,get_position=False):
    if not get_position:
        command = ["srcml","data/"+repo_name+"/code.zip","-o","data/"+repo_name+"/code.xml"]
    else:
        command = ["srcml","--position","data/"+repo_name+"/code.zip","-o","data/"+repo_name+"/code_pos.xml"]

    result = subprocess.run(command)

    if result.returncode == 0:
        return True
    else:
        return False

def add_srcml_to_database(repo_name):
    srcml_database.add_repo(repo_name)

    srcml = pylibsrcml.srcMLArchiveRead("data/"+repo_name+"/code_pos.xml")

    # Populate Files
    for unit in srcml:
        name = unit.get_filename()
        language = unit.get_language()
        srcml_database.add_file(name,language,repo_name)

    srcml_database.commit()

def run_stereocode(repo_name):
    command = ["./programs/stereocode", "data/"+repo_name+"/code_pos.xml","-o","data/"+repo_name+"/code_stereotype.xml"]

    result = subprocess.run(command)

    if result.returncode == 0:
        return True
    else:
        return False

def run_namecollector(repo_name):
    command = ["./programs/nameCollector","-i","data/"+repo_name+"/code_stereotype.xml","-o","data/"+repo_name+"/code_names.csv","--csv"]

    result = subprocess.run(command)

    if result.returncode == 0:
        return True
    else:
        return False

def add_names_to_database(repo_name):
    with open("data/"+repo_name+"/code_names.csv") as file:
        for line in file.readlines():
            vals = line.split(",")
            name = vals[0]
            type = vals[1]
            category = vals[2]
            file = vals[3]
            pos = vals[4]
            srcml_database.add_identifier(name,type,category,srcml_database.get_file_id_from_name_and_repo(file,srcml_database.get_repo_id_from_name(repo_name)),pos.split(":")[0],pos.split(":")[1])
    srcml_database.commit()


