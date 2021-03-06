#!/usr/bin/env python

from string import punctuation
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from heapq import nlargest
from collections import defaultdict
import bs4, urllib2, sys

class Summarizer:
    
    def __init__(self, upper_bound=0.9, lower_bound=0.1):
        self._upper_bound = upper_bound
        self._lower_bound = lower_bound
        
    def getTokens(self, text):
        return [word.lower() for word in word_tokenize(text)]

    def detectLanguage(self, text):
        languages_scores = {}
        tokens = word_tokenize(text)
        words = [word.lower() for word in tokens]
        # Compute per language included in nltk number of unique stopwords
        # appearing in analyzed text
        for language in stopwords.fileids():
            stopwords_set = set(stopwords.words(language))
            words_set = set(words)
            common_elements = words_set.intersection(stopwords_set)
            languages_scores[language] = len(common_elements) # language "score"

        return max(languages_scores, key=languages_scores.get)

    def getFreq(self, text, normalize=True):
        stop_words = stopwords.words(self.detectLanguage(text))
        words = self.getTokens(text)
        clean_words = filter(lambda word: not word in stop_words and not word in punctuation, words)
        fdist = FreqDist(clean_words)
#==============================================================================
#         # same result        
#         fdist = FreqDist()
#         for word in word_tokenize(text):
#             word = word.lower()
#             if not word in stop_words and not word in punctuation:
#                 fdist[word] += 1
#==============================================================================
        # normalization by dividing on max freqency 
        if normalize:
            norm = float(max(fdist.values()))
            for word in fdist.keys():
                fdist[word] = fdist[word] / norm
                # remove too frequent and too rare words
                if fdist[word] >= self._upper_bound or fdist[word] <= self._lower_bound:
                    del fdist[word]
        return fdist

    def _rank(self, ranking, n=1):
        # return the first n sentences with highest ranking
        return nlargest(n, ranking, key=ranking.get)
    
    def summarize(self, text, n=1, **kwargs):
        sents = sent_tokenize(text)
        freq = self.getFreq(text, **kwargs)
        #assert n <= len(sents)
        word_sent = [self.getTokens(sent) for sent in sents]
        ranking = defaultdict(int)
    
        for i, sent in enumerate(word_sent):
            for word in sent:
                if word in freq:
                    ranking[i] += freq[word]
                    
        sents_idx = self._rank(ranking, n)
        output = [sents[j] for j in sents_idx]
        
        # reordering 
        output.sort(lambda s1, s2: text.find(s1) - text.find(s2))
        return output

    def getContent(self, src):
        # check is url    
        try:
            html = urllib2.urlopen(src).read().decode('utf8')
            raw = bs4.BeautifulSoup(html, 'html.parser')
        # 1st approach to find text content: get largest sequence of p tag, using
        # BeautifulSoup
            # cleaning body from script and style tags        
            if len(raw.select('script style')) > 0:
               for script in raw.body(["script", "style"]):
                    script.extract()
            # largest sequence of p tags    
            return max(raw.find_all(), key=lambda t: len(t.find_all('p', recursive=False))).get_text()
#==============================================================================
#         # 2nd approach to find text content: get text of parent block,which contain 
#         # the longest p tag, using BeautifulSoup                
#             # find longest p tag
#             longest_p = max(raw.find_all('p'), key=lambda x: len(x.get_text())) 
#             # get parent block of longest p tag
#             parent = longest_p.find_parent()
#             # trash extracting
#             if len(raw.select('script style')) > 0:
#                 for script in parent(["script", "style"]):
#                     script.extract()
#             return parent.get_text()        
#==============================================================================
#==============================================================================
#         # 3rd approach to find text content: get text of parent block,which contain 
#         # the longest p tag, using pattern.web
#             from pattern.web import URL, DOM, plaintext
#             # getting DOM
#             dom = DOM(URL(src).download(cached=True))        
#             # find longest p tag
#             longest_p = max(dom('p'), key=lambda x: len(plaintext(x.content)))
#             # get parent block of longest p tag
#             return plaintext(longest_p.parent.content)        
#==============================================================================
            
        except ValueError:
            return src
        
    def _sortByVal(self, d, reverse=False):
        items = [(v, k) for k, v in d.items()]
        items.sort()
        if reverse:
            items.reverse()
        return [(k, v) for v, k in items]
    
    def getKeyWords(self, text, top=15, **kwargs):
        freq = self.getFreq(text, **kwargs)
        key_words = self._sortByVal(freq, **kwargs)[-top:]
        words, scores = list(zip(*key_words))
        return words, scores
    
    def getDispersion(self, text, **kwargs):
        words, _ = self.getKeyWords(text, **kwargs)
        tokens = self.getTokens(text)
        n_tokens = len(tokens)
        n_words = len(words)
        disp = []
        for x in range(n_tokens):
            for y in range(n_words):
                if tokens[x] == words[y]:
                    disp.append((x,y))
        x, y = list(zip(*disp))
        return x, y
    
    def draw(self, words, scores, x, y):
        import matplotlib.pyplot as plt
        plt.style.use('ggplot')
        
        fig = plt.figure(figsize=(14,6))
        fig.subplots_adjust(wspace = 0.3)
        
        ax1 = fig.add_subplot(121)
        plt.yticks(range(len(words)), words)
        ax1.barh(range(len(scores)), scores, align='center', alpha=0.4)
        ax1.set_title('Key Words Frequency')    
        ax1.set_xlabel('Normalized frequency')    
        
        ax2 = fig.add_subplot(122, sharey=ax1)
        plt.yticks(range(len(words)), words)
        ax2.plot(x, y, "b|", scalex=.1, markersize=10)
        ax2.set_title('Lexical Dispersion Plot')
        ax2.set_xlabel("Word Offset")
        
        plt.savefig('key_words_fig.pdf', format='pdf')
        
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        summarizer = Summarizer()        
        src = summarizer.getContent(sys.argv[1])
        if len(sys.argv) > 2:
            print(summarizer.summarize(src, n=sys.argv[2]))
        else:
            print(summarizer.summarize(src))
        
        while True:
            is_drawing = raw_input("Want to draw key words dispersion plot?[y/n]:")
            if is_drawing == "y" or is_drawing == "Y":
                words, scores = summarizer.getKeyWords(src)
                x, y = summarizer.getDispersion(src)
                summarizer.draw(words, scores, x, y)
                break
            elif is_drawing == "n" or is_drawing == "N":
                break
            else:
                print("Incorrect command.")
        sys.exit(0)
    else:
        print('There is no text to summarize')
        sys.exit(1)