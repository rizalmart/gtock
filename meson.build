project('gtock', 'python')

usr_files = files('gtock-src/usr/**')

install_data(usr_files, install_dir : '/usr')

run_command('/usr/share/glib-2.0/schemas/glib-compile-schemas', 
    dependencies : [find_program('glib-compile-schemas')],
    capture : true)
