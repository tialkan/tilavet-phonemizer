import {
    ALEF, ALEF_MADDA, ALEF_MAQSURA, ALEF_WASLA, DAGGER_ALEF, DAMMA, DAMMATAN,
    DIACRITICS, FATHA, FATHATAN, HAMZA_ABOVE, HAMZA_BELOW, HAMZA_LETTERS,
    IDGHAM_HOMORGANIC_PAIRS, IGNORABLE, KASRA, KASRATAN, LETTER_TO_SYMBOL,
    MADDAH, QALQALAH, SHADDA, SMALL_KASRA, SMALL_WAW, SMALL_YA, STOP_SIGNS,
    SUKUN, SUN_LETTERS, VOWELS
} from './arabic';

export class ArabicChar {
    constructor(
        public readonly base: string,
        public readonly marks: readonly string[] = []
    ) {}
}

export class RuleHit {
    constructor(
        public readonly symbol_index: number,
        public readonly symbol: string,
        public readonly rule: string,
        public readonly source: string
    ) {}
}

export class WordSpan {
    constructor(
        public readonly token: string,
        public readonly start: number,
        public readonly end: number
    ) {}
}

export class PhonemizationResult {
    constructor(
        public readonly symbols: string[],
        public readonly rules: RuleHit[] = [],
        public readonly words: WordSpan[] = []
    ) {}

    get text(): string {
        return this.symbols.filter(s => s).join(" ");
    }
}

export interface PhonemizerConfig {
    start_of_utterance?: boolean;
    wasl?: boolean;
    emit_pause?: boolean;
    waqf_on_pause?: boolean;
    cross_ayah_wasl?: boolean;
}

export class State {
    public at_utterance_start: boolean;
    public previous_vowel: string | null = null;
    public pending_noon_index: number | null = null;
    public pending_mim_index: number | null = null;
    public after_pause: boolean = false;

    constructor(at_utterance_start: boolean) {
        this.at_utterance_start = at_utterance_start;
    }
}

export class Phonemizer {
    public config: Required<PhonemizerConfig>;

    private _word_re = /\s+/;
    private _izhar = new Set(["'", "h", "3", "H", "gh", "kh"]);
    private _idgham_ghunna = new Set(["y", "n", "m", "w"]);
    private _idgham_no_ghunna = new Set(["l", "r", "L"]);
    private _ikhfa = new Set(["t", "th", "j", "d", "dh", "z", "s", "sh", "S", "D", "T", "Z", "f", "q", "k"]);

    constructor(config?: PhonemizerConfig) {
        this.config = {
            start_of_utterance: true,
            wasl: true,
            emit_pause: true,
            waqf_on_pause: false,
            cross_ayah_wasl: false,
            ...config
        };
    }

    public phonemize(text: string): PhonemizationResult {
        const state = new State(this.config.start_of_utterance);
        const symbols: string[] = [];
        const rules: RuleHit[] = [];
        const words: WordSpan[] = [];

        for (const raw_token of this._tokens(text)) {
            if (this._is_pause_token(raw_token)) {
                if (this.config.emit_pause) {
                    if (this.config.waqf_on_pause) {
                        this._resolve_pending_noon(state, null, symbols, rules, raw_token);
                        if (words.length > 0) {
                            this._apply_waqf_transformations(symbols, rules, words[words.length - 1], raw_token);
                        }
                    }
                    if (!this.config.cross_ayah_wasl) {
                        symbols.push("PAUSE");
                        rules.push(new RuleHit(symbols.length - 1, "PAUSE", "pause_mark", raw_token));
                        state.after_pause = true;
                    }
                }
                continue;
            }

            const [word_symbols, word_rules] = this._phonemize_word(raw_token, state);
            if (word_symbols.length === 0) {
                continue;
            }

            this._resolve_pending_noon(state, this._first_consonant(word_symbols), symbols, rules, raw_token);
            this._coalesce_leading_geminate_after(symbols, word_symbols, word_rules, "m_g", "m");
            this._resolve_pending_mim(state, word_symbols, word_rules, symbols, rules, raw_token);
            this._upgrade_silah_before_hamza(symbols, rules, word_symbols, raw_token);
            if (!(this.config.waqf_on_pause && state.after_pause)) {
                this._apply_iltiqa_sakinayn(symbols, rules, raw_token);
            }
            state.after_pause = false;

            const start = symbols.length;
            symbols.push(...word_symbols);
            for (const hit of word_rules) {
                rules.push(new RuleHit(
                    start + hit.symbol_index,
                    hit.symbol,
                    hit.rule,
                    hit.source
                ));
            }
            const end = symbols.length;
            words.push(new WordSpan(raw_token, start, end));

            state.pending_noon_index = this._pending_noon_index_from_rules(rules, symbols, start, end);
            state.pending_mim_index = this._pending_mim_index_from_rules(rules, symbols, start, end);
            state.previous_vowel = this._last_vowel(symbols);
            state.at_utterance_start = false;
        }

        this._resolve_pending_noon(state, null, symbols, rules, "");
        return new PhonemizationResult(symbols, rules, words);
    }

    private *_tokens(text: string): IterableIterator<string> {
        for (const token of text.trim().split(this._word_re)) {
            if (!token) continue;
            yield* this._split_pause_marks(token);
        }
    }

    private _split_pause_marks(token: string): string[] {
        const parts: string[] = [];
        let current: string[] = [];
        for (const char of token) {
            if (STOP_SIGNS.has(char)) {
                if (current.length > 0) {
                    parts.push(current.join(''));
                    current = [];
                }
                parts.push(char);
            } else {
                current.push(char);
            }
        }
        if (current.length > 0) {
            parts.push(current.join(''));
        }
        return parts;
    }

    private _is_pause_token(token: string): boolean {
        if (!token) return false;
        for (const char of token) {
            if (!STOP_SIGNS.has(char)) return false;
        }
        return true;
    }

