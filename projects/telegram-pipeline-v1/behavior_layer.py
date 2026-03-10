from typing import Any, Dict, List, Optional


def _has_trading_structure(text: str) -> bool:
    t = (text or "").lower()
    has_asset = any(k in t for k in ["btc", "eth", "sol", "link", "brent", "биток", "эфир", "солана", "сол", "линк", "брент", "дед"])
    has_numbers = bool(__import__("re").search(r"\$|%|\b\d+(?:[\.,]\d+)?\s*[-–]\s*\d+(?:[\.,]\d+)?\s*[kк]?\b", t))
    has_trading_words = any(k in t for k in ["лонг", "шорт", "вверх", "вниз", "цель", "стоп", "вход", "уровень", "зона", "диапазон", "позиция", "закрыл", "закрыла", "взял", "взяла", "беру"])
    return has_asset or has_numbers or has_trading_words


def _is_smalltalk_or_comment(text: str) -> bool:
    t = (text or "").lower().strip()
    if not t:
        return True
    if "?" in t and not any(k in t for k in ["лонг", "шорт", "вход", "стоп", "цель", "закрыл", "взял", "беру"]):
        return True
    markers = [
        "откуда", "кто", "почему", "как думаешь", "что думаешь", "спасибо", "доброе утро", "всем привет",
        "ты же", "сегодня стрим", "в офисе", "как дела",
    ]
    return any(m in t for m in markers)


def update_context(context_store: Dict[str, List[Dict[str, Any]]], trader_id: str, message: Dict[str, Any]) -> List[Dict[str, Any]]:
    tid = (trader_id or "unknown").lower()
    arr = context_store.get(tid, [])
    arr.append(message)
    if len(arr) > 12:
        arr = arr[-12:]
    context_store[tid] = arr
    return arr


def build_context_bundle(window: List[Dict[str, Any]], current_index: Optional[int] = None) -> str:
    if not window:
        return ""
    i = len(window) - 1 if current_index is None else max(0, min(current_index, len(window) - 1))
    lo = max(0, i - 3)
    hi = min(len(window), i + 4)
    parts: List[str] = []
    for m in window[lo:hi]:
        txt = (m.get("text") or "").strip()
        if txt:
            parts.append(txt)
        elif m.get("has_media"):
            parts.append("[media]")
    return "\n".join(parts).strip()


def normalize_state(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["вход", "лонг", "шорт", "зашел", "зашла", "открыл", "открыла"]):
        return "ENTRY"
    if any(k in t for k in ["прикрыл", "частично закрыл", "часть закрыл", "часть закрыла"]):
        return "PARTIAL_EXIT"
    if any(k in t for k in ["закрыл все", "закрыла все", "вышел", "вышла", "закрыто"]):
        return "EXIT"
    if any(k in t for k in ["стоп в бу", "в б/у", "безуб", "break even", "breakeven"]):
        return "B_E_UPDATE"
    if any(k in t for k in ["перенес стоп", "новый стоп", "stop moved", "подвинул стоп"]):
        return "STOP_UPDATE"
    if any(k in t for k in ["уровень", "не терять", "удержать", "если потеряем", "если не удержим"]):
        return "LEVEL_UPDATE"
    if any(k in t for k in ["держу", "удерживаю", "hold"]):
        return "HOLD"
    return "MARKET_VIEW"


