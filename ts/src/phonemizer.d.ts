export declare class ArabicChar {
    readonly base: string;
    readonly marks: readonly string[];
    constructor(base: string, marks?: readonly string[]);
}
export declare class RuleHit {
    readonly symbol_index: number;
    readonly symbol: string;
    readonly rule: string;
    readonly source: string;
    constructor(symbol_index: number, symbol: string, rule: string, source: string);
}
export declare class WordSpan {
    readonly token: string;
    readonly start: number;
    readonly end: number;
    constructor(token: string, start: number, end: number);
}
export declare class PhonemizationResult {
    readonly symbols: string[];
    readonly rules: RuleHit[];
    readonly words: WordSpan[];
    constructor(symbols: string[], rules?: RuleHit[], words?: WordSpan[]);
    get text(): string;
}
export interface PhonemizerConfig {
    start_of_utterance?: boolean;
    wasl?: boolean;
    emit_pause?: boolean;
    waqf_on_pause?: boolean;
    cross_ayah_wasl?: boolean;
}
export declare class State {
    at_utterance_start: boolean;
    previous_vowel: string | null;
    pending_noon_index: number | null;
    pending_mim_index: number | null;
    after_pause: boolean;
    constructor(at_utterance_start: boolean);
}
export declare class Phonemizer {
    config: Required<PhonemizerConfig>;
    private _word_re;
    private _izhar;
    private _idgham_ghunna;
    private _idgham_no_ghunna;
    private _ikhfa;
    constructor(config?: PhonemizerConfig);
    phonemize(text: string): PhonemizationResult;
    private _tokens;
    private _split_pause_marks;
    private _is_pause_token;
    private _phonemize_word;
    private _cluster;
    private _skeleton;
    private _MUQATTAT_NAMES;
    private _MUQATTAT_SKELETONS;
    private _try_muqattaat;
    private _try_allah;
    private _allah_lam_symbol;
    private _emit_allah_core;
    private _article_start;
    private _prefixed_article_start;
    private _prefixed_wasla_start;
    private _prefixed_dropped_article_start;
    private _emit_article;
    private _emit_bare_article_lam;
    private _emit_initial_wasla;
    private _guess_wasla_vowel;
    private _emit_cluster;
    private _symbol_for_cluster;
    private _is_long_vowel_carrier;
    private _emit_vowel_and_madd;
    private _emit_carrier_hamza;
    private _emit_short_vowel;
    private _has_vowel;
    private _is_plain_madd_letter;
    private _is_sakin_like;
    private _has_hamza_mark;
    private _emit_trailing_hamza;
    private _is_idgham_pair;
    private _apply_iltiqa_sakinayn;
    private _starts_with_wasla;
    private _starts_with_hamza;
    private _upgrade_silah_before_hamza;
    private _upgrade_previous_vowel;
    private _emit;
    private _first_consonant;
    private _last_vowel;
    private _pending_noon_index_from_rules;
    private _pending_mim_index_from_rules;
    private _resolve_noon_within_word;
    private _resolve_pending_noon;
    private _apply_noon_assimilation;
    private _resolve_pending_mim;
    private _coalesce_leading_geminate_after;
    private _last_nonempty_symbol_index;
    private _next_consonant;
    private _apply_waqf_transformations;
    private _is_taa_marbuta;
    private _is_dagger_alef_madd;
}
//# sourceMappingURL=phonemizer.d.ts.map