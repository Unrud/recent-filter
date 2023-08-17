project('recent-filter',
  version: '0.1.2',
  meson_version: '>= 0.62.0',
  default_options: ['warning_level=2', 'werror=false'],
)

python_sources_for_linting = []
i18n = import('i18n')
gnome = import('gnome')
python = import('python').find_installation('python3')
python_for_linting = import('python').find_installation('python3',
  modules: ['flake8'],
  required: false,
)
python_for_unittest = import('python').find_installation('python3',
  modules: ['unittest'],
  required: false,
)
create_gresource_aux = meson.current_source_dir() / 'build-aux' / 'meson' / 'create-gresource.py'
python_sources_for_linting += create_gresource_aux
extract_xml_aux = meson.current_source_dir() / 'build-aux' / 'meson' / 'extract-xml.py'
python_sources_for_linting += extract_xml_aux
merge_xml_aux = meson.current_source_dir() / 'build-aux' / 'meson' / 'merge-xml.py'
python_sources_for_linting += merge_xml_aux
move_aux = meson.current_source_dir() / 'build-aux' / 'meson' / 'move.py'
python_sources_for_linting += move_aux


subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)

if (python_for_linting.found() and python_sources_for_linting.length() > 0)
  test('Lint python sources', python_for_linting,
    args: ['-m', 'flake8', python_sources_for_linting],
  )
endif

if (python_for_unittest.found())
  test('Run python unittest', python_for_unittest,
    args: ['-B', '-c', 'import runpy, sys, src; sys.modules["recent_filter"]=src; runpy.run_module("unittest", alter_sys=True)',
           'discover', '-p', '*_test.py'],
  )
endif
