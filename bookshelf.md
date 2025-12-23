---
title: "Bookshelf"
permalink: /bookshelf/
layout: default
---

<style>
.bookshelf-section { margin: 1.5rem 0 2.5rem 0; }
.bookshelf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
  align-items: start;
}
.book-card {
  display: block;
  text-decoration: none;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.12);
  background: rgba(255,255,255,0.6);
  transition: transform 120ms ease, box-shadow 120ms ease;
}
.book-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}
.book-cover {
  width: 100%;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  display: block;
  background: rgba(0,0,0,0.04);
}
.book-meta { padding: 10px 10px 12px 10px; }
.book-title { font-size: 0.95rem; line-height: 1.2; font-weight: 600; margin: 0 0 6px 0; color: inherit; }
.book-author { font-size: 0.85rem; opacity: 0.85; margin: 0 0 8px 0; }
.book-blurb { font-size: 0.82rem; opacity: 0.8; margin: 0; }
</style>

{% assign books = site.data.bookshelf %}
{% assign education = books | where: "category", "education" %}
{% assign nonfiction = books | where: "category", "nonfiction" %}

<div class="bookshelf-section">
  <h2>Education</h2>
  <div class="bookshelf-grid">
    {% for book in education %}
      <a class="book-card" href="{{ book.url | relative_url }}">
        <img class="book-cover"
             src="{{ '/assets/bookshelf/' | append: book.cover | relative_url }}"
             alt="Cover of {{ book.title }}"
             loading="lazy">
        <div class="book-meta">
          <p class="book-title">{{ book.title }}</p>
          <p class="book-author">{{ book.author }}</p>
          {% if book.blurb %}<p class="book-blurb">{{ book.blurb }}</p>{% endif %}
        </div>
      </a>
    {% endfor %}
  </div>
</div>

<div class="bookshelf-section">
  <h2>Nonfiction</h2>
  <div class="bookshelf-grid">
    {% for book in nonfiction %}
      <a class="book-card" href="{{ book.url | relative_url }}">
        <img class="book-cover"
             src="{{ '/assets/bookshelf/' | append: book.cover | relative_url }}"
             alt="Cover of {{ book.title }}"
             loading="lazy">
        <div class="book-meta">
          <p class="book-title">{{ book.title }}</p>
          <p class="book-author">{{ book.author }}</p>
          {% if book.blurb %}<p class="book-blurb">{{ book.blurb }}</p>{% endif %}
        </div>
      </a>
    {% endfor %}
  </div>
</div>
