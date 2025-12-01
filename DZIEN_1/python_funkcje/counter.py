#przykład 3
def word_count(text):
    words = text.lower().split()
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts

print(word_count("Hello world hello world hello world hello Python Python world of python hello everybody"))
