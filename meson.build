project('gtock', 'c', version: '1.0')

# 1. Define the source directory
# Meson usually expects sources to be relative to the build file
source_dir = 'gtock-src'

# 2. Check if the directory exists (Logic check)
fs = import('fs')
if not fs.is_dir(source_dir)
  error('gtock source files are missing')
endif

# 3. Install files (Replaces 'cp -rf')
# Instead of a bulk copy, we define where specific folders/files go
install_subdir(source_dir,
  install_dir: get_option('prefix'),
  strip_directory: true
)

# 4. Compile schemas (Replaces the glib-compile-schemas logic)
# Meson has a built-in module for GLib tasks
gnome = import('gnome')
gnome.compile_schemas(
  depend_files: files('/usr/share/glib-2.0/schemas/org.gtk.gtock.gschema.xml') 
)

# 5. Set permissions (Replaces 'chmod +x')
# We do this during the install_data or install_exe phase
install_data(source_dir / 'usr/bin/gtock',
  install_dir: prefix_path / 'usr/bin',
  install_mode: 'rwxr-xr-x'
)
