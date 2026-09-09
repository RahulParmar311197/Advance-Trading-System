CANONICAL_SYMBOLS = {"NIFTY": "NIFTY", "BANKNIFTY": "BANKNIFTY"}

def canonical_symbol(symbol: str) -> str:
    key = symbol.strip().upper()
    if key not in CANONICAL_SYMBOLS:
        raise ValueError(f"unsupported symbol: {symbol}")
    return CANONICAL_SYMBOLS[key]
