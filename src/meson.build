pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'recent_filter'

release_notes = run_command([
  python, extract_xml_aux, '--escape',
  '..' / 'data' / 'io.github.unrud.RecentFilter.metainfo-releases.xml.in',
  './/release[@version="' + meson.project_version() + '"]/description/*'],
  check: true,
).stdout()

conf = configuration_data()
conf.set('VERSION', meson.project_version())
conf.set('releasenotes', release_notes)

about_dialog_ui_source = configure_file(
  input: 'about_dialog.ui.in',
  output: 'about_dialog.ui',
  configuration: conf,
)

recent_filter_ui_sources = [
  files([
    'gtk/help-overlay.ui',
    'window.ui',
  ]),
  about_dialog_ui_source,
]

recent_filter_gresource_xml = configure_file(
  capture: true,
  command: [python, create_gresource_aux, '/io/github/unrud/RecentFilter',
            recent_filter_ui_sources],
  output: 'recent_filter.gresource.xml',
)

gnome.compile_resources('recent-filter', recent_filter_gresource_xml,
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

conf = configuration_data()
conf.set('PYTHON', python.full_path())
conf.set_quoted('VERSION', meson.project_version())
conf.set_quoted('localedir', get_option('prefix') / get_option('localedir'))
conf.set_quoted('pkgdatadir', pkgdatadir)

recent_filter_bin = configure_file(
  input: 'recent-filter.in',
  output: 'recent-filter',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x',
)
python_sources_for_linting += recent_filter_bin

recent_filter_sources = files([
  '__init__.py',
  'background_portal.py',
  'filter.py',
  'gitignore.py',
  'main.py',
  'service.py',
  'window.py',
])
python_sources_for_linting += recent_filter_sources

install_data(recent_filter_sources, install_dir: moduledir)


subdir('util')
