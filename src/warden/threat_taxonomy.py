from enum import Enum

class ThreatClass(str, Enum):
    LLM01_PROMPT_INJECTION = "LLM01_PROMPT_INJECTION"
    LLM02_INSECURE_OUTPUT = "LLM02_INSECURE_OUTPUT"
    LLM03_SUPPLY_CHAIN = "LLM03_SUPPLY_CHAIN"
    LLM06_SENSITIVE_INFO = "LLM06_SENSITIVE_INFO"
    LLM07_INSECURE_PLUGIN = "LLM07_INSECURE_PLUGIN"
    LLM08_EXCESSIVE_AGENCY = "LLM08_EXCESSIVE_AGENCY"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"

class ThreatCitation(str, Enum):
    LLM01 = "OWASP LLM Top 10 (2025) — LLM01: Prompt Injection"
    LLM02 = "OWASP LLM Top 10 (2025) — LLM02: Insecure Output Handling"
    LLM03 = "OWASP LLM Top 10 (2025) — LLM03: Training Data Poisoning / Supply Chain"
    LLM06 = "OWASP LLM Top 10 (2025) — LLM06: Sensitive Information Disclosure"
    LLM07 = "OWASP LLM Top 10 (2025) — LLM07: Insecure Plugin Design"
    LLM08 = "OWASP LLM Top 10 (2025) — LLM08: Excessive Agency"
    EXFIL = "DATA_EXFILTRATION: Unauthorized data exfiltration to external/untrusted destination"