    private _phonemize_word(token: string, state: State): [string[], RuleHit[]] {
        const clusters = this._cluster(token);
        if (clusters.length === 0) {
            return [[], []];
        }

        const muqattaat = this._try_muqattaat(clusters, token);
        if (muqattaat !== null) {
            return muqattaat;
        }

        const allah = this._try_allah(clusters, state, token);
        if (allah !== null) {
            return allah;
        }

        const out: string[] = [];
        const rules: RuleHit[] = [];
        let index = 0;

        const prefixed_article_start = this._prefixed_article_start(clusters);
        const prefixed_dropped = this._prefixed_dropped_article_start(clusters);

        if (prefixed_article_start !== null) {
            index = this._emit_cluster(clusters, 0, token, out, rules);
            const local_state = new State(false);
            local_state.previous_vowel = this._last_vowel(out);
            index = this._emit_article(clusters, prefixed_article_start, local_state, token, out, rules);
        } else if (prefixed_dropped !== null) {
            index = this._emit_cluster(clusters, 0, token, out, rules);
            index = this._emit_bare_article_lam(clusters, prefixed_dropped, token, out, rules);
        } else if (this._prefixed_wasla_start(clusters) !== null) {
            index = this._emit_cluster(clusters, 0, token, out, rules);
            index = 2;
        } else {
            const article_start = this._article_start(clusters);
            if (article_start !== null) {
                index = this._emit_article(clusters, article_start, state, token, out, rules);
            } else if (clusters[0].base === ALEF_WASLA) {
                index = this._emit_initial_wasla(clusters, state, token, out, rules);
            }
        }

        while (index < clusters.length) {
            index = this._emit_cluster(clusters, index, token, out, rules);
        }

        this._resolve_noon_within_word(out, rules, token);
        return [out, rules];
    }

    private _cluster(token: string): ArabicChar[] {
        const clusters: ArabicChar[] = [];
        for (const char of token) {
            if (char === SMALL_WAW || char === SMALL_YA) {
                if (clusters.length > 0) {
                    const previous = clusters[clusters.length - 1];
                    clusters[clusters.length - 1] = new ArabicChar(previous.base, [...previous.marks, char]);
                }
                continue;
            }
            if (IGNORABLE.has(char)) {
                continue;
            }
            if (DIACRITICS.has(char)) {
                if (clusters.length > 0) {
                    const previous = clusters[clusters.length - 1];
                    clusters[clusters.length - 1] = new ArabicChar(previous.base, [...previous.marks, char]);
                }
                continue;
            }
            if (STOP_SIGNS.has(char) || char.trim() === '') {
                continue;
            }
            clusters.push(new ArabicChar(char, []));
        }
        return clusters;
    }

    private _skeleton(clusters: ArabicChar[]): string {
        return clusters
            .filter(cluster => !IGNORABLE.has(cluster.base))
            .map(cluster => cluster.base)
            .join('');
    }

    private _MUQATTAT_NAMES: Record<string, [string[], number, string]> = {
        "ا": [["'", "a", "l", "i", "f"], 3, "i"],
        "ل": [["l", "aa", "m"], 1, "a"],
        "م": [["m", "ii", "m"], 1, "i"],
        "ي": [["y", "aa"], 1, "a"],
        "س": [["s", "ii", "n"], 1, "i"],
        "ك": [["k", "aa", "f"], 1, "a"],
        "ه": [["h", "aa"], 1, "a"],
        "ع": [["3", "a", "y", "n"], 1, "a"],
        "ص": [["S", "aa", "d"], 1, "a"],
        "ط": [["T", "aa"], 1, "a"],
        "ح": [["H", "aa"], 1, "a"],
        "ن": [["n", "uu", "n"], 1, "u"],
        "ق": [["q", "aa", "f"], 1, "a"],
        "ر": [["r", "aa"], 1, "a"],
    };

    private _MUQATTAT_SKELETONS = new Set([
        "الم", "المص", "المر", "كهيعص", "طه", "طسم", "طس",
        "يس", "ص", "حم", "حمعسق", "عسق", "ق", "ن",
    ]);

    private _try_muqattaat(clusters: ArabicChar[], token: string): [string[], RuleHit[]] | null {
        const skeleton = this._skeleton(clusters);
        if (!this._MUQATTAT_SKELETONS.has(skeleton)) return null;

        for (const cluster of clusters) {
            if (!(cluster.base in this._MUQATTAT_NAMES)) return null;
        }

        const out: string[] = [];
        const rules: RuleHit[] = [];

        for (const cluster of clusters) {
            const [name_phonemes, madd_idx, madd_vowel] = this._MUQATTAT_NAMES[cluster.base];
            const has_madd = cluster.marks.includes(MADDAH);

            if (has_madd && madd_idx < name_phonemes.length) {
                for (let i = 0; i < name_phonemes.length; i++) {
                    const ph = name_phonemes[i];
                    if (i === madd_idx) {
                        if (madd_vowel === "a") out.push("aa6");
                        else if (madd_vowel === "i") out.push("ii6");
                        else if (madd_vowel === "u") out.push("uu6");
                        else out.push(ph);
                    } else {
                        out.push(ph);
                    }
                }
            } else {
                out.push(...name_phonemes);
            }
        }

        const idgham_ghunna = new Set(["y", "n", "m", "w"]);
        for (let i = 0; i < out.length - 1; i++) {
            const sym = out[i];
            const nxt = out[i + 1];
            if (sym === "n" && (this._ikhfa.has(nxt) || idgham_ghunna.has(nxt))) {
                out[i] = "n_g";
            } else if (sym === "m" && nxt === "m") {
                out[i] = "m_g";
            }
        }

        for (let index = 0; index < out.length; index++) {
            rules.push(new RuleHit(index, out[index], "huroof_muqattaat", token));
        }
        return [out, rules];
    }

