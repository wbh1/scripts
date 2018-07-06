import sys, re, os, subprocess
from tkinter import filedialog
import tkinter as tk

file = 'permissions.txt'
output_file = 'insert_statements.txt'
user = 'none'
classes = []
groups = []
cwd = os.getcwd()

def existing_file_check():
    try:
        with open(output_file, 'a') as out:
            out.truncate(0)
    except:
        pass

def user_prompt():
    global user
    user = input("What user should permissions be granted to?: ").upper()
    user_check(user)

def write_out(insert_statement):
    with open(output_file, 'a') as out:
        out.write(insert_statement + " \n")

def user_check(user):
    if user == 'none' or user == '':
        raise ValueError("Invalid user")

def file_prompt():
    print("Select a .txt file containing a list of permissions")
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename(title="Select a permissions file")
    file_check(file)
    print(file)

def file_check(file):
    if file == "":
        raise ValueError("Please specify an actual file")

def create_lists():
    with open(file) as cl:
        perms = cl.read().splitlines()
        regex1 = re.compile("(^[A-Z]{,4}-[A-Z]{1}-[A-Z]*$)|([A-Z]{,4}-[A-Z]{1}-[A-Z]*-[A-Z]*$)|(^[A-Z]*_[A-Z]*$)|(^[A-Z]*_[A-Z]*_[A-Z]*$)")
        regex2 = re.compile("(^[A-Z]{,4}-[A-Z]{3,}-[A-Z]*$)|(^[A-Z]{,4}-[A-Z]{3,}-[A-Z]*-[0-3]*$)")
        for perm in perms:
            if regex1.match(perm):
                classes.append(perm)
            elif regex2.match(perm):
                groups.append(perm)
            else:
                raise ValueError("Invalid class/group in the file.")

def create_statements():
    for x in classes:
        insert_statement = "insert into bansecr.gurucls " \
                            + "(GURUCLS_USERID, GURUCLS_CLASS_CODE, GURUCLS_ACTIVITY_DATE, GURUCLS_USER_ID) VALUES " \
                            + "('%s', '%s', CURRENT_DATE, 'BANSECR');" % (user, x)

        write_out(insert_statement)


    for y in groups:
        insert_statement = "insert into bansecr.gurugrp " \
                            + "(GURUGRP_USER, GURUGRP_SGRP_CODE, GURUGRP_ACTIVITY_DATE, GURUGRP_USER_ID) VALUES " \
                            + "('%s', '%s', CURRENT_DATE, 'BANSECR');" % (user, y)

        write_out(insert_statement)

def open_file():
    global output_file
    if sys.platform.startswith('darwin'):
        subprocess.call('clear')
        subprocess.call(('open', output_file))
    elif os.name == 'nt':
        os.system('cls')
        os.system('start ' + output_file)

def main():
    user_prompt()
    file_prompt()
    existing_file_check()
    create_lists()
    create_statements()
    open_file()

main()