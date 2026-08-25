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
    <div class="tomorrow">
      <h3>Tomorrow</h3>
      <h2>Led Zeppelin IV</h2>
      <p>Led Zeppelin</p>
    </div>
  </body>
</html>
'''


class ParseAlbumPageTests(unittest.TestCase):
    def test_parses_today_and_tomorrow(self):
        data = parse_album_page(HTML)

        self.assertEqual(data["today"]["title"], "The Dark Side of the Moon")
        self.assertEqual(data["today"]["artist"], "Pink Floyd")
        self.assertEqual(data["today"]["image"], "https://example.com/cover.jpg")
        self.assertEqual(data["tomorrow"]["title"], "Led Zeppelin IV")
        self.assertEqual(data["tomorrow"]["artist"], "Led Zeppelin")

    def test_no_auth_key_is_required(self):
        headers = build_auth_headers("abc123")

        self.assertEqual(headers, {})

if __name__ == "__main__":
    unittest.main()