    private _try_allah(clusters: ArabicChar[], state: State, token: string): [string[], RuleHit[]] | null {
        const skeleton = this._skeleton(clusters);
        if (skeleton === "الله" || skeleton === "ٱلله") {
            const out: string[] = [];
            const rules: RuleHit[] = [];
            let lam: string;
            if (state.at_utterance_start) {
                this._emit(out, rules, "'", "alif_wasla_initial", token);
                this._emit(out, rules, "a", "allah_initial_vowel", token);
                lam = "L";
            } else {
                lam = this._allah_lam_symbol(state.previous_vowel);
            }
            this._emit_allah_core(clusters, lam, token, out, rules);
            return [out, rules];
        }

        if (skeleton === "لله") {
            const out: string[] = [];
            const rules: RuleHit[] = [];
            const prefix = clusters[0];
            this._emit(out, rules, "l", "li_prefix", token);
            this._emit_short_vowel(prefix.marks, token, out, rules);
            this._emit_allah_core(clusters.slice(1), "l", token, out, rules);
            return [out, rules];
        }

        return null;
    }

    private _allah_lam_symbol(previous_vowel: string | null): string {
        if (previous_vowel && new Set(["a", "aa", "aa4", "aa6", "u", "uu", "uu4", "uu6"]).has(previous_vowel)) {
            return "L";
        }
        return "l";
    }

    private _emit_allah_core(
        clusters: ArabicChar[],
        lam_symbol: string,
        token: string,
        out: string[],
        rules: RuleHit[]
    ): void {
        this._emit(out, rules, lam_symbol, "lam_allah", token);
        this._emit(out, rules, lam_symbol, "lam_allah_shadda", token);
        this._emit(out, rules, "aa", "allah_madd", token);
        this._emit(out, rules, "h", "letter", token);

        const final_marks = clusters.length > 0 ? clusters[clusters.length - 1].marks : [];
        this._emit_short_vowel(final_marks, token, out, rules);
    }

    private _article_start(clusters: ArabicChar[]): number | null {
        if (clusters.length >= 2 && new Set([ALEF_WASLA, ALEF]).has(clusters[0].base) && clusters[1].base === "ل") {
            return 0;
        }
        return null;
    }

    private _prefixed_article_start(clusters: ArabicChar[]): number | null {
        if (clusters.length >= 3 && new Set(["و", "ف", "ب", "ك"]).has(clusters[0].base) && new Set([ALEF_WASLA, ALEF]).has(clusters[1].base) && clusters[2].base === "ل") {
            return 1;
        }
        return null;
    }

    private _prefixed_wasla_start(clusters: ArabicChar[]): number | null {
        if (clusters.length >= 2 && new Set(["و", "ف", "ب", "ك"]).has(clusters[0].base) && clusters[1].base === ALEF_WASLA) {
            return 1;
        }
        return null;
    }

    private _prefixed_dropped_article_start(clusters: ArabicChar[]): number | null {
        if (clusters.length >= 3 && clusters[0].base === "ل" && this._has_vowel(clusters[0].marks) && clusters[1].base === "ل" && !this._has_vowel(clusters[1].marks) && !clusters[1].marks.includes(SHADDA)) {
            return 1;
        }
        return null;
    }

    private _emit_article(
        clusters: ArabicChar[],
        start: number,
        state: State,
        token: string,
        out: string[],
        rules: RuleHit[]
    ): number {
        const next_index = start + 2;
        if (next_index >= clusters.length) {
            return next_index;
        }

        if (state.at_utterance_start) {
            this._emit(out, rules, "'", "alif_wasla_initial", token);
            this._emit(out, rules, "a", "alif_wasla_initial_vowel", token);
        }

        const article_lam = clusters[start + 1];
        if (article_lam.marks.includes(SHADDA)) {
            this._emit(out, rules, "l", "article_lam_shadda", token);
            this._emit(out, rules, "l", "article_lam_shadda", token);
            this._emit_short_vowel(article_lam.marks, token, out, rules);
            return next_index;
        }

        if (next_index + 1 < clusters.length && clusters[next_index].base === "ل" && clusters[next_index].marks.includes(SHADDA) && clusters[next_index].marks.includes(FATHA) && clusters[next_index + 1].base === "ه") {
            const lam_sym = this._allah_lam_symbol(this._last_vowel(out) || state.previous_vowel);
            rules.push(new RuleHit(out.length, "", "lam_shamsiyya_elided", token));
            this._emit_allah_core(clusters.slice(next_index), lam_sym, token, out, rules);
            return next_index + 2;
        }

        const next_base = clusters[next_index].base;
        if (!SUN_LETTERS.has(next_base)) {
            this._emit(out, rules, "l", "lam_qamariyya", token);
        } else {
            rules.push(new RuleHit(out.length, "", "lam_shamsiyya_elided", token));
        }

        if (this._has_vowel(article_lam.marks)) {
            this._emit_short_vowel(article_lam.marks, token, out, rules);
        }
        return next_index;
    }

    private _emit_bare_article_lam(
        clusters: ArabicChar[],
        article_idx: number,
        token: string,
        out: string[],
        rules: RuleHit[]
    ): number {
        const next_index = article_idx + 1;
        if (next_index >= clusters.length) {
            return next_index;
        }

        if (next_index + 1 < clusters.length && clusters[next_index].base === "ل" && clusters[next_index].marks.includes(SHADDA) && clusters[next_index].marks.includes(FATHA) && clusters[next_index + 1].base === "ه") {
            const lam_sym = this._allah_lam_symbol(this._last_vowel(out));
            rules.push(new RuleHit(out.length, "", "lam_shamsiyya_elided", token));
            this._emit_allah_core(clusters.slice(next_index), lam_sym, token, out, rules);
            return next_index + 2;
        }

        const article_lam = clusters[article_idx];
        const next_base = clusters[next_index].base;
        if (!SUN_LETTERS.has(next_base)) {
            this._emit(out, rules, "l", "lam_qamariyya", token);
        } else {
            rules.push(new RuleHit(out.length, "", "lam_shamsiyya_elided", token));
        }

        if (this._has_vowel(article_lam.marks)) {
            this._emit_short_vowel(article_lam.marks, token, out, rules);
        }
        return next_index;
    }

