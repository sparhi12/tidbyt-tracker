"""
Offline database of major airports (IATA / ICAO to City Name).
Provides instant, local resolution of airport codes to city names without network overhead.
"""

from typing import Optional, Tuple

AIRPORTS = {
    # Pacific Northwest / Local
    "KSEA": ("SEA", "Seattle"),
    "SEA": ("SEA", "Seattle"),
    "KBFI": ("BFI", "Seattle Boeing"),
    "BFI": ("BFI", "Seattle Boeing"),
    "KPAE": ("PAE", "Everett"),
    "PAE": ("PAE", "Everett"),
    "KPDX": ("PDX", "Portland"),
    "PDX": ("PDX", "Portland"),
    "KGEG": ("GEG", "Spokane"),
    "GEG": ("GEG", "Spokane"),
    "KPSC": ("PSC", "Pasco"),
    "PSC": ("PSC", "Pasco"),
    "KYKM": ("YKM", "Yakima"),
    "YKM": ("YKM", "Yakima"),
    "KBLI": ("BLI", "Bellingham"),
    "BLI": ("BLI", "Bellingham"),
    "KBOI": ("BOI", "Boise"),
    "BOI": ("BOI", "Boise"),

    # West Coast US
    "KSFO": ("SFO", "San Francisco"),
    "SFO": ("SFO", "San Francisco"),
    "KOAK": ("OAK", "Oakland"),
    "OAK": ("OAK", "Oakland"),
    "KSJC": ("SJC", "San Jose"),
    "SJC": ("SJC", "San Jose"),
    "KLAX": ("LAX", "Los Angeles"),
    "LAX": ("LAX", "Los Angeles"),
    "KSAN": ("SAN", "San Diego"),
    "SAN": ("SAN", "San Diego"),
    "KBUR": ("BUR", "Burbank"),
    "BUR": ("BUR", "Burbank"),
    "KSNA": ("SNA", "Orange County"),
    "SNA": ("SNA", "Orange County"),
    "KONT": ("ONT", "Ontario"),
    "ONT": ("ONT", "Ontario"),
    "KSMF": ("SMF", "Sacramento"),
    "SMF": ("SMF", "Sacramento"),
    "KLAS": ("LAS", "Las Vegas"),
    "LAS": ("LAS", "Las Vegas"),
    "KRNO": ("RNO", "Reno"),
    "RNO": ("RNO", "Reno"),
    "KPHX": ("PHX", "Phoenix"),
    "PHX": ("PHX", "Phoenix"),
    "KTUS": ("TUS", "Tucson"),
    "TUS": ("Tucson"),
    "KSLC": ("SLC", "Salt Lake City"),
    "SLC": ("SLC", "Salt Lake City"),
    "KDEN": ("DEN", "Denver"),
    "DEN": ("DEN", "Denver"),

    # Midwest US
    "KORD": ("ORD", "Chicago O'Hare"),
    "ORD": ("ORD", "Chicago O'Hare"),
    "KMDW": ("MDW", "Chicago Midway"),
    "MDW": ("MDW", "Chicago Midway"),
    "KMSP": ("MSP", "Minneapolis"),
    "MSP": ("MSP", "Minneapolis"),
    "KDTW": ("DTW", "Detroit"),
    "DTW": ("DTW", "Detroit"),
    "KSTL": ("STL", "St. Louis"),
    "STL": ("STL", "St. Louis"),
    "KMCI": ("MCI", "Kansas City"),
    "MCI": ("MCI", "Kansas City"),
    "KIND": ("IND", "Indianapolis"),
    "IND": ("IND", "Indianapolis"),
    "KCLE": ("CLE", "Cleveland"),
    "CLE": ("CLE", "Cleveland"),
    "KCMH": ("CMH", "Columbus"),
    "CMH": ("CMH", "Columbus"),
    "KMKE": ("MKE", "Milwaukee"),
    "MKE": ("MKE", "Milwaukee"),

    # South / Texas US
    "KDFW": ("DFW", "Dallas/Ft Worth"),
    "DFW": ("DFW", "Dallas/Ft Worth"),
    "KDAL": ("DAL", "Dallas Love"),
    "DAL": ("DAL", "Dallas Love"),
    "KIAH": ("IAH", "Houston Intercont"),
    "IAH": ("IAH", "Houston Intercont"),
    "KHOU": ("HOU", "Houston Hobby"),
    "HOU": ("HOU", "Houston Hobby"),
    "KAUS": ("AUS", "Austin"),
    "AUS": ("AUS", "Austin"),
    "KSAT": ("SAT", "San Antonio"),
    "SAT": ("SAT", "San Antonio"),
    "KATL": ("ATL", "Atlanta"),
    "ATL": ("ATL", "Atlanta"),
    "KBNA": ("BNA", "Nashville"),
    "BNA": ("BNA", "Nashville"),
    "KMEM": ("MEM", "Memphis"),
    "MEM": ("MEM", "Memphis"),
    "KCLT": ("CLT", "Charlotte"),
    "CLT": ("CLT", "Charlotte"),
    "KRDU": ("RDU", "Raleigh"),
    "RDU": ("RDU", "Raleigh"),
    "KMIA": ("MIA", "Miami"),
    "MIA": ("MIA", "Miami"),
    "KFLL": ("FLL", "Ft Lauderdale"),
    "FLL": ("FLL", "Ft Lauderdale"),
    "KMCO": ("MCO", "Orlando"),
    "MCO": ("MCO", "Orlando"),
    "KTPA": ("TPA", "Tampa"),
    "TPA": ("TPA", "Tampa"),
    "KRSW": ("RSW", "Fort Myers"),
    "RSW": ("Fort Myers"),
    "KJAX": ("JAX", "Jacksonville"),
    "JAX": ("JAX", "Jacksonville"),
    "KMSY": ("MSY", "New Orleans"),
    "MSY": ("MSY", "New Orleans"),

    # East Coast / Northeast US
    "KJFK": ("JFK", "New York JFK"),
    "JFK": ("JFK", "New York JFK"),
    "KLGA": ("LGA", "New York LaGuardia"),
    "LGA": ("LGA", "New York LaGuardia"),
    "KEWR": ("EWR", "Newark"),
    "EWR": ("EWR", "Newark"),
    "KBOS": ("BOS", "Boston"),
    "BOS": ("BOS", "Boston"),
    "KIAD": ("IAD", "Washington Dulles"),
    "IAD": ("IAD", "Washington Dulles"),
    "KDCA": ("DCA", "Washington Reagan"),
    "DCA": ("DCA", "Washington Reagan"),
    "KBWI": ("BWI", "Baltimore"),
    "BWI": ("BWI", "Baltimore"),
    "KPHL": ("PHL", "Philadelphia"),
    "PHL": ("PHL", "Philadelphia"),
    "KPIT": ("PIT", "Pittsburgh"),
    "PIT": ("PIT", "Pittsburgh"),

    # Alaska & Hawaii
    "PANC": ("ANC", "Anchorage"),
    "ANC": ("ANC", "Anchorage"),
    "PAFA": ("FAI", "Fairbanks"),
    "FAI": ("FAI", "Fairbanks"),
    "PAJN": ("JNU", "Juneau"),
    "JNU": ("JNU", "Juneau"),
    "PHNL": ("HNL", "Honolulu"),
    "HNL": ("HNL", "Honolulu"),
    "PHOG": ("OGG", "Maui Kahului"),
    "OGG": ("OGG", "Maui Kahului"),
    "PHKO": ("KOA", "Kona Hawaii"),
    "KOA": ("KOA", "Kona Hawaii"),
    "PHLI": ("LIH", "Kauai Lihue"),
    "LIH": ("LIH", "Kauai Lihue"),

    # Canada & Mexico
    "CYVR": ("YVR", "Vancouver"),
    "YVR": ("YVR", "Vancouver"),
    "CYYZ": ("YYZ", "Toronto"),
    "YYZ": ("YYZ", "Toronto"),
    "CYUL": ("YUL", "Montreal"),
    "YUL": ("YUL", "Montreal"),
    "CYYC": ("YYC", "Calgary"),
    "YYC": ("YYC", "Calgary"),
    "CYEG": ("YEG", "Edmonton"),
    "YEG": ("YEG", "Edmonton"),
    "CYVJ": ("YVJ", "Victoria"),
    "MMMX": ("MEX", "Mexico City"),
    "MEX": ("MEX", "Mexico City"),
    "MMSD": ("SJD", "Cabo San Lucas"),
    "SJD": ("SJD", "Cabo San Lucas"),
    "MMPR": ("PVR", "Puerto Vallarta"),
    "PVR": ("PVR", "Puerto Vallarta"),
    "MMUN": ("CUN", "Cancun"),
    "CUN": ("CUN", "Cancun"),

    # Europe
    "EGLL": ("LHR", "London Heathrow"),
    "LHR": ("LHR", "London Heathrow"),
    "EGKK": ("LGW", "London Gatwick"),
    "LGW": ("LGW", "London Gatwick"),
    "LFPG": ("CDG", "Paris Charles"),
    "CDG": ("CDG", "Paris Charles"),
    "EDDF": ("FRA", "Frankfurt"),
    "FRA": ("FRA", "Frankfurt"),
    "EDDM": ("MUC", "Munich"),
    "MUC": ("MUC", "Munich"),
    "EHAM": ("AMS", "Amsterdam"),
    "AMS": ("AMS", "Amsterdam"),
    "BIKF": ("KEF", "Reykjavik"),
    "KEF": ("KEF", "Reykjavik"),
    "EIDW": ("DUB", "Dublin"),
    "DUB": ("DUB", "Dublin"),
    "LEMD": ("MAD", "Madrid"),
    "MAD": ("MAD", "Madrid"),
    "LEBL": ("BCN", "Barcelona"),
    "BCN": ("BCN", "Barcelona"),
    "LIRF": ("FCO", "Rome"),
    "FCO": ("FCO", "Rome"),
    "LSZH": ("ZRH", "Zurich"),
    "ZRH": ("ZRH", "Zurich"),

    # Asia & Pacific
    "RJTT": ("HND", "Tokyo Haneda"),
    "HND": ("HND", "Tokyo Haneda"),
    "RJAA": ("NRT", "Tokyo Narita"),
    "NRT": ("NRT", "Tokyo Narita"),
    "RKSI": ("ICN", "Seoul Incheon"),
    "ICN": ("ICN", "Seoul Incheon"),
    "RCTP": ("TPE", "Taipei"),
    "TPE": ("TPE", "Taipei"),
    "VHHH": ("HKG", "Hong Kong"),
    "HKG": ("HKG", "Hong Kong"),
    "WSSS": ("SIN", "Singapore"),
    "SIN": ("SIN", "Singapore"),
    "ZBAA": ("PEK", "Beijing"),
    "PEK": ("PEK", "Beijing"),
    "ZSPD": ("PVG", "Shanghai"),
    "PVG": ("PVG", "Shanghai"),
    "OMDB": ("DXB", "Dubai"),
    "DXB": ("DXB", "Dubai"),
    "OTHH": ("DOH", "Doha"),
    "DOH": ("DOH", "Doha"),
    "YSSY": ("SYD", "Sydney"),
    "SYD": ("SYD", "Sydney"),
    "NZAA": ("AKL", "Auckland"),
    "AKL": ("AKL", "Auckland"),
}

def resolve_airport(raw_code: Optional[str]) -> Tuple[str, str]:
    """
    Resolve an ICAO or IATA airport code into (IATA_display_code, City_name).
    Example: 'KPDX' -> ('PDX', 'Portland')
    """
    if not raw_code:
        return ("---", "Unknown")

    code = raw_code.strip().upper()
    if code in AIRPORTS:
        return AIRPORTS[code]

    # For 4-letter US ICAO starting with 'K', check stripped 3-letter IATA
    if len(code) == 4 and code.startswith("K"):
        iata_candidate = code[1:]
        if iata_candidate in AIRPORTS:
            return AIRPORTS[iata_candidate]
        return (iata_candidate, iata_candidate)

    # For 4-letter Canadian ICAO starting with 'C', check stripped 3-letter
    if len(code) == 4 and code.startswith("C"):
        iata_candidate = code[1:]
        if iata_candidate in AIRPORTS:
            return AIRPORTS[iata_candidate]
        return (iata_candidate, iata_candidate)

    return (code, code)
