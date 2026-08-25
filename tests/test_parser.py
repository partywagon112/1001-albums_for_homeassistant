import unittest

from custom_components.one_thousand_one_albums.parser import build_auth_headers, parse_album_page


HTML = '''
<html>
  <head>
    <meta property="og:title" content="Today: The Dark Side of the Moon - Pink Floyd" />
    <meta property="og:image" content="https://example.com/cover.jpg" />
    <meta name="description" content="Artist: Pink Floyd | Album: The Dark Side of the Moon" />
  </head>
  <body>
    <h1>Album of the Day</h1>
    <div class="album-card">
      <h2>The Dark Side of the Moon</h2>
      <p>Pink Floyd</p>
    </div>
  </body>
</html>
'''

JSON_PAYLOAD = {
    "name": "Hard Again",
    "artist": "Muddy Waters",
    "images": [
        {"url": "https://example.com/cover-small.jpg", "width": 64, "height": 64},
        {"url": "https://example.com/cover-large.jpg", "width": 640, "height": 640},
    ],
}


class ParseAlbumPageTests(unittest.TestCase):
    def test_parses_today_album_from_html(self):
        data = parse_album_page(HTML)

        self.assertEqual(data["today"]["title"], "The Dark Side of the Moon")
        self.assertEqual(data["today"]["artist"], "Pink Floyd")
        self.assertEqual(data["today"]["image"], "https://example.com/cover.jpg")

    def test_parses_current_album_from_project_json(self):
        data = parse_album_page(JSON_PAYLOAD)

        self.assertEqual(data["today"]["title"], "Hard Again")
        self.assertEqual(data["today"]["artist"], "Muddy Waters")
        self.assertEqual(data["today"]["image"], "https://example.com/cover-large.jpg")

    def test_no_auth_key_is_required(self):
        headers = build_auth_headers("abc123")

        self.assertEqual(headers, {})

if __name__ == "__main__":
    unittest.main()