    private _emit_initial_wasla(
        clusters: ArabicChar[],
        state: State,
        token: string,
        out: string[],
        rules: RuleHit[]
    ): number {
        if (state.at_utterance_start) {
            this._emit(out, rules, "'", "alif_wasla_initial", token);
            this._emit(out, rules, this._guess_wasla_vowel(clusters), "alif_wasla_initial_vowel", token);
        }
        return 1;
    }

    private _guess_wasla_vowel(clusters: ArabicChar[]): string {
        for (const cluster of clusters.slice(1, 4)) {
            if (cluster.marks.includes(DAMMA)) {
                return "u";
            }
        }
        return "i";
    }

    private _emit_cluster(
        clusters: ArabicChar[],
        index: number,
        token: string,
        out: string[],
        rules: RuleHit[]
    ): number {
        const cluster = clusters[index];
        const base = cluster.base;

        if (base === ALEF_WASLA && index >= 1) {
            if (index + 1 < clusters.length && clusters[index + 1].base === "ل") {
                const local_state = new State(false);
                local_state.previous_vowel = this._last_vowel(out);
                return this._emit_article(clusters, index, local_state, token, out, rules);
            }
            return index + 1;
        }

        if (base === "ل" && index >= 1 && !this._has_vowel(cluster.marks) && !cluster.marks.includes(SHADDA) && clusters[index - 1]!.base === "ل" && this._has_vowel(clusters[index - 1].marks)) {
            return this._emit_bare_article_lam(clusters, index, token, out, rules);
        }

        if (index >= 1 && cluster.marks.length === 0 && index + 1 < clusters.length && clusters[index + 1].marks.includes(SHADDA) && this._is_idgham_pair(base, clusters[index + 1].base)) {
            rules.push(new RuleHit(out.length, "", "idgham_within_word", token));
            return index + 1;
        }

        if (base === ALEF_MADDA) {
            const next_cluster = index + 1 < clusters.length ? clusters[index + 1] : null;
            const is_farq = next_cluster !== null && next_cluster.base === "ل" && !this._has_vowel(next_cluster.marks) && !next_cluster.marks.includes(SHADDA) && index + 2 < clusters.length && clusters[index + 2].marks.includes(SHADDA);
            const is_lazim_mukhaffaf = !is_farq && next_cluster !== null && next_cluster.base === "ل" && next_cluster.marks.includes(SUKUN);
            
            let madd_sym: string;
            let madd_rule: string;

            if (is_farq) {
                madd_sym = "aa6"; madd_rule = "madd_farq";
            } else if (is_lazim_mukhaffaf) {
                madd_sym = "aa6"; madd_rule = "madd_lazim_kalimi_mukhaffaf";
            } else if (next_cluster && next_cluster.marks.includes(SHADDA)) {
                madd_sym = "aa6"; madd_rule = "madd_lazim";
            } else if (next_cluster && HAMZA_LETTERS.has(next_cluster.base)) {
                madd_sym = "aa4"; madd_rule = "madd_muttasil";
            } else if (index === 0) {
                madd_sym = "aa"; madd_rule = "madd_badl";
            } else {
                madd_sym = "aa"; madd_rule = "madd_tabii";
            }

            if (index === 0) {
                this._emit(out, rules, "'", "hamza", token);
                this._emit(out, rules, madd_sym, madd_rule, token);
            } else {
                this._upgrade_previous_vowel(out, rules, madd_sym, madd_rule, token, true);
            }

            if (is_farq) {
                return this._emit_bare_article_lam(clusters, index + 1, token, out, rules);
            }
            return index + 1;
        }

        if (base === "و" && cluster.marks.includes(DAGGER_ALEF) && !this._has_vowel(cluster.marks)) {
            this._upgrade_previous_vowel(out, rules, "aa", "waw_dagger_alef_carrier", token);
            return index + 1;
        }

        if (this._is_long_vowel_carrier(clusters, index)) {
            return index + 1;
        }

        const symbol = this._symbol_for_cluster(cluster);
        if (symbol === null) {
            return index + 1;
        }

        if (symbol === "n" && this._is_sakin_like(cluster.marks)) {
            this._emit(out, rules, "n", "noon_sakin", token);
            if (this._has_hamza_mark(cluster.marks)) {
                return this._emit_trailing_hamza(clusters, index, token, out, rules);
            }
            return index + 1;
        }

        if (symbol === "m" && this._is_sakin_like(cluster.marks)) {
            this._emit(out, rules, "m", "mim_sakin", token);
            if (this._has_hamza_mark(cluster.marks)) {
                return this._emit_trailing_hamza(clusters, index, token, out, rules);
            }
            return index + 1;
        }

        if (cluster.marks.includes(SUKUN) && QALQALAH.has(symbol)) {
            this._emit(out, rules, `${symbol}_qal`, "qalqalah", token);
            return index + 1;
        }

        if (cluster.marks.includes(SHADDA)) {
            this._emit(out, rules, symbol, "shadda", token);
            this._emit(out, rules, symbol, "shadda", token);
        } else {
            this._emit(out, rules, symbol, "letter", token);
        }

        if (this._has_hamza_mark(cluster.marks)) {
            return this._emit_carrier_hamza(clusters, index, token, out, rules);
        }

        return this._emit_vowel_and_madd(clusters, index, token, out, rules);
    }

    private _symbol_for_cluster(cluster: ArabicChar): string | null {
        if (cluster.base === "ة") {
            return this.config.wasl ? "t" : "h";
        }
        if (cluster.base === ALEF_MAQSURA) {
            if (cluster.marks.includes(SUKUN) || cluster.marks.includes(SHADDA) || this._has_vowel(cluster.marks)) {
                return "y";
            }
            return null;
        }
        return LETTER_TO_SYMBOL[cluster.base] || null;
    }