def apply_behavior_profile(
    trader_id: str,
    text: str,
    has_media: bool,
    media_kind: Optional[str],
    context_window: List[Dict[str, Any]],
    callbacks: Dict[str, Any],
    tv_link: bool = False,
    signal_threshold: int = 6,
    is_reply: bool = False,
) -> Dict[str, Any]:
    trader = (trader_id or "").lower()
    bundle_text = build_context_bundle(context_window)
    state_type = normalize_state(bundle_text or text)
    reasons: List[str] = ["TRADER_BEHAVIOR_APPLIED"]

    main_pass = False
    signal_pass = False
    signal_data: Dict[str, Any] = {"pass": False, "reason": "SIGNAL_NO_STRUCTURE", "confidence": 0}
    main_result: Dict[str, Any] = {"pass": False, "type": "VIEW", "reason": "DROP"}

    has_promo_spam = callbacks.get("has_promo_spam")
    if callable(has_promo_spam) and has_promo_spam(text):
        return {
            "main_pass": False,
            "signal_pass": False,
            "state_type": "MARKET_VIEW",
            "debug_reasons": reasons + ["DROP_PROMO_SPAM"],
            "bundle_text": bundle_text,
            "signal_data": {"pass": False, "reason": "DROP_PROMO_SPAM", "confidence": 0, "signal_type": "DROP"},
            "main_result": {"pass": False, "type": "DROP", "reason": "DROP_PROMO_SPAM"},
        }

    word_count = len([w for w in (text or "").split() if w])
    if is_reply and (not _has_trading_structure(text)) and word_count < 20:
        return {
            "main_pass": False,
            "signal_pass": False,
            "state_type": "MARKET_VIEW",
            "debug_reasons": reasons + ["DROP_DISCUSSION"],
            "bundle_text": bundle_text,
            "signal_data": {"pass": False, "reason": "DROP_DISCUSSION", "confidence": 0, "signal_type": "DROP"},
            "main_result": {"pass": False, "type": "DISCUSSION", "reason": "DROP_DISCUSSION"},
        }

    if tv_link:
        main_pass = True
        reasons.append("TRADINGVIEW_FORCE_MAIN")

    if trader == "artur":
        classify_artur_main = callbacks.get("classify_artur_main")
        parse_artur_signal = callbacks.get("parse_artur_signal")

        short_signal_words = ["газ", "делаем", "пробуем", "погнали", "шорчу", "держу", "закрываю", "стоп словлю", "удерживаю", "попробуем", "берем", "сделал", "зашел"]
        has_short_signal = any(w in (text or "").lower() for w in short_signal_words)

        if has_media and not (text or "").strip():
            main_pass = True
            main_result = {"pass": True, "type": "VIEW", "reason": "MAIN_FROM_CONTEXT"}
            reasons.append("MAIN_FROM_CONTEXT")
        else:
            mr = classify_artur_main(text) if callable(classify_artur_main) else {"pass": True, "type": "VIEW", "reason": "PASS_VIEW"}
            main_pass = main_pass or bool(mr.get("pass"))
            main_result = mr

        bundle = bundle_text if has_short_signal else (text or "")
        if has_short_signal and bundle_text:
            reasons.append("CONTEXT_BUNDLE_CREATED")
        sig = parse_artur_signal(bundle) if callable(parse_artur_signal) and bundle.strip() else {"pass": False, "reason": "ARTUR_SIGNAL_DROP", "confidence": 0}
        signal_data = sig
        signal_pass = bool(sig.get("pass"))
        if signal_pass and has_short_signal:
            reasons.append("SIGNAL_FROM_CONTEXT")

    elif trader == "ilya":
        classify_main_ilya_message = callbacks.get("classify_main_ilya_message")
        parse_ilya_signal = callbacks.get("parse_ilya_signal")
        rules = callbacks.get("rules") or {}
        ilya_main_filter_enabled = bool(callbacks.get("ilya_main_filter_enabled", True))

        if callable(classify_main_ilya_message):
            main_result = classify_main_ilya_message(text, has_media=has_media, rules=rules) if ilya_main_filter_enabled else {"pass": True, "score": 0, "type": "VIEW", "reason": "PASS_VIEW"}
            main_pass = main_pass or bool(main_result.get("pass"))
        else:
            main_pass = True
            main_result = {"pass": True, "type": "VIEW", "reason": "PASS_MAIN_MARKET_VIEW"}

        if callable(parse_ilya_signal):
            signal_data = parse_ilya_signal(text, rules)
            signal_pass = bool(signal_data.get("pass"))

        if _is_smalltalk_or_comment(text):
            main_pass = False
            signal_pass = False
            main_result = {"pass": False, "type": "SMALLTALK", "reason": "DROP_SMALLTALK"}
            signal_data = {"pass": False, "reason": "DROP_SMALLTALK", "confidence": 0, "signal_type": "DROP"}
            reasons.append("DROP_SMALLTALK")

    elif trader in {"evelina", "eli"}:
        parse_generic_signal = callbacks.get("parse_generic_signal")
        main_pass = True
        main_result = {"pass": True, "type": "MARKET_VIEW", "reason": "PASS_MAIN_MARKET_VIEW"}
        if callable(parse_generic_signal):
            signal_data = parse_generic_signal(text, threshold=signal_threshold, trader_id=trader)
            signal_pass = bool(signal_data.get("pass"))
            st = (signal_data.get("signal_type") or "").upper()
            if st == "CONDITIONAL_ENTRY":
                main_result = {"pass": True, "type": "SCENARIO", "reason": "PASS_SCENARIO"}
            elif st == "EXIT":
                main_result = {"pass": True, "type": "EXIT", "reason": "PASS_EXIT"}
            elif st in {"LONG_ENTRY", "SHORT_ENTRY"}:
                main_result = {"pass": True, "type": "SIGNAL", "reason": "PASS_SIGNAL"}
            if bool(signal_data.get("stop_inferred", False)):
                reasons.append("IMPLICIT_STOP_INFERRED")
        if _is_smalltalk_or_comment(text):
            main_pass = False
            signal_pass = False
            main_result = {"pass": False, "type": "SMALLTALK", "reason": "DROP_SMALLTALK"}
            signal_data = {"pass": False, "reason": "DROP_SMALLTALK", "confidence": 0, "signal_type": "DROP"}
            reasons.append("DROP_SMALLTALK")

    elif trader == "irina":
        # Any TradingView for Irina: MAIN only, never SIGNAL.
        main_pass = True
        main_result = {"pass": True, "type": "VIEW", "reason": "PASS_MAIN_MARKET_VIEW"}
        signal_data = {"pass": False, "reason": "IRINA_SIGNAL_OFF", "confidence": 0}
        signal_pass = False

    elif trader == "psy":
        parse_generic_signal = callbacks.get("parse_generic_signal")
        main_pass = True
        main_result = {"pass": True, "type": "VIEW", "reason": "PASS_MAIN_MARKET_VIEW"}
        if callable(parse_generic_signal):
            sig = parse_generic_signal(text, threshold=signal_threshold, trader_id=trader)
            signal_data = sig
            signal_pass = has_media and bool(sig.get("pass"))

    else:
        parse_generic_signal = callbacks.get("parse_generic_signal")
        main_pass = True
        main_result = {"pass": True, "type": "VIEW", "reason": "PASS_MAIN_MARKET_VIEW"}
        if callable(parse_generic_signal):
            signal_data = parse_generic_signal(text, threshold=signal_threshold, trader_id=trader)
            signal_pass = bool(signal_data.get("pass"))

    base_min_signal_conf = int(callbacks.get("signal_min_confidence", 4) or 4)
    min_conf_by_trader = {"evelina": 2, "eli": 2, "altador": 2, "ilya": 4, "artur": 4}
    min_signal_conf = int(min_conf_by_trader.get(trader, base_min_signal_conf))
    conf_final = int(signal_data.get("confidence_final", signal_data.get("confidence", 0)) or 0)
    sig_type = (signal_data.get("signal_type") or "").upper()
    explicit_exit_words = ["закрыла", "закрыл", "вышла", "вышел"]
    explicit_exit = sig_type == "EXIT" and any(w in (text or "").lower() for w in explicit_exit_words)
    if signal_pass and (conf_final < min_signal_conf) and not explicit_exit:
        signal_pass = False
        reasons.append(f"SIGNAL_CONF_LT_{min_signal_conf}")
        if not main_pass:
            main_pass = True
            main_result = {"pass": True, "type": "MARKET_VIEW", "reason": "LOW_CONF_TO_MAIN"}

    if state_type == "HOLD":
        reasons.append("HOLD_STATE_DETECTED")
    if state_type in {"EXIT", "PARTIAL_EXIT"}:
        reasons.append("EXIT_STATE_DETECTED")
    if state_type == "B_E_UPDATE":
        reasons.append("B_E_DETECTED")

    if tv_link:
        main_result = {"pass": True, "type": main_result.get("type") or "VIEW", "reason": "PASS_MAIN_TRADINGVIEW", "hold_only": False}
        main_pass = True

    return {
        "main_pass": bool(main_pass),
        "signal_pass": bool(signal_pass),
        "state_type": state_type,
        "debug_reasons": reasons,
        "bundle_text": bundle_text,
        "signal_data": signal_data,
        "main_result": main_result,
    }
