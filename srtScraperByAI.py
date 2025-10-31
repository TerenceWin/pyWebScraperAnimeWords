import pysrt
from sudachipy import dictionary, tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer

# === Load common words (JLPT + frequency list) ===
def load_common_words(*files):
    common_words = set()
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip()
                    if word:
                        common_words.add(word)
        except FileNotFoundError:
            print(f"⚠️ Skipped missing file: {path}")
    return common_words


common_words = load_common_words("jp_common_words.txt", "jlpt_common_words.txt")

# === Set up Sudachi tokenizer ===
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C  # detailed mode for best accuracy

# === Read subtitle file ===
subs = pysrt.open("example.srt")
lines = [sub.text.replace("\n", " ") for sub in subs if sub.text.strip()]

# === Tokenize subtitles ===
def tokenize_texts(lines):
    tokenized_lines = []
    all_tokens = []
    for text in lines:
        words = []
        for m in tokenizer_obj.tokenize(text, mode):
            base = m.dictionary_form()
            pos = m.part_of_speech()[0]
            # Only keep content words
            if pos in ["名詞", "動詞", "形容詞"] and len(base) > 1:
                # Exclude common words and numerics
                if base not in common_words and not base.isdigit():
                    words.append(base)
                    all_tokens.append(base)
        tokenized_lines.append(" ".join(words))
    return tokenized_lines, all_tokens

tokenized_lines, all_tokens = tokenize_texts(lines)
print(f"✅ Total tokens: {len(all_tokens)}")

# === TF-IDF scoring to find distinct anime terms ===
vectorizer = TfidfVectorizer(token_pattern=None, tokenizer=lambda x: x.split())
tfidf_matrix = vectorizer.fit_transform(tokenized_lines)
scores = tfidf_matrix.sum(axis=0).A1
vocab = vectorizer.get_feature_names_out()

# Pair word with TF-IDF score
tfidf_scores = sorted(zip(vocab, scores), key=lambda x: x[1], reverse=True)

# === Filter top 15% most distinctive words ===
cutoff = int(len(tfidf_scores) * 0.15)
anime_words = dict(tfidf_scores[:cutoff])

# === Optional: filter kana-only trivial words ===
hiragana_chars = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんゃゅょっゎゐゑゔーッ"
kana_whitelist = {"かわいい", "すごい", "やばい", "うそ", "きゃー", "まじ", "ほんと"}

filtered_words = {
    w: s for w, s in anime_words.items()
    if not (all(ch in hiragana_chars for ch in w) and w not in kana_whitelist)
}

# === Print results ===
print(f"\n🎯 Extracted {len(filtered_words)} high-accuracy anime terms:\n")
for word, score in list(filtered_words.items())[:100]:  # top 100
    print(f"{word}\t{score:.4f}")

# === Save to file ===
with open("anime_terms.txt", "w", encoding="utf-8") as f:
    for word in filtered_words:
        f.write(word + "\n")

print("\n✅ Saved to anime_terms.txt")