    private _is_long_vowel_carrier(clusters: ArabicChar[], index: number): boolean {
        if (index === 0) return false;
        const base = clusters[index].base;
        const marks = clusters[index].marks;

        if (base === ALEF && !this._has_hamza_mark(marks)) return true;
        if (base === ALEF_MAQSURA && !marks.includes(SUKUN) && this._is_plain_madd_letter(clusters[index]) && !marks.includes(MADDAH)) return true;

        const previous_marks = clusters[index - 1].marks;
        if (base === "و" && previous_marks.includes(DAMMA) && this._is_plain_madd_letter(clusters[index])) return true;
        if (base === "ي" && previous_marks.includes(KASRA) && this._is_plain_madd_letter(clusters[index])) return true;

        return false;
    }

    private _emit_vowel_and_madd(
        clusters: ArabicChar[],
        index: number,
        token: string,
        out: string[],
        rules: RuleHit[]
    ): number {
        const cluster = clusters[index];
        const marks = cluster.marks;
        const next_cluster = index + 1 < clusters.length ? clusters[index + 1] : null;

        if (cluster.base === "ه" && marks.includes(SMALL_WAW)) {
            this._emit(out, rules, marks.includes(MADDAH) ? "uu4" : "uu", "madd_silah", token);
            return index + 1;
        }
        if (cluster.base === "ه" && marks.includes(SMALL_YA)) {
            this._emit(out, rules, marks.includes(MADDAH) ? "ii4" : "ii", "madd_silah", token);
            return index + 1;
        }

        if (marks.includes(FATHATAN)) {
            this._emit(out, rules, "a", "tanwin", token);
            this._emit(out, rules, "n", "tanwin_n", token);
            return index + 1;
        }
        if (marks.includes(DAMMATAN)) {
            this._emit(out, rules, "u", "tanwin", token);
            this._emit(out, rules, "n", "tanwin_n", token);
            return index + 1;
        }
        if (marks.includes(KASRATAN)) {
            this._emit(out, rules, "i", "tanwin", token);
            this._emit(out, rules, "n", "tanwin_n", token);
            return index + 1;
        }

        if (marks.includes(FATHA) && marks.includes(DAGGER_ALEF)) {
            if (marks.includes(MADDAH)) {
                this._emit(out, rules, "aa4", "small_alef_madd_muttasil", token);
            } else {
                this._emit(out, rules, "aa", "small_alef_madd_tabii", token);
            }
            return index + 1;
        }

        if (marks.includes(FATHA) && next_cluster !== null && (next_cluster.base === ALEF || (next_cluster.base === ALEF_MAQSURA && !next_cluster.marks.includes(SUKUN) && this._is_plain_madd_letter(next_cluster) && !next_cluster.marks.includes(MADDAH)))) {
            if (next_cluster.marks.includes(MADDAH)) {
                if (index + 2 < clusters.length && clusters[index + 2].marks.includes(SHADDA)) {
                    this._emit(out, rules, "aa6", "madd_lazim", token);
                } else if (index + 3 < clusters.length && clusters[index + 2].base === "ل" && !this._has_vowel(clusters[index + 2].marks) && !clusters[index + 2].marks.includes(SHADDA) && clusters[index + 3].marks.includes(SHADDA)) {
                    this._emit(out, rules, "aa6", "madd_farq", token);
                    return this._emit_bare_article_lam(clusters, index + 2, token, out, rules);
                } else if (index + 2 < clusters.length && clusters[index + 2].base === "ل" && clusters[index + 2].marks.includes(SUKUN)) {
                    this._emit(out, rules, "aa6", "madd_lazim_kalimi_mukhaffaf", token);
                } else {
                    this._emit(out, rules, "aa4", "madd_muttasil_or_munfasil", token);
                }
            } else {
                this._emit(out, rules, "aa", "madd_tabii", token);
            }
            return index + 2;
        }

        if (marks.includes(KASRA) && next_cluster !== null && new Set(["ي", ALEF_MAQSURA]).has(next_cluster.base) && this._is_plain_madd_letter(next_cluster)) {
            if (next_cluster.marks.includes(MADDAH)) {
                this._emit(out, rules, "ii4", "madd_munfasil_or_silah", token);
            } else {
                this._emit(out, rules, "ii", "madd_tabii", token);
            }
            return index + 2;
        }

        if (marks.includes(DAMMA) && next_cluster !== null && next_cluster.base === "و" && this._is_plain_madd_letter(next_cluster)) {
            this._emit(out, rules, next_cluster.marks.includes(MADDAH) ? "uu4" : "uu", "madd_tabii", token);
            return index + 2;
        }

        this._emit_short_vowel(marks, token, out, rules);

        if (marks.includes(DAGGER_ALEF)) {
            this._emit(out, rules, "aa", "small_alef_madd_tabii", token);
        }

        return index + 1;
    }

