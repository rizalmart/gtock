project('gtock', 'c')

# Define your source and destination directories
source_dir = 'gtock-src'
install_dir = get_option('prefix') / 

# Get a list of all files in the source directory
files_to_install = files(glob(join_paths(source_dir, '*')))

# Loop through the files and create install targets
install_targets = []

foreach file: files_to_install

  # Define the install target path by preserving the relative directory structure
  target_path = join_paths(install_dir, file.relative_path())
  
  # Create the install target
  install_targets += install_data(file, install_dir: target_path)

# Add all install targets to the installation script
foreach target: install_targets
  add_install_script(target)

run_command('/usr/share/glib-2.0/schemas/glib-compile-schemas', 
    dependencies : [find_program('glib-compile-schemas')],
    capture : true)
