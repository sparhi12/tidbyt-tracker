"""
Offline ICAO airline code database.
Maps 3-letter ICAO callsign prefixes to short, clean primary brand names
(e.g. 'Alaska' instead of 'Alaska Airlines') to fit statically without marquee cutoff.
"""

from typing import Optional

AIRLINES_SHORT = {
    # Major US Carriers
    "ASA": "Alaska",
    "QXE": "Horizon",
    "DAL": "Delta",
    "UAL": "United",
    "AAL": "American",
    "SWA": "Southwest",
    "JBU": "JetBlue",
    "FFT": "Frontier",
    "NKS": "Spirit",
    "HAL": "Hawaiian",
    "SKW": "SkyWest",
    "EDV": "Endeavor",
    "ENY": "Envoy",
    "RPA": "Republic",
    "PSA": "PSA Air",
    "PDT": "Piedmont",
    "GJS": "GoJet",
    "AWI": "Air Wisconsin",
    "CPZ": "Compass",
    "MCO": "Mesa",
    "ASH": "Mesa",
    "SCX": "Sun Country",
    "AAY": "Allegiant",
    "MXY": "Breeze",
    "VRD": "Virgin Amer",

    # Cargo / Logistics
    "FDX": "FedEx",
    "UPS": "UPS",
    "GTI": "Atlas Air",
    "PAC": "Polar Cargo",
    "ATN": "Air Transport",
    "ABX": "ABX Air",
    "CJT": "Cargojet",
    "BOE": "Boeing",

    # Canada & Mexico
    "ACA": "Air Canada",
    "ROU": "AC Rouge",
    "JZA": "Jazz",
    "WJA": "WestJet",
    "WEN": "Encore",
    "TSC": "Air Transat",
    "AMX": "Aeromexico",
    "SLI": "Aeromexico",
    "VOI": "Volaris",
    "VIV": "VivaAerobus",

    # Transpacific / Asia
    "ANA": "ANA",
    "JAL": "Japan Air",
    "KAL": "Korean Air",
    "AAR": "Asiana",
    "EVA": "EVA Air",
    "CAL": "China Air",
    "CPA": "Cathay",
    "HDA": "Cathay",
    "SIA": "Singapore",
    "SQC": "Singapore",
    "CCA": "Air China",
    "CES": "China East",
    "CSN": "China South",
    "CHH": "Hainan",
    "PAL": "Philippine",
    "THA": "Thai Air",
    "HVN": "Vietnam",
    "MAS": "Malaysia",
    "GIA": "Garuda",
    "AIC": "Air India",
    "QFA": "Qantas",
    "ANZ": "Air NZ",
    "VOZ": "Virgin Aust",
    "FJI": "Fiji Air",

    # Europe
    "BAW": "British Air",
    "VIR": "Virgin",
    "AFR": "Air France",
    "KLM": "KLM",
    "DLH": "Lufthansa",
    "GEC": "Lufthansa",
    "SWR": "Swiss",
    "AUA": "Austrian",
    "BEL": "Brussels",
    "IBE": "Iberia",
    "AEA": "Air Europa",
    "EIN": "Aer Lingus",
    "ICE": "Icelandair",
    "SAS": "SAS",
    "FIN": "Finnair",
    "AZA": "ITA",
    "TAP": "TAP Air",
    "THY": "Turkish",
    "LOT": "LOT",
    "EZY": "easyJet",
    "RYR": "Ryanair",
    "WZZ": "Wizz Air",

    # Middle East
    "UAE": "Emirates",
    "QTR": "Qatar",
    "ETD": "Etihad",
    "SVA": "Saudia",
    "ELY": "El Al",
    "RJA": "Royal Jordan",
    "KAC": "Kuwait",
}

IATA_PREFIX_MAP = {
    "AS": "Alaska",
    "DL": "Delta",
    "UA": "United",
    "AA": "American",
    "WN": "Southwest",
    "B6": "JetBlue",
    "F9": "Frontier",
    "NK": "Spirit",
    "HA": "Hawaiian",
    "AC": "Air Canada",
    "WS": "WestJet",
    "BA": "British Air",
    "AF": "Air France",
    "LH": "Lufthansa",
    "NH": "ANA",
    "JL": "Japan Air",
    "KE": "Korean Air",
    "BR": "EVA Air",
    "CI": "China Air",
    "CX": "Cathay",
    "SQ": "Singapore",
    "EK": "Emirates",
    "QR": "Qatar",
}

def resolve_airline(callsign: Optional[str]) -> str:
    """
    Resolve airline short brand name from an ICAO or IATA callsign.
    Example: 'ASA1762' -> 'Alaska', 'AS1762' -> 'Alaska'
    """
    if not callsign:
        return "Unknown"

    cs = callsign.strip().upper()
    if not cs:
        return "Unknown"

    # US general aviation registration check
    if cs.startswith("N") and len(cs) > 1 and cs[1].isdigit():
        return "General Av"

    # 3-letter ICAO prefix check
    prefix3 = cs[:3]
    if prefix3 in AIRLINES_SHORT:
        return AIRLINES_SHORT[prefix3]

    # 2-letter IATA prefix fallback
    prefix2 = cs[:2]
    if prefix2 in IATA_PREFIX_MAP:
        return IATA_PREFIX_MAP[prefix2]

    return cs