    private _emit_carrier_hamza(
        clusters: ArabicChar[],
        index: number,
        token: string,
        out: string[],
        rules: RuleHit[]
    ): number {
        const cluster = clusters[index];
        const marks = cluster.marks;
        const next_cluster = index + 1 < clusters.length ? clusters[index + 1] : null;

        let consonant_harakat: string | null = null;
        let hamza_harakat: string | null = null;
        let hamza_tanwin: string | null = null;
        let hamza_sakin = false;
        let seen_first = false;

        for (const m of marks) {
            if (m === HAMZA_ABOVE || m === HAMZA_BELOW || m === SHADDA) continue;
            if (!seen_first) {
                consonant_harakat = m;
                seen_first = true;
            } else {
                if (m === SUKUN) {
                    hamza_sakin = true;
                } else if (m === FATHA || m === KASRA || m === DAMMA) {
                    hamza_harakat = m;
                } else if (m === FATHATAN || m === DAMMATAN || m === KASRATAN) {
                    hamza_tanwin = m;
                }
            }
        }

        if (seen_first && consonant_harakat === SUKUN && hamza_harakat === null && !hamza_sakin && hamza_tanwin === null) {
            consonant_harakat = null;
            hamza_sakin = true;
        }

        if (seen_first && hamza_harakat === null && !hamza_sakin && hamza_tanwin === null && (consonant_harakat === FATHA || consonant_harakat === KASRA || consonant_harakat === DAMMA)) {
            hamza_harakat = consonant_harakat;
            consonant_harakat = null;
        }

        if (consonant_harakat === FATHA) this._emit(out, rules, "a", "pre_hamza_vowel", token);
        else if (consonant_harakat === KASRA) this._emit(out, rules, "i", "pre_hamza_vowel", token);
        else if (consonant_harakat === DAMMA) this._emit(out, rules, "u", "pre_hamza_vowel", token);

        this._emit(out, rules, "'", "hamza_mark", token);

        if (hamza_sakin) return index + 1;

        if (hamza_harakat === DAMMA && next_cluster !== null && next_cluster.base === "و" && this._is_plain_madd_letter(next_cluster)) {
            this._emit(out, rules, next_cluster.marks.includes(MADDAH) ? "uu4" : "uu", "madd_tabii", token);
            return index + 2;
        }
        if (hamza_harakat === KASRA && next_cluster !== null && new Set(["ي", ALEF_MAQSURA]).has(next_cluster.base) && this._is_plain_madd_letter(next_cluster)) {
            this._emit(out, rules, next_cluster.marks.includes(MADDAH) ? "ii4" : "ii", "madd_tabii", token);
            return index + 2;
        }
        if (hamza_harakat === FATHA && next_cluster !== null && new Set([ALEF, ALEF_MAQSURA]).has(next_cluster.base)) {
            this._emit(out, rules, next_cluster.marks.includes(MADDAH) ? "aa4" : "aa", "madd_tabii", token);
            return index + 2;
        }

        if (hamza_harakat === DAMMA) this._emit(out, rules, "u", "hamza_vowel", token);
        else if (hamza_harakat === KASRA) this._emit(out, rules, "i", "hamza_vowel", token);
        else if (hamza_harakat === FATHA) this._emit(out, rules, "a", "hamza_vowel", token);

        if (hamza_tanwin === FATHATAN) {
            this._emit(out, rules, "a", "tanwin", token);
            this._emit(out, rules, "n", "tanwin_n", token);
        } else if (hamza_tanwin === DAMMATAN) {
            this._emit(out, rules, "u", "tanwin", token);
            this._emit(out, rules, "n", "tanwin_n", token);
        } else if (hamza_tanwin === KASRATAN) {
            this._emit(out, rules, "i", "tanwin", token);
            this._emit(out, rules, "n", "tanwin_n", token);
        }

        return index + 1;
    }

    private _emit_short_vowel(marks: readonly string[], token: string, out: string[], rules: RuleHit[]): void {
        if (marks.includes(FATHA)) this._emit(out, rules, "a", "vowel", token);
        else if (marks.includes(KASRA) || marks.includes(SMALL_KASRA)) this._emit(out, rules, "i", "vowel", token);
        else if (marks.includes(DAMMA)) this._emit(out, rules, "u", "vowel", token);
    }

    private _has_vowel(marks: readonly string[]): boolean {
        for (const m of marks) {
            if (m === FATHA || m === DAMMA || m === KASRA || m === FATHATAN || m === DAMMATAN || m === KASRATAN || m === SMALL_KASRA) return true;
        }
        return false;
    }

    private _is_plain_madd_letter(cluster: ArabicChar): boolean {
        return !this._has_vowel(cluster.marks) && !cluster.marks.includes(SHADDA);
    }

    private _is_sakin_like(marks: readonly string[]): boolean {
        return marks.includes(SUKUN) || (!this._has_vowel(marks) && !marks.includes(SHADDA));
    }

    private _has_hamza_mark(marks: readonly string[]): boolean {
        return marks.includes(HAMZA_ABOVE) || marks.includes(HAMZA_BELOW);
    }

    private _emit_trailing_hamza(
        clusters: ArabicChar[],
        index: number,
        token: string,
        out: string[],
        rules: RuleHit[]
    ): number {
        const marks = clusters[index].marks;
        this._emit(out, rules, "'", "hamza_mark", token);
        for (const m of marks) {
            if (m === FATHA || m === KASRA || m === DAMMA) {
                const vowel_map: Record<string, string> = { [FATHA]: "a", [KASRA]: "i", [DAMMA]: "u" };
                this._emit(out, rules, vowel_map[m], "hamza_vowel", token);
                break;
            }
        }
        return index + 1;
    }

    private _is_idgham_pair(first: string, second: string): boolean {
        if (first === ALEF || first === "و" || first === "ي") return false;
        if (first === second) return true;
        return IDGHAM_HOMORGANIC_PAIRS.has(`${first},${second}`);
    }

    private _apply_iltiqa_sakinayn(symbols: string[], rules: RuleHit[], next_token: string): void {
        if (!this.config.wasl || !this._starts_with_wasla(next_token)) return;

        const index = this._last_nonempty_symbol_index(symbols);
        if (index === null) return;

        const replacementMap: Record<string, string> = {
            "aa": "a", "aa4": "a", "aa6": "a",
            "ii": "i", "ii4": "i", "ii6": "i",
            "uu": "u", "uu4": "u", "uu6": "u"
        };
        const replacement = replacementMap[symbols[index]];
        if (!replacement) return;

        symbols[index] = replacement;
        rules.push(new RuleHit(index, replacement, "iltiqa_sakinayn_madd_drop", next_token));
    }

    private _starts_with_wasla(token: string): boolean {
        const clusters = this._cluster(token);
        return clusters.length > 0 && clusters[0].base === ALEF_WASLA;
    }

    private _starts_with_hamza(word_symbols: string[]): boolean {
        if (word_symbols.length === 0) return false;
        return word_symbols[0] === "'";
    }

