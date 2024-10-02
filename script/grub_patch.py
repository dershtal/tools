import argparse
import subprocess
import sys
import os

GRUB_CONFIG_PATH = "/etc/default/grub"
GRUB_UPDATE_CMD = "sudo update-grub"
DISABLE_PARAMS = "pti=off spectre_v1=off spectre_v2=off l1tf=off nospec_store_bypass_disable ibrs=off stibp=off ssbd=off l1d_flush=off mds=off tsx_async_abort=off mitigations=off noibpb no_stf_barrier tsx=on retbleed=off spectre_v2=retpoline,force"

def print_help():
    help_text = """
    GRUB Patching Script

    This script allows you to patch the GRUB configuration to disable protections against the Meltdown and Spectre vulnerabilities, as well as check the current system status.

    Usage:
      --help      Display this help message
      --patch     Apply patch to GRUB configuration by disabling protections against Meltdown and Spectre
      --check     Show current system status by displaying relevant kernel parameters using spectre-meltdown-checker
    """
    print(help_text)

def patch_grub():
    # Backup the current GRUB configuration
    if os.path.exists(GRUB_CONFIG_PATH):
        backup_path = GRUB_CONFIG_PATH + ".bak"
        subprocess.run(["sudo", "cp", GRUB_CONFIG_PATH, backup_path])
        print(f"Backup of the GRUB configuration created at {backup_path}")

        # Read the current configuration
        with open(GRUB_CONFIG_PATH, "r") as file:
            config = file.read()

        # Add the necessary parameters if not already present
        if DISABLE_PARAMS not in config:
            config = config.replace('GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"',
                                    f'GRUB_CMDLINE_LINUX_DEFAULT="quiet splash {DISABLE_PARAMS}"')

            # Write the modified configuration back to the file
            with open(GRUB_CONFIG_PATH, "w") as file:
                file.write(config)

            # Update GRUB
            subprocess.run(GRUB_UPDATE_CMD.split())
            print("GRUB configuration has been patched and updated.")
            
            # Output the "Please reboot system!" message in red color
            print("\033[91mPlease reboot system!\033[0m")
        else:
            print("The necessary parameters are already present in the GRUB configuration.")
    else:
        print(f"GRUB configuration file not found at {GRUB_CONFIG_PATH}")

def check_system_status():
    # Check if spectre-meltdown-checker is installed
    try:
        subprocess.run(["spectre-meltdown-checker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("spectre-meltdown-checker is installed.")
    except subprocess.CalledProcessError:
        print("spectre-meltdown-checker is not installed.")
        install = input("Would you like to install it now? (yes/no): ").strip().lower()
        if install == "yes":
            # Try to install spectre-meltdown-checker
            try:
                subprocess.run(["sudo", "apt-get", "install", "-y", "spectre-meltdown-checker"], check=True)
                print("spectre-meltdown-checker has been installed.")
            except subprocess.CalledProcessError:
                print("Failed to install spectre-meltdown-checker. Please install it manually.")
                sys.exit(1)
        else:
            print("spectre-meltdown-checker is required for checking the system status.")
            sys.exit(1)

    # Run spectre-meltdown-checker and display the result
    try:
        print("Running spectre-meltdown-checker...")
        # Using 'sudo' to run the checker with proper permissions
        result = subprocess.run(["sudo", "spectre-meltdown-checker"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Decode and print both stdout and stderr
        print(result.stdout.decode())
        if result.stderr:
            print(result.stderr.decode(), file=sys.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Failed to run spectre-meltdown-checker: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="GRUB Patching Script")
    parser.add_argument('--patch', action='store_true', help="Patch the GRUB configuration to disable protections against Meltdown and Spectre")
    parser.add_argument('--check', action='store_true', help="Check current system status by showing relevant kernel parameters using spectre-meltdown-checker")

    args = parser.parse_args()

    if args.patch:
        patch_grub()
    elif args.check:
        check_system_status()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
