from constant import *
import subprocess
import shutil
import sys
import os 


def run_script(script_path, script_args):
    try:
        # Prepare the command to run the script with its arguments
        command = ['python', script_path] + script_args

        # Run the script
        completed_process = subprocess.run(command, check=True, text=True, capture_output=True)

        # Output the result
        print("Script output:\n", completed_process.stdout)

    except subprocess.CalledProcessError as e:
        print("Error occurred while running the script:", e)
        print("Error output:\n", e.stderr)

def begin(folder, subfolder):
    """Copy xx_src to data/docs
    xx_src_refs.md to data/refs
    xx_src_catalog.md to data/input
    """
    xx_src_dir = os.path.join(SOURCE_DIR, folder, subfolder)
    xx_src_dest = os.path.join(DESTINATION_DIR, "data", "docs", subfolder)
    if not os.path.exists(xx_src_dest):
        shutil.copytree(xx_src_dir, xx_src_dest)
    xx_src_refs_file = os.path.join(SOURCE_DIR, folder, subfolder + "_refs.md")
    xx_src_refs_dest = os.path.join(DESTINATION_DIR, "data", "refs")
    if not os.path.exists(xx_src_refs_dest):
        shutil.copy(xx_src_refs_file, xx_src_refs_dest)
    xx_src_catalog_file = os.path.join(SOURCE_DIR, folder, subfolder + "_catalog.md")
    xx_src_catalog_dest = os.path.join(DESTINATION_DIR, "data", "catalog")
    if not os.path.exists(xx_src_catalog_dest):
        shutil.copy(xx_src_catalog_file, xx_src_catalog_dest)


def end(folder, subfolder):
    final_path = os.path.join(DESTINATION_DIR, "data", "final", subfolder + "_final.md")
    dest_path = os.path.join(SOURCE_DIR, folder)
    if not os.path.exists(dest_path):
        shutil.copy(final_path, dest_path)
    # img_path = os.path.join(DESTINATION_DIR, "img", subfolder + "_img")
    # dest_img_path = os.path.join(SOURCE_DIR, folder)
    # shutil.copytree(img_path, dest_img_path)



def main():
    if len(sys.argv) < 3:
        print("Usage: python %s <folder> <subfolder>" % sys.argv[0])
        sys.exit(0)
    folder = sys.argv[1]
    subfolder = sys.argv[2]  # xxx_src
    print("Beginning...")
    begin(folder, subfolder)
    run_script("chat_paper/ingest_data.py", [subfolder])
    run_script("chat_paper/file_app.py", [subfolder])
    run_script("chat_paper/final.py", [subfolder])
    end(folder, subfolder)
    print("End")


if __name__=="__main__":
    main()

    