    private _upgrade_silah_before_hamza(
        symbols: string[],
        rules: RuleHit[],
        word_symbols: string[],
        source: string
    ): void {
        if (!this._starts_with_hamza(word_symbols)) return;

        const index = this._last_nonempty_symbol_index(symbols);
        if (index === null) return;

        const upgrade_map: Record<string, string> = { "aa": "aa4", "uu": "uu4", "ii": "ii4" };
        const sym = symbols[index];
        if (!(sym in upgrade_map)) return;

        symbols[index] = upgrade_map[sym];
        const was_silah = rules.some(hit => hit.symbol_index === index && hit.rule === "madd_silah");
        const new_rule = was_silah ? "madd_silah_kubra" : "madd_munfasil";
        rules.push(new RuleHit(index, symbols[index], new_rule, source));
    }

    private _upgrade_previous_vowel(
        out: string[],
        rules: RuleHit[],
        symbol: string,
        rule: string,
        source: string,
        drop_preceding_hamza: boolean = false
    ): void {
        for (let index = out.length - 1; index >= 0; index--) {
            if (out[index] === "a") {
                out[index] = symbol;
                rules.push(new RuleHit(index, symbol, rule, source));
                if (drop_preceding_hamza && index > 0 && out[index - 1] === "'") {
                    out.splice(index - 1, 1);
                    const rules_to_drop = rules.filter(r => r.symbol_index === index - 1 && r.symbol === "'");
                    for (const r of rules_to_drop) {
                        const r_idx = rules.indexOf(r);
                        if (r_idx > -1) rules.splice(r_idx, 1);
                    }
                    for (let i=0; i<rules.length; i++) {
                        if(rules[i].symbol_index >= index - 1) {
                            rules[i] = new RuleHit(rules[i].symbol_index - 1, rules[i].symbol, rules[i].rule, rules[i].source);
                        }
                    }
                }
                return;
            }
            if (!VOWELS.has(out[index])) break;
        }
        this._emit(out, rules, symbol, rule, source);
    }

    private _emit(out: string[], rules: RuleHit[], symbol: string, rule: string, source: string): void {
        out.push(symbol);
        rules.push(new RuleHit(out.length - 1, symbol, rule, source));
    }

    private _first_consonant(symbols: string[]): string | null {
        for (const symbol of symbols) {
            if (symbol && !VOWELS.has(symbol) && symbol !== "PAUSE") {
                return symbol.replace("_qal", "");
            }
        }
        return null;
    }

    private _last_vowel(symbols: string[]): string | null {
        for (let i = symbols.length - 1; i >= 0; i--) {
            const symbol = symbols[i];
            if (VOWELS.has(symbol)) return symbol;
        }
        return null;
    }

    private _pending_noon_index_from_rules(rules: RuleHit[], symbols: string[], start: number, end: number): number | null {
        for (let i = rules.length - 1; i >= 0; i--) {
            const hit = rules[i];
            if (hit.symbol_index < start) break;
            if (hit.symbol_index >= start && hit.symbol_index < end && (hit.rule === "tanwin_n" || hit.rule === "noon_sakin") && symbols[hit.symbol_index] === "n") {
                return hit.symbol_index;
            }
        }
        return null;
    }

    private _pending_mim_index_from_rules(rules: RuleHit[], symbols: string[], start: number, end: number): number | null {
        for (let i = rules.length - 1; i >= 0; i--) {
            const hit = rules[i];
            if (hit.symbol_index < start) break;
            if (hit.symbol_index >= start && hit.symbol_index < end && hit.rule === "mim_sakin" && symbols[hit.symbol_index] === "m") {
                return hit.symbol_index;
            }
        }
        return null;
    }

    private _resolve_noon_within_word(symbols: string[], rules: RuleHit[], source: string): void {
        const current_rules = [...rules];
        for (const hit of current_rules) {
            if ((hit.rule !== "tanwin_n" && hit.rule !== "noon_sakin") || symbols[hit.symbol_index] !== "n") {
                continue;
            }
            const next_consonant = this._next_consonant(symbols, hit.symbol_index + 1);
            if (next_consonant !== null) {
                this._apply_noon_assimilation(hit.symbol_index, next_consonant, symbols, rules, source);
            }
        }
    }

    private _resolve_pending_noon(state: State, next_consonant: string | null, symbols: string[], rules: RuleHit[], source: string): void {
        const pending = state.pending_noon_index;
        state.pending_noon_index = null;
        if (pending === null || next_consonant === null) return;

        this._apply_noon_assimilation(pending, next_consonant, symbols, rules, source);
    }

    private _apply_noon_assimilation(pending: number, next_consonant: string, symbols: string[], rules: RuleHit[], source: string): void {
        if (next_consonant === "b") {
            symbols[pending] = "m_g";
            rules.push(new RuleHit(pending, "m_g", "iqlab", source));
        } else if (next_consonant === "m") {
            symbols[pending] = "m_g";
            rules.push(new RuleHit(pending, "m_g", "idgham_ghunna", source));
        } else if (this._idgham_ghunna.has(next_consonant)) {
            symbols[pending] = "n_g";
            rules.push(new RuleHit(pending, "n_g", "idgham_ghunna", source));
        } else if (this._idgham_no_ghunna.has(next_consonant)) {
            symbols[pending] = "";
            rules.push(new RuleHit(pending, "", "idgham_no_ghunna", source));
        } else if (this._ikhfa.has(next_consonant)) {
            symbols[pending] = "n_g";
            rules.push(new RuleHit(pending, "n_g", "ikhfa", source));
        } else if (this._izhar.has(next_consonant)) {
            rules.push(new RuleHit(pending, "n", "izhar", source));
        }
    }

