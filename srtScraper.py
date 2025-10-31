import pysrt
from sudachipy import dictionary, tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer

#Reading common word files
jpCommonWordsFile = open("jp_common_words.txt", "r", encoding="utf-8")
line = jpCommonWordsFile.readline()
lineNum = 1
jpDict = set()

while line:
    jpDict.add(line.strip())
    lineNum += 1
    line = jpCommonWordsFile.readline()

#Reading jlpt common word files
jlptFile = open("jlpt_common_words.txt", "r", encoding="utf-8")
line = jlptFile.readline()

while line:
    jpDict.add(line.strip())
    lineNum+=1
    line = jlptFile.readline()

jpPunctuation = [
    "。", "、", "・", "「", "」",
    "『", "』", "（", "）", "［", "(", ")", "］", "｛", "｝",
    "【", "】", "〈", "〉", "《", "》", "〝", "〟", "〜", "ー",
    "…", "‥", "：", "；", "？", "！", "／", "＼", "｜", "＿",
    "＠", "＃", "＊", "＋", "－", "＝", "＜", "＞", "％", "＆",
    "＄", "＾", "｀", "〆", "々", "〃", "〄", "゛", "゜", "‐",
    "―", "─", "○", "×", "△", "□", "◇", "･", "“", "”", "’",
    "‘", "‾", "～"
]

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C

subs = pysrt.open('example.srt')
lines = [sub.text.replace("\n", " ") for sub in subs if sub.text.strip()]

allWords = []
animeWords = []

#Reading srt files, using token to divide each text lines to Japanese words and append to animeWords
for l in lines:
    tokens = tokenizer_obj.tokenize(l, mode)
    for token in tokens:
        word = token.dictionary_form()
        allWords.append(word)
        if word not in jpDict and word[0] not in jpPunctuation and len(word) > 1 and not word.isdigit():
            # Exclude common words that are in dict, punctuations, 1 word character, digital String
            animeWords.append(word)

#Exclude common words that are in dict, punctuations, 1 word character, digital String

#Created an animeDict to indicates occurance of each words
frequentWords = {}
for word in animeWords:
    if word in frequentWords:
        frequentWords[word] += 1
    else:
        frequentWords[word] = 1

#Getting rid of words that occurred only once
newDict = {word: count for word, count in frequentWords.items() if count > 1}

#We will get rid of all remaining words, example です、してる、ない、毛と、なに、まあ...
#い　と　る　す　あ　に
hiraganaChar = [
    "あ", "い", "う", "え", "お", "か", "き", "く",
    "け", "こ", "さ", "し", "す", "せ", "そ", "た",
    "ち", "つ", "て", "と", "な", "に", "ぬ", "ね",
    "の", "は", "ひ", "ふ", "へ", "ほ", "ま", "み",
    "む", "め", "も", "や", "ゆ", "よ", "ら", "り",
    "る", "れ", "ろ", "わ", "を", "ん", "が", "ぎ",
    "ぐ", "げ", "ご", "ざ", "じ", "ず", "ぜ", "ぞ",
    "だ", "ぢ", "づ", "で", "ど", "ば", "び", "ぶ",
    "べ", "ぼ", "ぱ", "ぴ", "ぷ", "ぺ", "ぽ", "ゃ",
    "ゅ", "ょ", "っ", "ゎ", "ゐ", "ゑ", "ゔ", "ー", "ッ"
]

for key in list(newDict.keys()):
    if str(key[len(key) - 1]) in hiraganaChar:
        del newDict[key]

#By now we are mostly left with kanji words and anime words
#Find the average occrance of all words and the kanji words with occurance less than average number
#will be deleted. Because these words aren't relevent if their occurance is less than average number.
totalWord = 0
for word in newDict:
    totalWord += newDict[word]
avgWord=round(totalWord/len(newDict))

print("Average word count: " + str(avgWord))
for key in list(newDict.keys()):
    if newDict[key] <= avgWord:
        del newDict[key]

print(newDict)
print(len(newDict))