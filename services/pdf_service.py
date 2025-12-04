import os
import json
from playwright.sync_api import sync_playwright


# --------------------------------------------------------
# THEME
# --------------------------------------------------------

def find_theme_json_and_root(theme_extract_dir):
    for root, dirs, files in os.walk(theme_extract_dir):
        for f in files:
            if f.endswith(".json"):
                return os.path.join(root, f), root
    raise FileNotFoundError("Theme JSON not found inside theme directory")


def load_theme(theme_extract_dir):
    theme_path, theme_root = find_theme_json_and_root(theme_extract_dir)

    try:
        with open(theme_path, "r", encoding="utf-8") as f:
            return json.load(f), theme_root
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid theme JSON: {theme_path}") from e


# --------------------------------------------------------
# BACKGROUND
# --------------------------------------------------------

def build_background_css(theme, theme_dir):
    bg_type = theme.get("background_type", "solid")

    if bg_type == "solid":
        return f"background: {theme.get('background_color', '#000')};"

    if bg_type == "gradient":
        start = theme.get("background_start_color")
        end = theme.get("background_end_color")
        direction = theme.get("background_direction", "vertical")

        if not start or not end:
            raise ValueError("Gradient theme missing start or end color")

        css_dir = "to bottom" if direction == "vertical" else "to right"
        return f"background: linear-gradient({css_dir}, {start}, {end});"

    if bg_type == "image":
        bg = theme.get("background_filename")
        filename = None

        if isinstance(bg, dict) and "parts" in bg:
            filename = bg["parts"][-1]
        elif isinstance(bg, str):
            filename = bg

        if not filename:
            raise ValueError("Theme background_filename is invalid")

        image_path = os.path.join(theme_dir, filename)

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Background image not found: {image_path}")

        image_path = os.path.abspath(image_path).replace("\\", "/")

        return f"""
            background-image: url("file://{image_path}");
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
            background-color: black;
        """

    if bg_type == "transparent":
        return "background: transparent;"

    raise ValueError(f"Unknown background_type: {bg_type}")


# --------------------------------------------------------
# STYLE
# --------------------------------------------------------

def build_page_style(theme, theme_dir):
    required = [
        "font_main_width", "font_main_height",
        "font_main_name", "font_main_size",
        "font_main_color"
    ]

    for key in required:
        if key not in theme:
            raise KeyError(f"Theme missing required key: {key}")

    width = int(theme["font_main_width"])
    height = int(theme["font_main_height"])
    font = theme["font_main_name"]
    size = int(theme["font_main_size"])
    color = theme["font_main_color"]

    if width <= 0 or height <= 0:
        raise ValueError("Invalid page dimensions from theme")

    bg_css = build_background_css(theme, theme_dir)

    h_align = theme.get("display_horizontal_align", 2)
    v_align = theme.get("display_vertical_align", 1)

    align_map = {0: "left", 1: "right", 2: "center", 3: "justify"}
    v_map = {0: "flex-start", 1: "center", 2: "flex-end"}

    return width, height, f"""
    <style>
        @page {{
            size: {width}px {height}px;
            margin: 0;
        }}

        body {{
            margin: 0;
            font-family: "{font}", sans-serif;
        }}

        .page {{
            width: {width}px;
            height: {height}px;
            display: flex;
            justify-content: {align_map.get(h_align, "center")};
            align-items: {v_map.get(v_align, "center")};
            page-break-after: always;
            box-sizing: border-box;
            padding: 60px;
            {bg_css}
        }}

        .content {{
            color: {color};
            font-size: {size}px;
            text-align: {align_map.get(h_align, "center")};
            white-space: pre-line;
            line-height: 1.4;
            width: 100%;
        }}

        .page:last-child {{
            page-break-after: auto;
        }}
    </style>
    """


# --------------------------------------------------------
# PAGINATION
# --------------------------------------------------------

def estimate_lines_per_page(theme):
    try:
        height = float(theme["font_main_height"])
        font_size = float(theme["font_main_size"])
    except Exception:
        raise ValueError("Invalid font_main_height or font_main_size")

    line_height = font_size * 1.4
    padding = 120

    usable_height = height - padding
    max_lines = int(usable_height / line_height) - 1

    if max_lines < 1:
        raise ValueError("Theme margins too large for slide height")

    return max(max_lines, 3)


def split_slide_to_pages(slide_text, theme):
    if not isinstance(slide_text, str):
        raise TypeError("Slide is not a string")

    max_lines = estimate_lines_per_page(theme)
    lines = slide_text.splitlines()

    if not lines:
        raise ValueError("Slide contains no lines")

    pages = []
    for i in range(0, len(lines), max_lines):
        chunk = lines[i:i + max_lines]
        pages.append("<br>".join(chunk))

    return pages


# --------------------------------------------------------
# HTML COMPOSITION
# --------------------------------------------------------

def build_pages(slides, theme):
    if not slides:
        raise ValueError("No slides to render")

    pages = []

    for slide in slides:
        slide_pages = split_slide_to_pages(slide, theme)
        for block in slide_pages:
            pages.append(
                f"""
                <div class="page">
                    <div class="content">{block}</div>
                </div>
                """
            )

    if not pages:
        raise RuntimeError("No pages generated from slides")

    return pages


def compose_document(pages, style):
    if not pages:
        raise ValueError("HTML composition failed: no pages")

    return f"""
    <html>
        <head>
            <meta charset="UTF-8">
            {style}
        </head>
        <body>
            {"".join(pages)}
        </body>
    </html>
    """


# --------------------------------------------------------
# PDF GENERATION
# --------------------------------------------------------

def convert_slides_to_pdf(slides, theme_extract_dir, job_dir):

    if not os.path.exists(job_dir):
        raise FileNotFoundError(f"Job directory missing: {job_dir}")

    theme, theme_root = load_theme(theme_extract_dir)

    width, height, style = build_page_style(theme, theme_root)
    pages = build_pages(slides, theme)
    html = compose_document(pages, style)

    os.makedirs(job_dir, exist_ok=True)

    html_path = os.path.join(job_dir, "slides.html")
    pdf_path = os.path.join(job_dir, "slides.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": height})

            page.goto("file://" + html_path, wait_until="load")

            page.pdf(
                path=pdf_path,
                width=f"{width}px",
                height=f"{height}px",
                print_background=True
            )

            browser.close()

    except Exception as e:
        raise RuntimeError("Playwright failed to generate PDF") from e

    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF was not generated")

    return pdf_path
