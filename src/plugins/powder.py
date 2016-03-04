from app import bot, config
import os.path
import random

adjectives = None
conjunctions = None
nouns = None
RARITY_LOOKUP = [0, 0, 0, 0, 1, 1, 1, 2, 2, 3]
BINARY = [True, False]


def load_file(name):
    current_set = []
    words = [current_set]

    filename = os.path.join(config["powder"]["folder"], name)
    with open(filename, "r") as word_file:
        for word in word_file:
            word = word.strip(" \n")
            if len(word):
                current_set.append(word)
            else:
                current_set = []
                words.append(current_set)

    return words


def rarity_switch(word_set):
    i = random.choice(range(10))
    return get_word(word_set, RARITY_LOOKUP[i])


def get_word(word_set, rarity_level):
    if len(word_set[rarity_level]):
        return random.choice(word_set[rarity_level])
    else:
        return ""


@bot.setup
def load_words():
    global adjectives, conjunctions, nouns

    adjectives = load_file("adjectives.txt")
    conjunctions = load_file("conjunctions.txt")
    nouns = load_file("nouns.txt")


@bot.listen("@me: powder", channel="#smash-chicago")
def generate(channel):
    protein = []
    if random.choice(BINARY):
        protein.append(rarity_switch(adjectives))

    protein.append(rarity_switch(nouns))

    if random.choice(BINARY) and not protein[-1][0].isupper():
        protein.append(rarity_switch(conjunctions))

    protein.append(rarity_switch(nouns))
    protein.append("protein powder")

    protein[0] = protein[0].capitalize()

    bot.post(channel, text=" ".join(protein))
