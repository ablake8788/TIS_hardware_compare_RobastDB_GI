@"
# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

added_files = [
    ('templates', 'templates'),
    ('static',    'static'),
]
added_files += collect_data_files('docx')
added_files += collect_data_files('flask')

hidden_imports = [
    'config.ini_config','config.presets',
    'domain.models','domain.errors',
    'ports.llm',
    'adapters.llm_openai','adapters.llm_anthropic',
    'services.analysis_service','services.prompt_builder',
    'renderers.docx_renderer','app_factory',
    'flask','flask.templating','jinja2',
    'werkzeug','werkzeug.serving','werkzeug.routing',
    'openai','anthropic','httpx','httpcore',
    'docx','docx.oxml','docx.oxml.ns','docx.shared',
    'docx.enum.text','docx.enum.table',
    'lxml','lxml.etree','configparser','dataclasses','webbrowser',
]
hidden_imports += collect_submodules('openai')
hidden_imports += collect_submodules('anthropic')
hidden_imports += collect_submodules('flask')
hidden_imports += collect_submodules('docx')

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter','matplotlib','numpy','pandas','scipy'],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='TIS_GapAnalysis',
    debug=False, strip=False, upx=True,
    console=True, runtime_tmpdir=None,
)
"@ | Out-File -FilePath "tis_gap_app.spec" -Encoding UTF8