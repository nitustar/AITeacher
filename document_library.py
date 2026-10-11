"""Simple page-based search over PDF learning materials in the docs directory."""

import re
from pathlib import Path

from pypdf import PdfReader


class DocumentLibrary:
    def __init__(self, docs_dir=None):
        self.docs_dir = Path(docs_dir) if docs_dir else Path(__file__).parent / "docs"
        self._pages = None

    def _load_pages(self):
        if self._pages is not None:
            return self._pages

        pages = []
        if not self.docs_dir.exists():
            print(f"Learning materials folder not found: {self.docs_dir}")
            self._pages = pages
            return pages

        for path in sorted(self.docs_dir.glob("*.pdf")):
            try:
                reader = PdfReader(str(path))
                for page_number, page in enumerate(reader.pages, start=1):
                    text = page.extract_text() or ""
                    text = re.sub(r"\s+", " ", text).strip()
                    if text:
                        pages.append(
                            {
                                "source": path.name,
                                "page": page_number,
                                "text": text,
                            }
                        )
            except Exception as error:
                print(f"Could not read {path.name}: {error}")

        self._pages = pages
        if not pages:
            print("No searchable text found in docs/*.pdf. Scanned PDFs need OCR first.")
        return pages

    def sources(self):
        """Return PDF names and page counts for readable files."""
        result = []
        for path in sorted(self.docs_dir.glob("*.pdf")) if self.docs_dir.exists() else []:
            try:
                result.append((path.name, len(PdfReader(str(path)).pages)))
            except Exception:
                result.append((path.name, None))
        return result

    def search(self, query, limit=4):
        """Return excerpts from the pages most relevant to the query."""
        terms = {
            term
            for term in re.findall(r"[a-zA-Z]{3,}", query.casefold())
            if term not in {"the", "and", "for", "with", "about", "from", "that", "this", "please"}
        }
        if not terms:
            return []

        ranked = []
        for item in self._load_pages():
            page_text = item["text"].casefold()
            score = sum(page_text.count(term) for term in terms)
            if score:
                ranked.append((score, item))

        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in ranked[:limit]]

    @staticmethod
    def format_excerpts(excerpts):
        if not excerpts:
            return "No matching text was found in the supplied PDFs."
        return "\n\n".join(
            f"Source: {item['source']}, page {item['page']}\n{item['text'][:1800]}"
            for item in excerpts
        )
