project(
  'gtock',
  version: '3.0.0',
  meson_version: '>=0.60.0',
  default_options: [
    'prefix=/usr',
    'warning_level=2',
  ],
)

# gTock is a Python/GTK application.  Meson installs the Python sources and
# data files without compiling or byte-compiling them, which keeps the build
# usable by Debian, RPM, Arch, Alpine and source-based package builders.

py_install_dir = join_paths(get_option('datadir'), 'gtock')
schema_dir = join_paths(get_option('datadir'), 'glib-2.0', 'schemas')
applications_dir = join_paths(get_option('datadir'), 'applications')
icons_dir = join_paths(get_option('datadir'), 'icons', 'hicolor', 'scalable', 'apps')
doc_dir = join_paths(get_option('datadir'), 'doc', 'gtock')

# Main Python application and its runtime data (Glade files, SVGs, helpers).
install_subdir(
  'gtock-src/usr/share/gtock',
  install_dir: join_paths(get_option('datadir'), 'gtock'),
  strip_directory: true,
  exclude_directories: ['__pycache__'],
)

# Install the GSettings schema in the standard GLib schema directory.
schema_file = files('gtock-src/usr/share/glib-2.0/schemas/org.gtk.gtock.gschema.xml')
install_data(schema_file, install_dir: schema_dir)

# Validate/compile schemas in the build tree. Distribution package hooks should
# rebuild the shared schema cache after installation/removal; never install a
# package-owned gschemas.compiled file over the system-wide cache.
gnome = import('gnome')
gnome.compile_schemas(
  depend_files: schema_file,
  build_by_default: true,
  install: false,
)

# Desktop entry and themed application icon.
install_data(
  'gtock-src/usr/share/applications/gtock.desktop',
  install_dir: applications_dir,
)
install_data(
  'gtock-src/usr/share/gtock/pixmaps/gtock.svg',
  install_dir: icons_dir,
  rename: 'gtock.svg',
)
install_data('README.md', install_dir: doc_dir)

# Generate launchers using the configured prefix/datadir. This avoids the
# previous hard-coded /usr/share/gtock path and supports staged package builds.
conf = configuration_data()
conf.set('GTOCK_APPDIR', join_paths(get_option('prefix'), get_option('datadir'), 'gtock'))

configure_file(
  input: 'packaging/gtock.in',
  output: 'gtock',
  configuration: conf,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x',
)
configure_file(
  input: 'packaging/gtock-import.in',
  output: 'gtock-import',
  configuration: conf,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x',
)
configure_file(
  input: 'packaging/gtock-export.in',
  output: 'gtock-export',
  configuration: conf,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x',
)

# Unit tests are also available to distro package builders (`meson test`).
python3 = find_program('python3', required: false)
if python3.found()
  test('anacron-parser', python3,
    args: files('tests/test_anacron.py'),
    suite: 'gtock',
  )
  test('cron-backend-detection', python3,
    args: files('tests/test_backend_detection.py'),
    suite: 'gtock',
  )
endif

summary({
  'Application data': join_paths(get_option('prefix'), py_install_dir),
  'Executable directory': join_paths(get_option('prefix'), get_option('bindir')),
  'GSettings schemas': join_paths(get_option('prefix'), schema_dir),
  'Desktop entries': join_paths(get_option('prefix'), applications_dir),
  'Documentation': join_paths(get_option('prefix'), doc_dir),
}, section: 'Installation paths')
