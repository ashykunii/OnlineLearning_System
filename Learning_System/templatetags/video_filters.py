import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def youtube_embed(url):
    """
    Converts any YouTube URL variant to an embed-ready URL string.
    Supports:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
      - https://youtube.com/shorts/VIDEO_ID
      - https://www.youtube.com/embed/VIDEO_ID  (already embed)
    Returns the embed URL, or the original URL if not a recognised YouTube link.
    """
    if not url:
        return url

    # Already an embed URL
    if 'youtube.com/embed/' in url:
        return url

    # youtu.be/VIDEO_ID
    m = re.match(r'https?://youtu\.be/([A-Za-z0-9_\-]+)', url)
    if m:
        return f'https://www.youtube.com/embed/{m.group(1)}'

    # youtube.com/watch?v=VIDEO_ID
    m = re.search(r'[?&]v=([A-Za-z0-9_\-]+)', url)
    if m:
        return f'https://www.youtube.com/embed/{m.group(1)}'

    # youtube.com/shorts/VIDEO_ID
    m = re.match(r'https?://(?:www\.)?youtube\.com/shorts/([A-Za-z0-9_\-]+)', url)
    if m:
        return f'https://www.youtube.com/embed/{m.group(1)}'

    return url


@register.filter
def is_youtube(url):
    """Returns True if URL is a YouTube link."""
    if not url:
        return False
    return 'youtube.com' in url or 'youtu.be' in url


@register.filter
def is_direct_video(url):
    """Returns True if URL points to a playable video file."""
    if not url:
        return False
    return any(url.lower().endswith(ext) for ext in ['.mp4', '.webm', '.ogg', '.mov'])


@register.filter
def is_pdf(url):
    """Returns True if the URL points to a PDF file."""
    if not url:
        return False
    return url.lower().endswith('.pdf')


@register.filter
def file_extension(url):
    """Returns the file extension (lowercase, without dot) from a URL."""
    if not url:
        return ''
    path = url.split('?')[0]  # strip query params
    if '.' in path:
        return path.rsplit('.', 1)[-1].lower()
    return ''
