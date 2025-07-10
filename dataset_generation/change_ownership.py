
import os
import sys
import pwd
import grp

def change_ownership(directory, username, groupname):
    try:
        uid = pwd.getpwnam(username).pw_uid
        gid = grp.getgrnam(groupname).gr_gid
    except KeyError:
        print(f"Error: User '{username}' or group '{groupname}' not found.")
        sys.exit(1)

    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                os.chown(filepath, uid, gid)
                print(f"Changed ownership of '{filepath}' to {username}:{groupname}")
            except OSError as e:
                print(f"Error changing ownership of '{filepath}': {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python change_ownership.py <directory_path>")
        sys.exit(1)

    directory_to_change = sys.argv[1]
    target_username = "user"
    target_groupname = "user"

    change_ownership(directory_to_change, target_username, target_groupname)
