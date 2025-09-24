
import os
import sys

def set_permanent_env_var():
    hf_token = input("Please enter your Hugging Face API token: ").strip()
    if not hf_token:
        print("Error: Token cannot be empty.")
        sys.exit(1)

    home_dir = os.path.expanduser('~')
    bashrc_path = os.path.join(home_dir, '.bashrc')
    profile_path = os.path.join(home_dir, '.profile')

    target_file = None
    if os.path.exists(bashrc_path):
        target_file = bashrc_path
    elif os.path.exists(profile_path):
        target_file = profile_path
    else:
        print(f"Warning: Neither {bashrc_path} nor {profile_path} found. Cannot set permanently.")
        print("Please set the environment variable manually using: export HF_TOKEN='YOUR_TOKEN'")
        sys.exit(0)

    env_line = f'export HF_TOKEN="{hf_token}"'
    file_content = []
    token_found = False

    try:
        with open(target_file, 'r') as f:
            file_content = f.readlines()

        with open(target_file, 'w') as f:
            for line in file_content:
                if line.strip().startswith('export HF_TOKEN='):
                    f.write(env_line + '\n')
                    token_found = True
                else:
                    f.write(line)
            if not token_found:
                f.write('\n# Added by text-generation-webui setup script\n')
                f.write(env_line + '\n')

        print(f"Successfully added/updated HF_TOKEN in {target_file}")
        print("Please run 'source ~/{file_name}' (e.g., 'source ~/.bashrc') or restart your terminal for the changes to take effect.")
        print("You can verify by typing 'echo $HF_TOKEN' in a new terminal session.")

    except IOError as e:
        print(f"Error writing to {target_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    set_permanent_env_var()
