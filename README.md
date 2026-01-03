# pyao3

A mobile client for Archive of Our Own, inspired by the FanFiction.net mobile app. Built with `flet`, `ao3-api`, and `FanFicFare`. Pronounced as `pharaoh`. I am currently waiting for a stable release of Flet 1.0 before putting in more work.

## Roadmap

### Phase 1: 
Converting raw web data into text components.
- [x] Async integration with `FanFicFare` for background work fetching.
- [x] HTML-to-Markdown pipeline via `markdownify`
- [x] Optimized reader with `ft.Markdown`.
- [x] Custom `MarkdownStyleSheet` with Kindle-style blockquotes.
- [x] Drawer-based chapter selection.

### Phase 2:
Managing fics locally, inspired by the FFN "Download" feature.
- [ ] Local storage for work metadata, reading progress (offset), and "Last Read" timestamps.
- [ ] Grid/list view of downloaded works with cover thumbnails.
- [ ] Logic to check for local chapter data before hitting AO3 servers.
- [ ] A notification-style progress bar for fetching entire multi-chapter works in the background.
- [ ] Update fics lazily upon being launched.

### Phase 3:
Finding new content without leaving the app.
- [ ] Multi-filter search (Tags, Fandom, Characters, Rating, Warnings).
- [ ] Landing Page for fics showing full tags, summary, and "Download/Read" buttons.
- [ ] Quick access to "Trending," "Most Recent," and "Bookmarked."

### Phase 4: User Profile & Social
Account-level integration.
- [ ] Session cookie management to access restricted/adult content.
- [ ] Fetching and displaying personal "Bookmarks" and "Marked for Later."
- [ ] Buttons for "Kudos" and "Post Comment" (via `ao3-api`).

### Phase 5:
Advanced UI/UX features for a native feel.
- [ ] On-the-fly adjustment of font size, line height, and background tint (Sepia/Grey/Black), provide custom in-built themes for this.
- [ ] Refined scroll animations and "Tap to Next Chapter" logic.
- [ ] Full optimization for the stable Flet release, including native mobile performance tweaks.

---

## Architecture

1. `ao3-api` handles searching, metadata fetching, and user account interactions.
2. `FanFicFare` handles the "Deep Scraping" of chapter content and formatting for offline use.
3. A responsive Flutter-based front-end `flet` allows usage of the previous dependencies in the same native ecosystem.
