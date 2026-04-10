from domain.models import CompetitorConfig, HardwareItem

# ── Preset competitors ──────────────────────────────────────────────────────
COMPETITORS: list[CompetitorConfig] = [
    CompetitorConfig(name="PointCentral",  url="https://www.pointcentral.com",  slug="pointcentral"),
    CompetitorConfig(name="EnTouch",       url="https://www.entouch.net",        slug="entouch"),
    CompetitorConfig(name="SmartRent",     url="https://smartrent.com",          slug="smartrent"),
    CompetitorConfig(name="75F",           url="https://www.75f.io",             slug="75f"),
    CompetitorConfig(name="Pelican",       url="https://www.pelicanthermo.com",  slug="pelican"),
    CompetitorConfig(name="Kairos",        url="https://www.kairoswater.io",     slug="kairos"),
]

# ── Companies shown in "Companies Using" column ─────────────────────────────
COMPANIES_IN_SCOPE: list[str] = [
    "Titanium", "PointCentral", "EnTouch", "SmartRent", "75F", "Pelican", "Kairos"
]

# ── Default Titanium hardware list ──────────────────────────────────────────
DEFAULT_HARDWARE: list[HardwareItem] = [
    HardwareItem("Smart Thermostat",        "Networked thermostat for HVAC control and scheduling",                    "Yes"),
    HardwareItem("Smart Lock",              "Keypad or credential-based door access control",                          "No"),
    HardwareItem("CO2 Sensor",              "Standalone carbon dioxide air quality monitor",                           "Yes"),
    HardwareItem("VOC Sensor",              "Volatile organic compound air quality detector",                          "Yes"),
    HardwareItem("Temperature Sensor",      "Standalone ambient temperature sensor",                                   "Yes"),
    HardwareItem("IAQ Multi-Sensor",        "Combined indoor air quality sensor (CO2, VOC, temp, humidity bundled)",   "No"),
    HardwareItem("Humidity Sensor",         "Standalone relative humidity sensor",                                     "Yes"),
    HardwareItem("Water Leak Detector",     "Sensor detecting water presence / flood events",                          "Yes"),
    HardwareItem("Water Valve Controller",  "Motorized valve to shut off water supply remotely",                       "Yes"),
    HardwareItem("Energy Meter / Sub-Meter","Circuit-level electricity consumption monitoring",                        "Yes"),
    HardwareItem("Smart Plug / Outlet",     "Controllable smart outlet for load management",                           "No"),
    HardwareItem("Occupancy / Motion Sensor","PIR or radar-based presence detection",                                  "Yes"),
    HardwareItem("Door / Window Sensor",    "Open/close contact sensor",                                               "Yes"),
    HardwareItem("Wireless Gateway / Hub",  "Local hub bridging devices to cloud platform",                            "Yes"),
    HardwareItem("BACnet Controller",       "BACnet-compatible building automation controller",                        "Yes"),
    HardwareItem("Modbus Controller",       "Modbus RTU/TCP integration gateway",                                      "Yes"),
    HardwareItem("ZigBee Coordinator",      "ZigBee mesh radio coordinator",                                           "No"),
    HardwareItem("Z-Wave Controller",       "Z-Wave mesh radio controller",                                            "No"),
    HardwareItem("Demand-Controlled Ventilation","CO2-driven ventilation control for ASHRAE 62.1",                    "Yes"),
    HardwareItem("Fault Detection System",  "Automated HVAC fault detection and diagnostics",                          "Yes"),
    HardwareItem("Leak Detection Cable",    "Zone-based water leak detection cable",                                    "No"),
]
