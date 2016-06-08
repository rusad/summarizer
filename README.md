summarizer
=========

    A python library for simple text summarization

Installation 
============

    git clone https://github.com/rusad/summarizer.git
    cd summarizer
    python setup.py install

Usage example
========

    Usage from console:

        python summarize.py <text or URL> , <sentences number>
        python summarize.py http://www.bloomberg.com/view/articles/2016-06-06/putin-devotes-oil-windfall-to-guns-not-butter 3 
        
    Usage from code:

        import summarizer
        summarizer.summarize(<text or URL> , <sentences number>)
        summarizer.summarize('http://www.bloomberg.com/view/articles/2016-06-06/putin-devotes-oil-windfall-to-guns-not-butter',3)