    private _resolve_pending_mim(state: State, word_symbols: string[], word_rules: RuleHit[], symbols: string[], rules: RuleHit[], source: string): void {
        const pending = state.pending_mim_index;
        state.pending_mim_index = null;
        if (pending === null || this._first_consonant(word_symbols) !== "m") return;

        symbols[pending] = "m_g";
        rules.push(new RuleHit(pending, "m_g", "idgham_shafawi", source));
        if (word_symbols.length >= 2 && word_symbols[0] === "m" && word_symbols[1] === "m") {
            word_symbols.shift();
            const shifted: RuleHit[] = [];
            let skipped = false;
            for (const hit of word_rules) {
                if (!skipped && hit.symbol_index === 0 && hit.symbol === "m") {
                    skipped = true;
                    continue;
                }
                const new_index = hit.symbol_index > 0 ? hit.symbol_index - 1 : hit.symbol_index;
                shifted.push(new RuleHit(new_index, hit.symbol, hit.rule, hit.source));
            }
            word_rules.length = 0;
            word_rules.push(...shifted);
        }
    }

    private _coalesce_leading_geminate_after(symbols: string[], word_symbols: string[], word_rules: RuleHit[], previous_symbol: string, leading_symbol: string): void {
        let previous: string | null = null;
        for (let i = symbols.length - 1; i >= 0; i--) {
            const s = symbols[i];
            if (!s || s === "PAUSE") continue;
            previous = s;
            break;
        }
        if (previous !== previous_symbol) return;
        if (word_symbols.length < 2 || word_symbols[0] !== leading_symbol || word_symbols[1] !== leading_symbol) return;

        word_symbols.shift();
        const shifted: RuleHit[] = [];
        let skipped = false;
        for (const hit of word_rules) {
            if (!skipped && hit.symbol_index === 0 && hit.symbol === leading_symbol) {
                skipped = true;
                continue;
            }
            const new_index = hit.symbol_index > 0 ? hit.symbol_index - 1 : hit.symbol_index;
            shifted.push(new RuleHit(new_index, hit.symbol, hit.rule, hit.source));
        }
        word_rules.length = 0;
        word_rules.push(...shifted);
    }

    private _last_nonempty_symbol_index(symbols: string[]): number | null {
        for (let index = symbols.length - 1; index >= 0; index--) {
            if (symbols[index]) return index;
        }
        return null;
    }

    private _next_consonant(symbols: string[], start: number): string | null {
        for (let i = start; i < symbols.length; i++) {
            const symbol = symbols[i];
            if (symbol && !VOWELS.has(symbol) && symbol !== "PAUSE") {
                return symbol.replace("_qal", "");
            }
        }
        return null;
    }

    private _apply_waqf_transformations(symbols: string[], rules: RuleHit[], word_span: WordSpan, source: string): void {
        if (word_span.end <= word_span.start) return;

        const word_symbols = symbols.slice(word_span.start, word_span.end);
        if (word_symbols.length === 0) return;

        let last_idx = word_symbols.length - 1;
        if (last_idx >= 1 && word_symbols[last_idx] === "n" && (word_symbols[last_idx - 1] === "a" || word_symbols[last_idx - 1] === "i" || word_symbols[last_idx - 1] === "u")) {
            word_symbols[last_idx] = "";
            word_symbols[last_idx - 1] = "";
        }

        let non_empty_last_idx = this._last_nonempty_symbol_index(word_symbols);
        if (non_empty_last_idx !== null && (word_symbols[non_empty_last_idx] === "a" || word_symbols[non_empty_last_idx] === "i" || word_symbols[non_empty_last_idx] === "u")) {
            word_symbols[non_empty_last_idx] = "";
        }

        if (this._is_taa_marbuta(word_span)) {
            for (let idx = word_symbols.length - 1; idx >= 0; idx--) {
                if (word_symbols[idx] === "t") {
                    word_symbols[idx] = "h";
                    rules.push(new RuleHit(word_span.start + idx, "h", "taa_marbuta_waqf", source));
                    break;
                }
            }
        }

        non_empty_last_idx = this._last_nonempty_symbol_index(word_symbols);
        if (non_empty_last_idx !== null && QALQALAH.has(word_symbols[non_empty_last_idx])) {
            word_symbols[non_empty_last_idx] = `${word_symbols[non_empty_last_idx]}_qal`;
            rules.push(new RuleHit(word_span.start + non_empty_last_idx, word_symbols[non_empty_last_idx], "qalqalah_kubra_waqf", source));
        }

        const madd_tabii = new Set(["aa", "ii", "uu"]);
        const madd_map: Record<string, string> = { "aa": "aa6", "ii": "ii6", "uu": "uu6" };
        non_empty_last_idx = this._last_nonempty_symbol_index(word_symbols);
        if (non_empty_last_idx !== null) {
            const last_sym = word_symbols[non_empty_last_idx];
            if (madd_tabii.has(last_sym)) {
                if (!this._is_dagger_alef_madd(word_span)) {
                    word_symbols[non_empty_last_idx] = madd_map[last_sym];
                    rules.push(new RuleHit(word_span.start + non_empty_last_idx, word_symbols[non_empty_last_idx], "madd_arid_lis_sukun_waqf", source));
                }
            } else if (last_sym !== "a" && last_sym !== "i" && last_sym !== "u" && last_sym !== "") {
                let prev_idx = non_empty_last_idx - 1;
                while (prev_idx >= 0 && !word_symbols[prev_idx]) {
                    prev_idx--;
                }
                if (prev_idx >= 0 && madd_tabii.has(word_symbols[prev_idx])) {
                    word_symbols[prev_idx] = madd_map[word_symbols[prev_idx]];
                    rules.push(new RuleHit(word_span.start + prev_idx, word_symbols[prev_idx], "madd_arid_lis_sukun_waqf", source));
                }
            }
        }

        for(let i=0; i<word_symbols.length; i++) {
            symbols[word_span.start + i] = word_symbols[i];
        }
    }

    private _is_taa_marbuta(word_span: WordSpan): boolean {
        return word_span.token.includes("ة");
    }

    private _is_dagger_alef_madd(word_span: WordSpan): boolean {
        return word_span.token.includes(DAGGER_ALEF);
    }
}


