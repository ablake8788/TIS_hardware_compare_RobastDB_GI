# @"
import os
import configparser
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class OpenAISettings:
    api_key: str
    model: str = 'gpt-4.1-mini'

@dataclass
class SQLServerSettings:
    driver: str
    server: str
    database: str
    username: str
    password: str
    trust_cert: bool = True

@dataclass
class EmailSettings:
    enabled: bool
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_email: str
    to_email: list
    subject: str

@dataclass
class OutputSettings:
    pptx_enabled: bool = True
    docx_enabled: bool = True
    html_enabled: bool = True
    md_enabled: bool = True

@dataclass
class AppSettings:
    openai: OpenAISettings
    report_location: str = 'reports'
    compare_file_location: str = ''
    baseline_url: str = ''
    max_doc_chars: int = 60000
    max_site_chars: int = 40000
    open_report: bool = True
    timeout_seconds: int = 25
    tesseract_path: str = ''
    pdf_dpi: int = 300
    outputs: OutputSettings = field(default_factory=OutputSettings)
    email: Optional[EmailSettings] = None
    sqlserver: Optional[SQLServerSettings] = None

def load_settings(ini_path=None):
    cfg = configparser.ConfigParser(inline_comment_prefixes=(';', '#'))
    ini_name = 'tis_gap_app.ini'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    candidates = []
    if ini_path:
        candidates.append(ini_path)
    candidates += [
        os.path.join(base_dir, ini_name),
        os.path.join(project_root, ini_name),
        os.path.join(os.getcwd(), ini_name),
    ]
    found = None
    for path in candidates:
        if os.path.isfile(path):
            found = path
            break
    if found:
        print(f'[ini_config] Loaded: {found}')
        cfg.read(found, encoding='utf-8')
    else:
        print(f'[ini_config] WARNING: {ini_name} not found')
    api_key = cfg.get('OpenAI', 'api_key', fallback='').strip() or os.environ.get('OPENAI_API_KEY', '')
    model = cfg.get('OpenAI', 'model', fallback='gpt-4.1-mini').strip()
    openai_settings = OpenAISettings(api_key=api_key, model=model)
    report_location = cfg.get('Settings', 'report_location', fallback='reports').strip()
    compare_file_location = cfg.get('Settings', 'compare_file_location', fallback='').strip()
    baseline_url = cfg.get('Settings', 'baseline_url', fallback='').strip()
    max_doc_chars = cfg.getint('Settings', 'max_doc_chars', fallback=60000)
    max_site_chars = cfg.getint('Settings', 'max_site_chars', fallback=40000)
    open_report = cfg.getboolean('Settings', 'open_report', fallback=True)
    if not os.path.isabs(report_location) or not os.path.exists(os.path.dirname(report_location)):
        report_location = os.path.join(project_root, 'reports')
    os.makedirs(report_location, exist_ok=True)
    timeout_seconds = cfg.getint('HTTP', 'timeout_seconds', fallback=25)
    tesseract_path = cfg.get('OCR', 'tesseract_path', fallback='').strip()
    pdf_dpi = cfg.getint('OCR', 'pdf_dpi', fallback=300)
    outputs = OutputSettings(
        pptx_enabled=cfg.getboolean('Outputs', 'pptx_enabled', fallback=True),
        docx_enabled=cfg.getboolean('Outputs', 'docx_enabled', fallback=True),
        html_enabled=cfg.getboolean('Outputs', 'html_enabled', fallback=True),
        md_enabled=cfg.getboolean('Outputs', 'md_enabled', fallback=True),
    )
    email_settings = None
    if cfg.has_section('Email'):
        to_raw = cfg.get('Email', 'to_email', fallback='').strip()
        to_list = [e.strip() for e in to_raw.split(',') if e.strip()]
        email_settings = EmailSettings(
            enabled=cfg.getboolean('Email', 'enabled', fallback=False),
            smtp_server=cfg.get('Email', 'smtp_server', fallback='').strip(),
            smtp_port=cfg.getint('Email', 'smtp_port', fallback=587),
            smtp_user=cfg.get('Email', 'smtp_user', fallback='').strip(),
            smtp_password=cfg.get('Email', 'smtp_password', fallback='').strip(),
            from_email=cfg.get('Email', 'from_email', fallback='').strip(),
            to_email=to_list,
            subject=cfg.get('Email', 'subject', fallback='Gap Analysis Report').strip(),
        )
    sql_settings = None
    if cfg.has_section('sqlserver'):
        sql_settings = SQLServerSettings(
            driver=cfg.get('sqlserver', 'driver', fallback='ODBC Driver 17 for SQL Server').strip(),
            server=cfg.get('sqlserver', 'server', fallback='localhost').strip(),
            database=cfg.get('sqlserver', 'database', fallback='').strip(),
            username=cfg.get('sqlserver', 'username', fallback='').strip(),
            password=cfg.get('sqlserver', 'password', fallback='').strip(),
            trust_cert=cfg.getboolean('sqlserver', 'trust_cert', fallback=True),
        )
    return AppSettings(
        openai=openai_settings,
        report_location=report_location,
        compare_file_location=compare_file_location,
        baseline_url=baseline_url,
        max_doc_chars=max_doc_chars,
        max_site_chars=max_site_chars,
        open_report=open_report,
        timeout_seconds=timeout_seconds,
        tesseract_path=tesseract_path,
        pdf_dpi=pdf_dpi,
        outputs=outputs,
        email=email_settings,
        sqlserver=sql_settings,
    )

_settings = None

def get_settings(ini_path=None):
    global _settings
    if _settings is None:
        _settings = load_settings(ini_path)
    return _settings

def reload_settings(ini_path=None):
    global _settings
    _settings = load_settings(ini_path)
    return _settings
# "@ | Out-File -FilePath "config\ini_config.py" -Encoding UTF8