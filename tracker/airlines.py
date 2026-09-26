"""
Offline ICAO airline code database.
Maps 3-letter ICAO callsign prefixes to official airline names.
"""

from typing import Optional

AIRLINES_ICAO = {
    # Major US Carriers
    "ASA": "Alaska Airlines",
    "QXE": "Horizon Air",
    "DAL": "Delta Air Lines",
    "UAL": "United Airlines",
    "AAL": "American Airlines",
    "SWA": "Southwest Airlines",
    "JBU": "JetBlue Airways",
    "FFT": "Frontier Airlines",
    "NKS": "Spirit Airlines",
    "HAL": "Hawaiian Airlines",
    "SKW": "SkyWest Airlines",
    "EDV": "Endeavor Air",
    "ENY": "Envoy Air",
    "RPA": "Republic Airways",
    "PSA": "PSA Airlines",
    "PDT": "Piedmont Airlines",
    "GJS": "GoJet Airlines",
    "AWI": "Air Wisconsin",
    "CPZ": "Compass Airlines",
    "MCO": "Mesa Airlines",
    "ASH": "Mesa Airlines",
    "SCX": "Sun Country Airlines",
    "AAY": "Allegiant Air",
    "MXY": "Breeze Airways",
    "VRD": "Virgin America",

    # Cargo / Logistics
    "FDX": "FedEx Express",
    "UPS": "UPS Airlines",
    "GTI": "Atlas Air",
    "PAC": "Polar Air Cargo",
    "ATN": "Air Transport Int'l",
    "ABX": "ABX Air",
    "CJT": "Cargojet Airways",
    "BOE": "Boeing Test Flight",

    # Canada & Mexico
    "ACA": "Air Canada",
    "ROU": "Air Canada Rouge",
    "JZA": "Jazz Aviation",
    "WJA": "WestJet",
    "WEN": "Encore Air",
    "TSC": "Air Transat",
    "AMX": "Aeromexico",
    "SLI": "Aeromexico Connect",
    "VOI": "Volaris",
    "VIV": "VivaAerobus",

    # Transpacific / Asia
    "ANA": "All Nippon Airways",
    "JAL": "Japan Airlines",
    "KAL": "Korean Air",
    "AAR": "Asiana Airlines",
    "EVA": "EVA Air",
    "CAL": "China Airlines",
    "CPA": "Cathay Pacific",
    "HDA": "Cathay Dragon",
    "SIA": "Singapore Airlines",
    "SQC": "Singapore Cargo",
    "CCA": "Air China",
    "CES": "China Eastern Airlines",
    "CSN": "China Southern Airlines",
    "CHH": "Hainan Airlines",
    "PAL": "Philippine Airlines",
    "THA": "Thai Airways",
    "HVN": "Vietnam Airlines",
    "MAS": "Malaysia Airlines",
    "GIA": "Garuda Indonesia",
    "AIC": "Air India",
    "QFA": "Qantas",
    "ANZ": "Air New Zealand",
    "VOZ": "Virgin Australia",
    "FJI": "Fiji Airways",

    # Europe
    "BAW": "British Airways",
    "VIR": "Virgin Atlantic",
    "AFR": "Air France",
    "KLM": "KLM Royal Dutch",
    "DLH": "Lufthansa",
    "GEC": "Lufthansa Cargo",
    "SWR": "Swiss Int'l Air Lines",
    "AUA": "Austrian Airlines",
    "BEL": "Brussels Airlines",
    "IBE": "Iberia",
    "AEA": "Air Europa",
    "EIN": "Aer Lingus",
    "ICE": "Icelandair",
    "SAS": "SAS Scandinavian",
    "FIN": "Finnair",
    "AZA": "ITA Airways",
    "TAP": "TAP Air Portugal",
    "THY": "Turkish Airlines",
    "LOT": "LOT Polish Airlines",
    "EZY": "easyJet",
    "RYR": "Ryanair",
    "WZZ": "Wizz Air",
    "NOS": "Neos",

    # Middle East
    "UAE": "Emirates",
    "QTR": "Qatar Airways",
    "ETD": "Etihad Airways",
    "SVA": "Saudia",
    "ELY": "El Al Israel Airlines",
    "RJA": "Royal Jordanian",
    "KAC": "Kuwait Airways",
    "GFA": "Gulf Air",
    "OMA": "Oman Air",
}

def resolve_airline(callsign: Optional[str]) -> str:
    """
    Resolve airline commercial name from an ICAO callsign (e.g. 'ASA1762' -> 'Alaska Airlines').
    """
    if not callsign:
        return "Unknown Flight"

    cs = callsign.strip().upper()
    if not cs:
        return "Unknown Flight"

    # US general aviation registration check (starts with 'N' and next char is a digit)
    if cs.startswith("N") and len(cs) > 1 and cs[1].isdigit():
        return "General Aviation"

    # 3-letter ICAO prefix check
    prefix3 = cs[:3]
    if prefix3 in AIRLINES_ICAO:
        return AIRLINES_ICAO[prefix3]

    # 2-letter IATA prefix fallback (e.g. 'AS1762')
    prefix2 = cs[:2]
    iata_mapping = {
        "AS": "Alaska Airlines",
        "DL": "Delta Air Lines",
        "UA": "United Airlines",
        "AA": "American Airlines",
        "WN": "Southwest Airlines",
        "B6": "JetBlue Airways",
        "F9": "Frontier Airlines",
        "NK": "Spirit Airlines",
        "HA": "Hawaiian Airlines",
        "AC": "Air Canada",
        "WS": "WestJet",
        "BA": "British Airways",
        "AF": "Air France",
        "LH": "Lufthansa",
        "NH": "All Nippon Airways",
        "JL": "Japan Airlines",
        "KE": "Korean Air",
        "BR": "EVA Air",
        "CI": "China Airlines",
        "CX": "Cathay Pacific",
        "SQ": "Singapore Airlines",
        "EK": "Emirates",
        "QR": "Qatar Airways",
    }
    if prefix2 in iata_mapping:
        return iata_mapping[prefix2]

    return f"Flight {cs}"
