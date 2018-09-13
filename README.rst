Ibis
====
Ibis is a searchable, interactive, tag-based, and wiki-like personal note-taking system for history and news.


Design Goals
------------
This project was born out of my human inability to memorize the details of hundreds of news articles and books I read
every year. Text-based notes are good for high-level details, but can miss specifics and require you to be lucky with
keyword-based searches. Tag based note systems help solve this problem, but don't address overlapping information
between sources (and most lack a robust sourcing system). Wikis are better, and have the added usability of hyperlinks,
but facts and sources are often repeated across multiple articles, adding additional work to writing and making updates
a chore.

What I'd like to be able to do is this: While reading the news or a book, I can write down its claims as I go, tagging
relevant topics for each one, or adding my current reading on as an additional source to something I've heard before.
Ideally, this should take as little time as possible - I don't want reading to become a chore. Then I want to search
through these facts by topic, place, people involved, or dates they took place. I can summarize statements into an
article with an automatically generated list of sources.

With this in mind, these are the core design goals of Ibis:

* *DRY (Don't Repeat Yourself)* - Current systems require repetition in one form or another: either you have to reread
  through the notes on a source, pulling out information in the same order & context in which it was originally
  presented, or you have to rewrite the same facts & sources in every article that references them.
* *Usability in Note-taking* - If reading & taking notes becomes a chore, it just doesn't happen. Taking notes should be
  as effortless as possible to encourage you to actually use the system.
* *Searchability* - The value of notes is in being able to recall the information later. Without an effective recall
  mechanism, the notes might as well not exist.
* *Usability in composition* - Once you've found your notes, you should be able to easily compose them into
  human-readable articles, backed by the sources where this process all started.


Feature Goals
-------------
Based on the design goals, this is what I have planned for Ibis:

* *Fact-based knowledge* - To cut out repetition, Ibis is built on facts, which are singular, verifiable pieces of
  information tied to one or more sources, and tagged with relevant topics for later searchability
* *Rapid note-taking* - While the tagging system is powerful, it can also be tedious. Ibis relies on the typical linear
  progression of texts from one set of topics to the next to copy over tags and reduce time spent fiddling with the
  system so you can focus on reading.
* *Hierarchical tagging* - Facts often address very specific situations while building up to more generalized
  conclusions. Hierarchical tagging allows you to manage this by organizing facts into subtopics and only revealing
  specifics when you want to.
* *Key-Value Facts* - Some facts can be registered as key-value data for aggregation and analysis
* *Typed topics* - Topics can be one of many different types: people, places, organizations, time periods, etc. Facts
  can be organized in these topics for consistent presentation (like the side panels on Wikipedia). Combined with
  key-value data, these can also provide unique aggregations (data graphed over time, plotted on a map, etc.)
* *Batch tag operations* - A common problem I see in tagging systems is the inability to address human error.
  Mislabeling or inconsistent tagging leads to a need to merge tags together, or split them apart. Bulk editing means
  you don't have to do the same operation over and over for hundreds of tagged items
